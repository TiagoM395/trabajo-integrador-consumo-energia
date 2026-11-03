// Conexión entre la escena isométrica (escena.js) y Streamlit (componentes v2).
// Python -> JS: data = { ambiente, objetos, seleccion, base_kw, hora }
// JS -> Python: triggers "mover" {key, x, y}, "seleccion" {key}, "rotar" {key}
const INSTANCIAS = new WeakMap();

// Ambiente 3D en tres partes (navbar y resumen · simulador · artefactos y muebles):
// cada movimiento de la rueda pasa a la parte siguiente o a la anterior, sin quedar a mitad de camino.
if (!window.__ambientePorPartes) {
  window.__ambientePorPartes = true;
  // Después de cada salto se espera a que termine el gesto (rueda o touchpad: un deslizamiento del
  // touchpad manda muchos movimientos seguidos) antes de aceptar el siguiente.
  let ocupado = false, finSalto = 0, tPausa = null, acumulado = 0, tAcum = null;
  // Un salto solo puede empezar con un gesto nuevo: si el gesto venía scrolleando un texto largo
  // y llegó al final, se frena ahí (hay que soltar y volver a deslizar para pasar a la parte siguiente).
  let ultimo = 0, puedeSaltar = true;
  const soltarCuandoPare = () => {
    clearTimeout(tPausa);
    tPausa = setTimeout(() => { if (performance.now() >= finSalto) ocupado = false; else soltarCuandoPare(); }, 250);
  };
  const bloquear = () => { ocupado = true; finSalto = performance.now() + 600; soltarCuandoPare(); };
  document.addEventListener('wheel', (e) => {
    const main = document.querySelector('[data-testid="stMain"]');
    const s2 = document.querySelector('.st-key-amb-pantalla');
    const s3 = document.querySelector('.st-key-amb-abajo');
    if (!main || !s2 || !s3 || !main.contains(e.target) || e.deltaY === 0) return;
    if (window.innerWidth <= 640) return;  // en el celular, scroll normal
    const ahora = performance.now();
    if (ahora - ultimo > 200) puedeSaltar = true;  // pausa: empieza un gesto nuevo
    ultimo = ahora;
    // Mientras dura un salto, la rueda no hace nada (si no, se pasaría de largo).
    if (ocupado) { e.preventDefault(); soltarCuandoPare(); return; }
    const arriba = main.scrollTop, alto = main.clientHeight;
    const base = main.getBoundingClientRect().top - arriba;
    const partes = [0, s2.getBoundingClientRect().top - base, s3.getBoundingClientRect().top - base];
    let i = 0;
    partes.forEach((p, k) => { if (arriba >= p - 8) i = k; });
    const baja = e.deltaY > 0;
    // Primera parte más larga que la pantalla (por ejemplo, con «¿De dónde salen estos números?»
    // abierto): adentro se scrollea normal y recién al llegar al final se pasa al simulador.
    const paso = Math.abs(e.deltaY);
    const ir = (y) => { e.preventDefault(); bloquear(); main.scrollTo({ top: y, behavior: 'smooth' }); };
    if (i === 0 && baja && arriba + alto < partes[1] - 8) {
      // Al llegar al final de la primera parte se frena en el borde; el próximo gesto salta.
      puedeSaltar = false;
      if (arriba + alto + paso > partes[1]) ir(partes[1] - alto);
      return;
    }
    if (i === 0 && !baja && arriba > 8) { puedeSaltar = false; return; }
    // Tercera parte: si es más larga que la pantalla, el scroll sigue normal.
    if (i === 2 && baja) { puedeSaltar = false; return; }
    if (i === 2 && arriba > partes[2] + 8) {
      // Al volver al comienzo de la tercera parte se frena ahí; el próximo gesto sube al simulador.
      puedeSaltar = false;
      if (arriba - paso < partes[2]) ir(partes[2]);
      return;
    }
    e.preventDefault();
    if (!puedeSaltar) return;
    // Los movimientos chicos (touchpad) se suman: se salta recién cuando el gesto es claro.
    acumulado += e.deltaY;
    clearTimeout(tAcum);
    tAcum = setTimeout(() => { acumulado = 0; }, 250);
    if (Math.abs(acumulado) < 30) return;
    acumulado = 0;
    let destino = partes[Math.max(0, Math.min(2, i + (baja ? 1 : -1)))];
    // Al subir desde el simulador, se muestra el final de la primera parte.
    if (i === 1 && !baja) destino = Math.max(0, partes[1] - alto);
    if (Math.abs(destino - arriba) < 2) return;
    puedeSaltar = false;
    bloquear();
    main.scrollTo({ top: destino, behavior: 'smooth' });
  }, { passive: false });
}

