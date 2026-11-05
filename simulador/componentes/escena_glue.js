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
// Mismo corte que usa la ventana de la escena para dibujar el sol y la luna.
const DIA_INICIO = (window.SimEscena && window.SimEscena.DIA_INICIO) ?? 6;
const DIA_FIN = (window.SimEscena && window.SimEscena.DIA_FIN) ?? 19;
const esDia = (h) => h >= DIA_INICIO && h < DIA_FIN;

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
        <div class="mapa" role="group" aria-label="Mapa de consumo por hora. Tocá una hora para saltar."></div>
        <input type="range" min="0" max="23.99" step="0.05" aria-label="Hora del día">
        <div class="metricas">
          <div class="met dia" title="Consumo estimado del día (06:00 a 19:00) en este ambiente">
            <span class="met-t">☀ Día <small>6–19 h</small></span>
            <b class="met-v">—</b>
            <span class="met-s"></span>
          </div>
          <div class="met noche" title="Consumo estimado de la noche (19:00 a 06:00) en este ambiente">
            <span class="met-t">🌙 Noche <small>19–6 h</small></span>
            <b class="met-v">—</b>
            <span class="met-s"></span>
          </div>
        </div>
        <div class="picos" aria-live="polite"></div>
      </div>
      <div class="tip" role="tooltip"></div>
    </div>
    <p class="ayuda">Arrastrá muebles y artefactos · tocá uno para editarlo · <b>R</b> rota · flechas mueven · ▶ simula el día y la noche · tocá el mapa para ir a una hora.</p>`;
  st.el = {
    titulo: raiz.querySelector('.titulo'), lienzo: raiz.querySelector('.lienzo'), play: raiz.querySelector('.play'),
    hora: raiz.querySelector('.hora'), w: raiz.querySelector('.w'), rango: raiz.querySelector('input'),
    reloj: raiz.querySelector('.reloj'), mapa: raiz.querySelector('.mapa'), tip: raiz.querySelector('.tip'),
    metDia: raiz.querySelector('.met.dia'), metNoche: raiz.querySelector('.met.noche'), picos: raiz.querySelector('.picos'),
  };
  st.el.mapa.innerHTML = Array.from({ length: 24 }, (_, h) =>
    `<button type="button" class="celda" data-h="${h}" aria-label="Hora ${hhmm(h)}"></button>`).join('');
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
  // El mapa se puede tocar en cualquier punto: se elige la hora que cae debajo del dedo o del mouse.
  const horaDePuntero = (e) => {
    const r = st.el.mapa.getBoundingClientRect();
    const t = Math.max(0, Math.min(0.9999, (e.clientX - r.left) / (r.width || 1)));
    return Math.min(23, Math.floor(t * 24));
  };
  st.el.mapa.addEventListener('click', (e) => {
    const celda = e.target.closest('.celda');
    // Con Enter o barra espaciadora no hay coordenadas: se usa la celda enfocada.
    st.hora = e.detail === 0 && celda ? +celda.dataset.h : horaDePuntero(e);
    st.play = false;
    ocultarTip(st);
    pintar(st);
  });
  st.el.mapa.addEventListener('pointermove', (e) => {
    if (e.pointerType === 'touch') return;
    mostrarTip(st, horaDePuntero(e));
  });
  st.el.mapa.addEventListener('pointerleave', () => ocultarTip(st));
  st.el.mapa.addEventListener('focusin', (e) => {
    const c = e.target.closest('.celda');
    if (c) mostrarTip(st, +c.dataset.h);
  });
  st.el.mapa.addEventListener('focusout', () => ocultarTip(st));
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

// Del verde (consumo bajo) al rojo (consumo alto) para el mapa de las 24 horas.
function colorCalor(t) {
  const x = Math.max(0, Math.min(1, t));
  return `hsl(${Math.round(145 - 145 * x)}, 72%, 46%)`;
}

// Calcula una sola vez por cambio de datos: totales horarios, picos y reparto día/noche.
function prepararMapa(st) {
  const arts = st.objs.filter((o) => o.tipo === 'art');
  const base = +st.data.base_kw || 0;
  const totales = Array.from({ length: 24 }, (_, h) =>
    base + arts.reduce((s, o) => s + ((o.perfil && o.perfil[h]) || 0), 0));
  const max = Math.max(...totales, 0);
  const min = Math.min(...totales, max);
  const spread = max - min;
  const tops = totales.map((_, h) => {
    let top = base > 0 ? { nombre: 'Base de la casa', w: base, icono: '🏠' } : null;
    for (const o of arts) {
      const w = (o.perfil && o.perfil[h]) || 0;
      if (!top || w > top.w) top = { nombre: o.label, w, icono: o.icono || '🔌' };
    }
    return top && top.w > 0.0001 ? top : null;
  });
  const orden = totales.map((v, h) => ({ v, h })).filter((p) => p.v > 0.0001)
    .sort((a, b) => b.v - a.v || a.h - b.h);
  // Un "foco" es una hora que sobresale del resto; si todo consume parejo no hay picos.
  const picos = spread > Math.max(0.001, max * 0.01) ? orden.slice(0, 3) : [];
  const rank = new Map(picos.map((p, i) => [p.h, i + 1]));
  const diaKwh = totales.reduce((s, v, h) => s + (esDia(h) ? v : 0), 0);
  const nocheKwh = totales.reduce((s, v, h) => s + (esDia(h) ? 0 : v), 0);
  const totalKwh = diaKwh + nocheKwh || 1;
  st.analisis = { totales, tops, picos, rank, diaKwh, nocheKwh, totalKwh };

  st.el.mapa.querySelectorAll('.celda').forEach((c, h) => {
    const v = totales[h];
    const t = spread > 0.0001 ? (v - min) / spread : 0.15;
    const pico = rank.get(h);
    const top = tops[h];
    c.style.background = v > 0.0001 ? colorCalor(t) : 'transparent';
    c.classList.toggle('pico', !!pico);
    if (pico) c.dataset.pico = String(pico); else delete c.dataset.pico;
    c.setAttribute('aria-label', `${hhmm(h)}–${hhmm(h + 1)}. ${fmt(v * 1000)} W` +
      (pico ? `. Pico número ${pico}` : '') +
      (top ? `. Consume más: ${top.nombre}, ${fmt(top.w * 1000)} W` : ''));
  });

  actualizarMetricas(st);
  pintarPicos(st);
}

function actualizarMetricas(st) {
  const a = st.analisis;
  if (!a) return;
  const tarifa = +st.data.tarifa || 0;
  const pintar = (el, kwh, pct, nombre, desde, hasta) => {
    const costo = tarifa > 0 ? ` · $ ${fmt(kwh * tarifa)}` : '';
    el.querySelector('.met-v').textContent = `${fmt(kwh, kwh < 100 ? 1 : 0)} kWh`;
    el.querySelector('.met-s').textContent = `${fmt(pct, 0)}%${costo}`;
    el.title = `${nombre} (${hhmm(desde)}–${hhmm(hasta)}): ${fmt(kwh, 1)} kWh${costo} · ` +
      `${fmt(pct, 0)}% del consumo diario de este ambiente`;
  };
  pintar(st.el.metDia, a.diaKwh, a.diaKwh / a.totalKwh * 100, 'Día', DIA_INICIO, DIA_FIN);
  pintar(st.el.metNoche, a.nocheKwh, a.nocheKwh / a.totalKwh * 100, 'Noche', DIA_FIN, 24 + DIA_INICIO);
}

function pintarPicos(st) {
  const picos = st.analisis ? st.analisis.picos : [];
  st.el.picos.textContent = picos.length
    ? `🔥 Picos: ${picos.map((p) => String(p.h).padStart(2, '0')).join(' · ')} h`
    : '🔥 Sin picos de consumo';
  st.el.picos.title = picos.length
    ? picos.map((p, i) => `#${i + 1} ${hhmm(p.h)}–${hhmm(p.h + 1)}: ${fmt(p.v * 1000)} W`).join('\n')
    : 'El consumo no cambia lo suficiente entre horas como para marcar un pico.';
}

