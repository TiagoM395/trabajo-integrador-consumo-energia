// Conexión entre la escena isométrica (escena.js) y Streamlit (componentes v2).
// Python -> JS: data = { ambiente, objetos, seleccion, base_kw, hora }
// JS -> Python: triggers "mover" {key, x, y}, "seleccion" {key}, "rotar" {key}
const INSTANCIAS = new WeakMap();

const fmt = (v, d = 0) => Number(v).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d });
const hhmm = (h) => {
  const t = Math.round((((h % 24) + 24) % 24) * 60);
  return `${String(Math.floor(t / 60) % 24).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`;
};

function construir(raiz, st) {
  raiz.innerHTML = `
    <div class="barra">
      <span class="titulo"></span>
      <div class="seg" role="group" aria-label="Qué muestran los globos">
        <button type="button" data-vista="kwh">kWh/mes</button>
        <button type="button" data-vista="w">Watts ahora</button>
        <button type="button" data-vista="costo">$ / mes</button>
      </div>
    </div>
    <div class="lienzo" tabindex="0" aria-label="Ambiente interactivo: arrastrá los objetos. R rota, flechas mueven."></div>
    <div class="reloj">
      <button type="button" class="play" aria-label="Reproducir el día">▶</button>
      <div class="c">
        <div class="l"><span class="hora"></span><span class="w"></span></div>
        <input type="range" min="0" max="23.99" step="0.05" aria-label="Hora del día">
      </div>
    </div>
    <p class="ayuda">Arrastrá muebles y artefactos · tocá uno para editarlo · <b>R</b> rota · flechas mueven · ▶ simula el día y la noche.</p>`;
  st.el = {
    titulo: raiz.querySelector('.titulo'), lienzo: raiz.querySelector('.lienzo'), play: raiz.querySelector('.play'),
    hora: raiz.querySelector('.hora'), w: raiz.querySelector('.w'), rango: raiz.querySelector('input'),
  };
  raiz.querySelectorAll('[data-vista]').forEach((b) => b.addEventListener('click', () => { st.vista = b.dataset.vista; pintar(st); }));
  st.el.rango.addEventListener('input', () => { st.hora = +st.el.rango.value; pintar(st); });
  st.el.play.addEventListener('click', () => {
    st.play = !st.play;
    if (st.play && st.vista === 'kwh') st.vista = 'w';
    st.ultimo = 0;
    pintar(st);
    if (st.play) requestAnimationFrame((t) => bucle(st, t));
  });
  st.el.lienzo.addEventListener('keydown', (e) => {
    if (!st.sel) return;
    const o = st.objs.find((x) => x.key === st.sel);
    if (!o) return;
    const mov = { ArrowLeft: [-0.5, 0], ArrowRight: [0.5, 0], ArrowUp: [0, -0.5], ArrowDown: [0, 0.5] }[e.key];
    if (mov) {
      e.preventDefault();
      st.setTrigger('mover', { key: o.key, x: o.x + mov[0], y: o.y + mov[1] });
    } else if (e.key === 'r' || e.key === 'R') {
      e.preventDefault();
      st.setTrigger('rotar', { key: o.key });
    }
  });
}

function bucle(st, t) {
  if (!st.play || !st.raiz.isConnected) return;
  if (st.ultimo) st.hora = (st.hora + ((t - st.ultimo) / 1000) * 1.6) % 24;
  st.ultimo = t;
  pintar(st);
  requestAnimationFrame((t2) => bucle(st, t2));
}

function objetosVista(st) {
  const h = Math.min(23, Math.floor(st.hora));
  return st.objs.map((o) => {
    if (o.tipo !== 'art') return o;
    const kw = o.perfil[h] || 0;
    const sub = st.vista === 'w' ? `${o.icono} ${fmt(kw * 1000)} W`
      : st.vista === 'costo' ? `${o.icono} $ ${fmt(o.costo)}` : `${o.icono} ${fmt(o.kwh, o.kwh < 10 ? 1 : 0)} kWh`;
    return { ...o, sub, potencia: kw > 0.001 ? kw : 0, intensidad: Math.min(1, kw / 1.5) };
  });
}

function pintar(st) {
  const h = Math.min(23, Math.floor(st.hora));
  const total = st.data.base_kw + st.objs.reduce((s, o) => s + (o.tipo === 'art' ? o.perfil[h] || 0 : 0), 0);
  st.el.titulo.innerHTML = `${st.data.ambiente.icono} ${st.data.ambiente.nombre}<small>${st.data.resumen || ''}</small>`;
  st.el.hora.textContent = hhmm(st.hora);
  st.el.w.textContent = `${fmt(total * 1000)} W en la casa`;
  st.el.play.textContent = st.play ? '⏸' : '▶';
  if (document.activeElement !== st.el.rango) st.el.rango.value = st.hora;
  st.raiz.querySelectorAll('[data-vista]').forEach((b) => b.classList.toggle('on', b.dataset.vista === st.vista));
  st.ctl.actualizar({ ambiente: st.data.ambiente, objetos: objetosVista(st), seleccion: st.sel, hora: st.hora });
}

export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  const raiz = parentElement.querySelector('.sim-escena');
  if (!raiz || !data) return;
  let st = INSTANCIAS.get(parentElement);
  if (!st) {
    st = { raiz, hora: data.hora ?? 12, vista: 'kwh', play: false, objs: [], data };
    construir(raiz, st);
    st.ctl = window.SimEscena.crear(st.el.lienzo, {
      ambiente: data.ambiente, objetos: [], seleccion: null, hora: st.hora,
      onSelect: (k) => { st.sel = k; st.ctl.actualizar({ seleccion: k }); if (k === null) st.setTrigger('seleccion', { key: null }); },
      onMove: (k, x, y) => {
        const o = st.objs.find((ob) => ob.key === k);
        if (o) { o.x = x; o.y = y; pintar(st); }
      },
      onFin: (k) => {
        const o = st.objs.find((ob) => ob.key === k);
        if (o) st.setTrigger('mover', { key: k, x: o.x, y: o.y });
      },
      onClic: (k) => st.setTrigger('seleccion', { key: k }),
    });
    INSTANCIAS.set(parentElement, st);
  }
  st.setTrigger = (nombre, valor) => setTriggerValue(nombre, { ...valor, t: Date.now() });
  st.data = data;
  st.objs = data.objetos.map((o) => ({ ...o }));
  st.sel = data.seleccion;
  pintar(st);
}