const fmt = (v, d = 0) => Number(v).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d });
const hhmm = (h) => {
  const t = Math.round((((h % 24) + 24) % 24) * 60);
  return `${String(Math.floor(t / 60) % 24).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`;
};

function construir(raiz, st) {
  raiz.innerHTML = `
    <div class="barra">
      <div class="seg ambientes" role="group" aria-label="Ambiente"></div>
      <span class="titulo"></span>
      <div class="seg vistas" role="group" aria-label="Qué muestran los globos">
        <button type="button" data-vista="kwh">kWh/mes</button>
        <button type="button" data-vista="w">Watts ahora</button>
        <button type="button" data-vista="costo">$ / mes</button>
      </div>
    </div>
    <div class="accion" aria-live="polite"></div>
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
  // Panel izquierdo: rotar o eliminar el objeto seleccionado.
  raiz.querySelector('.accion').addEventListener('click', (e) => {
    const b = e.target.closest('[data-accion]');
    if (b && st.sel) st.setTrigger(b.dataset.accion, { key: st.sel });
  });
  raiz.querySelector('.ambientes').addEventListener('click', (e) => {
    const b = e.target.closest('[data-amb]');
    if (b && b.dataset.amb !== st.data.ambiente.id) st.setTrigger('ambiente', { id: b.dataset.amb });
  });
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

// Se redibuja solo cuando cambia la selección (no en cada cuadro de la animación del día),
// así los botones no se reemplazan mientras se hace clic.
function pintarAccion(st) {
  const o = st.objs.find((x) => x.key === st.sel);
  const clave = o ? `${o.key}|${o.kwh ?? ''}` : '';
  if (clave === st.accClave) return;
  st.accClave = clave;
  const panel = st.raiz.querySelector('.accion');
  if (!o) {
    panel.innerHTML = '<div class="acc-vacio"><span>👆</span>Tocá un objeto de la escena para rotarlo o eliminarlo</div>';
    return;
  }
  const icono = o.icono || (o.def && o.def.icono) || '📦';
  const dato = o.tipo === 'art' ? `${fmt(o.kwh, o.kwh < 10 ? 1 : 0)} kWh/mes` : 'Mueble';
  panel.innerHTML = `
    <div class="acc-ico">${icono}</div>
    <div class="acc-nom">${o.label}</div>
    <div class="acc-dato">${dato}</div>
    <button type="button" class="acc-btn" data-accion="rotar">⟳<span>Rotar</span></button>
    <button type="button" class="acc-btn quitar" data-accion="quitar">🗑<span>Eliminar</span></button>`;
}

function pintar(st) {
  const h = Math.min(23, Math.floor(st.hora));
  const total = st.data.base_kw + st.objs.reduce((s, o) => s + (o.tipo === 'art' ? o.perfil[h] || 0 : 0), 0);
  st.el.titulo.innerHTML = `${st.data.ambiente.icono} ${st.data.ambiente.nombre}<small>${st.data.resumen || ''}</small>`;
  st.raiz.querySelector('.ambientes').innerHTML = (st.data.ambientes || []).map((a) =>
    `<button type="button" data-amb="${a.id}" class="${a.id === st.data.ambiente.id ? 'on' : ''}">${a.icono} ${a.nombre}</button>`).join('');
  st.el.hora.textContent = hhmm(st.hora);
  st.el.w.textContent = `${fmt(total * 1000)} W en la casa`;
  st.el.play.textContent = st.play ? '⏸' : '▶';
  if (document.activeElement !== st.el.rango) st.el.rango.value = st.hora;
  st.raiz.querySelectorAll('[data-vista]').forEach((b) => b.classList.toggle('on', b.dataset.vista === st.vista));
  st.ctl.actualizar({ ambiente: st.data.ambiente, objetos: objetosVista(st), seleccion: st.sel, hora: st.hora });
  pintarAccion(st);
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
      onSelect: (k) => {
        st.sel = k; st.ctl.actualizar({ seleccion: k }); pintarAccion(st);
        if (k === null) st.setTrigger('seleccion', { key: null });
      },
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
  st.accClave = null;  // datos nuevos: el panel izquierdo se vuelve a dibujar
  pintar(st);
}