function mostrarTip(st, h) {
  const a = st.analisis;
  if (!a || st.tipHora === h) return;
  st.tipHora = h;
  const top = a.tops[h];
  const pico = a.rank.get(h);
  const total = a.totales[h] || 0;
  st.el.tip.innerHTML = `<b>${hhmm(h)}–${hhmm(h + 1)}</b>` +
    `<span>${fmt(total * 1000)} W${pico ? ` · 🔥 pico #${pico}` : ''}</span>` +
    `<small>${top ? `${top.icono} ${top.nombre} · ${fmt(top.w * 1000)} W` : 'Sin consumo'}</small>`;
  const mr = st.el.mapa.getBoundingClientRect();
  const rr = st.el.reloj.getBoundingClientRect();
  st.el.tip.style.left = `${mr.left - rr.left + mr.width / 2}px`;
  st.el.tip.style.top = `${mr.top - rr.top - 8}px`;
  st.el.tip.classList.add('on');
}

function ocultarTip(st) {
  st.tipHora = null;
  st.el.tip.classList.remove('on');
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
  const total = (+st.data.base_kw || 0) + st.objs.reduce((s, o) => s + (o.tipo === 'art' ? o.perfil[h] || 0 : 0), 0);
  st.el.titulo.innerHTML = `${st.data.ambiente.icono} ${st.data.ambiente.nombre}<small>${st.data.resumen || ''}</small>`;
  st.raiz.querySelector('.ambientes').innerHTML = (st.data.ambientes || []).map((a) =>
    `<button type="button" data-amb="${a.id}" class="${a.id === st.data.ambiente.id ? 'on' : ''}">${a.icono} ${a.nombre}</button>`).join('');
  st.el.hora.textContent = hhmm(st.hora);
  st.el.w.textContent = `${fmt(total * 1000)} W en este ambiente`;
  st.el.w.title = 'Suma los artefactos del ambiente visible más la base de la casa';
  st.el.play.textContent = st.play ? '⏸' : '▶';
  if (document.activeElement !== st.el.rango) st.el.rango.value = st.hora;
  st.raiz.querySelectorAll('[data-vista]').forEach((b) => b.classList.toggle('on', b.dataset.vista === st.vista));
  // La hora actual se marca en el mapa y en la tarjeta de día o de noche.
  if (st.horaPintada !== h) {
    st.horaPintada = h;
    st.el.mapa.querySelectorAll('.celda').forEach((c) => c.classList.toggle('ahora', +c.dataset.h === h));
    st.el.metDia.classList.toggle('on', esDia(h));
    st.el.metNoche.classList.toggle('on', !esDia(h));
  }
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
  st.accClave = null;   // datos nuevos: el panel izquierdo se vuelve a dibujar
  st.horaPintada = null;  // fuerza a remarcar la hora actual en el mapa
  prepararMapa(st);
  pintar(st);
}
