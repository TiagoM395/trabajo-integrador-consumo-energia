/* Ambiente isométrico en SVG: muebles y artefactos arrastrables.
   Unidad: 1 baldosa = 0,5 m. Ambiente de 12 x 10 baldosas (6 x 5 m). */
(function (root) {
  const TW = 56, TH = 28, ZH = 24;
  const ANCHO = 12, FONDO = 10, ALTO = 5.6;
  const OX = FONDO * TW / 2 + 24;
  const OY = ALTO * ZH + 84;
  const VW = (ANCHO + FONDO) * TW / 2 + 48;
  const VH = OY + (ANCHO + FONDO) * TH / 2 + 24;

  const iso = (x, y, z = 0) => [OX + (x - y) * TW / 2, OY + (x + y) * TH / 2 - z * ZH];
  const pts = (arr) => arr.map((p) => p.map((n) => n.toFixed(1)).join(',')).join(' ');

  function tono(hex, k) {
    const n = parseInt(hex.slice(1), 16);
    let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
    if (k >= 0) { r += (255 - r) * k; g += (255 - g) * k; b += (255 - b) * k; }
    else { r *= 1 + k; g *= 1 + k; b *= 1 + k; }
    return `rgb(${r | 0},${g | 0},${b | 0})`;
  }

  // Rotación de 90° de una parte dentro de la huella (FW x FD)
  function rotar(partes, FW, FD, rot) {
    let ps = partes.map((p) => ({ ...p }));
    let fw = FW, fd = FD, front = [0, 1];
    for (let i = 0; i < ((rot % 4) + 4) % 4; i++) {
      ps = ps.map((p) => ({ ...p, x: fd - p.y - p.d, y: p.x, w: p.d, d: p.w }));
      [fw, fd] = [fd, fw];
      front = [-front[1], front[0]];
    }
    return { partes: ps, fw, fd, front };
  }

  function formaDe(def) {
    const s = def.iso || def;
    if (s.partes) return { partes: s.partes, W: s.w, D: s.d, luz: s.luz };
    return { partes: [{ x: 0, y: 0, z: 0, w: s.w, d: s.d, h: s.h, color: s.color, detalle: s.detalle }], W: s.w, D: s.d };
  }

  function huella(def, rot) {
    const f = formaDe(def);
    return rot % 2 ? { w: f.D, d: f.W } : { w: f.W, d: f.D };
  }

  // Punto paramétrico (u, v) sobre la cara frontal visible de una caja
  function caraPunto(b, front, u, v) {
    if (front[1] === 1) return iso(b.x + u * b.w, b.y + b.d, b.z + v * b.h);
    return iso(b.x + b.w, b.y + (1 - u) * b.d, b.z + v * b.h);
  }
  const quad = (b, f, u0, u1, v0, v1) =>
    pts([caraPunto(b, f, u0, v0), caraPunto(b, f, u1, v0), caraPunto(b, f, u1, v1), caraPunto(b, f, u0, v1)]);

  function detalle(b, front, tipo, encendido) {
    const visible = (front[0] === 0 && front[1] === 1) || (front[0] === 1 && front[1] === 0);
    if (!visible || !tipo) return '';
    switch (tipo) {
      case 'pantalla':
        return `<polygon points="${quad(b, front, 0.06, 0.94, 0.1, 0.9)}" class="pantalla ${encendido ? 'on' : ''}"/>`;
      case 'heladera':
        return `<polyline points="${pts([caraPunto(b, front, 0, 0.66), caraPunto(b, front, 1, 0.66)])}" class="linea-det"/>` +
          `<polyline points="${pts([caraPunto(b, front, 0.85, 0.72), caraPunto(b, front, 0.85, 0.9)])}" class="manija"/>` +
          `<polyline points="${pts([caraPunto(b, front, 0.85, 0.4), caraPunto(b, front, 0.85, 0.6)])}" class="manija"/>`;
      case 'puerta':
        return `<polygon points="${quad(b, front, 0.08, 0.92, 0.08, 0.92)}" class="puerta-det"/>`;
      case 'rejilla':
        return [0.3, 0.5, 0.7].map((v) =>
          `<polyline points="${pts([caraPunto(b, front, 0.08, v), caraPunto(b, front, 0.92, v)])}" class="linea-det"/>`).join('');
      case 'ojo': {
        const ring = [];
        for (let i = 0; i < 18; i++) {
          const a = (i / 18) * Math.PI * 2;
          ring.push(caraPunto(b, front, 0.5 + 0.3 * Math.cos(a), 0.45 + 0.3 * Math.sin(a) * (b.w / b.h) * 0.9));
        }
        return `<polygon points="${pts(ring)}" class="ojo ${encendido ? 'on' : ''}"/>`;
      }
      case 'termo':
        return `<polygon points="${quad(b, front, 0.35, 0.65, 0.75, 0.88)}" class="puerta-det"/>`;
      default: return '';
    }
  }

  function caja(b, front, encendido, material = '') {
    const c = b.color || '#cbd5e1';
    const top = [iso(b.x, b.y, b.z + b.h), iso(b.x + b.w, b.y, b.z + b.h), iso(b.x + b.w, b.y + b.d, b.z + b.h), iso(b.x, b.y + b.d, b.z + b.h)];
    const izq = [iso(b.x, b.y + b.d, b.z), iso(b.x + b.w, b.y + b.d, b.z), iso(b.x + b.w, b.y + b.d, b.z + b.h), iso(b.x, b.y + b.d, b.z + b.h)];
    const der = [iso(b.x + b.w, b.y, b.z), iso(b.x + b.w, b.y + b.d, b.z), iso(b.x + b.w, b.y + b.d, b.z + b.h), iso(b.x + b.w, b.y, b.z + b.h)];
    return `<polygon points="${pts(izq)}" fill="${tono(c, -0.1)}" class="cara ${material}"/>` +
      `<polygon points="${pts(der)}" fill="${tono(c, -0.25)}" class="cara ${material}"/>` +
      `<polygon points="${pts(top)}" fill="${tono(c, 0.12)}" class="cara ${material}"/>` +
      detalle(b, front, b.detalle, encendido);
  }

  function colorMueble(id, color) {
    const paletas = {
      sofa: { '#6366f1': '#526e69', '#818cf8': '#78918a', '#a5b4fc': '#d9cbb8' },
      alfombra: { '#f59e0b': '#b77d5f' },
      planta: { '#c2410c': '#a9674c' },
      biblioteca: { '#78350f': '#765a43', '#ef4444': '#c78f6c', '#22c55e': '#8c9b82', '#3b82f6': '#718ba0' },
      mesa: { '#92400e': '#765a43', '#b45309': '#a87950' },
      silla: { '#78716c': '#765a43', '#a8a29e': '#a87950' },
    };
    const paleta = paletas[id] || {};
    return paleta[color] || color;
  }

  function decoracionMueble(o, r, z0) {
    if (o.def.id === 'sofa') {
      const cojines = [0.48, 1.55, 2.62].map((x) => ({
        x, y: 0.62, z: 0.79, w: 0.9, d: 0.98, h: 0.14, color: '#a5b4fc',
      }));
      const girados = rotar(cojines, 4, 1.8, o.rot);
      return girados.partes.map((p) => caja({
        ...p, x: o.x + p.x, y: o.y + p.y, z: z0 + p.z,
      }, girados.front, false, 'cojin')).join('');
    }
    if (o.def.id === 'alfombra') {
      return `<polygon points="${pts([
        iso(o.x + 0.18, o.y + 0.18, z0 + 0.06),
        iso(o.x + r.fw - 0.18, o.y + 0.18, z0 + 0.06),
        iso(o.x + r.fw - 0.18, o.y + r.fd - 0.18, z0 + 0.06),
        iso(o.x + 0.18, o.y + r.fd - 0.18, z0 + 0.06),
      ])}" class="alfombra-borde"/>`;
    }
    if (o.def.id === 'planta') {
      const cx = o.x + r.fw / 2, cy = o.y + r.fd / 2;
      const base = iso(cx, cy, z0 + 0.76);
      const hojas = [
        [-15, -12, -29, -33, '#3f7654'],
        [-10, -18, -8, -45, '#6d9b69'],
        [0, -17, 7, -47, '#4d865b'],
        [8, -13, 27, -37, '#7da66e'],
        [13, -7, 42, -26, '#3f7654'],
        [-4, -12, -38, -20, '#588f60'],
        [4, -11, 33, -16, '#6d9b69'],
      ];
      const stems = hojas.map(([sx, sy, tx, ty]) =>
        `<path d="M ${base[0]} ${base[1]} Q ${base[0] + sx / 2} ${base[1] + sy / 2} ${base[0] + tx} ${base[1] + ty}" class="tallo"/>`).join('');
      const follaje = hojas.map(([sx, sy, tx, ty, color]) => {
        const x = base[0] + tx, y = base[1] + ty;
        const midX = base[0] + sx, midY = base[1] + sy;
        const tipX = base[0] + tx * 1.18, tipY = base[1] + ty * 1.18;
        return `<path d="M ${base[0]} ${base[1]} Q ${midX - 7} ${midY - 5} ${x} ${y} Q ${midX + 7} ${midY + 4} ${base[0]} ${base[1]} Z" fill="${color}" class="hoja"/>` +
          `<path d="M ${base[0]} ${base[1]} Q ${midX} ${midY} ${tipX} ${tipY}" class="nervadura"/>`;
      }).join('');
      return stems + follaje;
    }
    return '';
  }

  function colorCielo(h) {
    const stops = [[0, '#0b1026'], [5, '#141b3d'], [6.5, '#fb923c'], [8, '#7dd3fc'], [17, '#7dd3fc'], [18.7, '#f472b6'], [20, '#1e1b4b'], [24, '#0b1026']];
    for (let i = 0; i < stops.length - 1; i++) {
      const [h0, c0] = stops[i], [h1, c1] = stops[i + 1];
      if (h >= h0 && h <= h1) {
        const t = (h - h0) / (h1 - h0 || 1);
        const a = parseInt(c0.slice(1), 16), b = parseInt(c1.slice(1), 16);
        const mix = (s) => Math.round(((a >> s) & 255) * (1 - t) + ((b >> s) & 255) * t);
        return `rgb(${mix(16)},${mix(8)},${mix(0)})`;
      }
    }
    return '#0b1026';
  }
  const oscuridad = (h) => (h >= 8 && h <= 17.5 ? 0 : h < 6 || h > 20 ? 0.5 : h < 8 ? 0.5 * (8 - h) / 2 : 0.5 * (h - 17.5) / 2.5);

  /**
   * opts: { ambiente, objetos:[{key, tipo:'art'|'mueble', def, x, y, rot, label, sub, potencia, intensidad, color}],
   *         seleccion, hora, onSelect(key), onMove(key, x, y), onFin() }
   */
  function crear(el, opts0) {
    let opts = opts0;
    let drag = null;

    function svgPunto(e) {
      const svg = el.querySelector('svg');
      const p = svg.createSVGPoint();
      p.x = e.clientX; p.y = e.clientY;
      return p.matrixTransform(svg.getScreenCTM().inverse());
    }
    function aPiso(sp) {
      const a = (sp.x - OX) / (TW / 2), b = (sp.y - OY) / (TH / 2);
      return { x: (a + b) / 2, y: (b - a) / 2 };
    }

    function render() {
      const { objetos, seleccion, hora, ambiente } = opts;
      const noche = oscuridad(hora);
      let s = `<svg viewBox="0 0 ${VW} ${VH}" class="iso" role="img" aria-label="Ambiente ${ambiente.nombre}">`;
      s += `<defs>
        <radialGradient id="glow"><stop offset="0" stop-color="#34d399" stop-opacity=".85"/><stop offset="1" stop-color="#34d399" stop-opacity="0"/></radialGradient>
        <radialGradient id="glowHot"><stop offset="0" stop-color="#f97316" stop-opacity=".9"/><stop offset="1" stop-color="#f97316" stop-opacity="0"/></radialGradient>
        <radialGradient id="luzG"><stop offset="0" stop-color="#fde68a" stop-opacity=".75"/><stop offset="1" stop-color="#fde68a" stop-opacity="0"/></radialGradient>
        <linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${colorCielo(hora)}"/><stop offset="1" stop-color="${colorCielo((hora + 1) % 24)}"/></linearGradient>
        <linearGradient id="muroA" x1="0" y1="0" x2="0.9" y2="1"><stop stop-color="#f2eee7"/><stop offset="1" stop-color="#d9d3ca"/></linearGradient>
        <linearGradient id="muroB" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#d9d4cc"/><stop offset="1" stop-color="#c9c4bc"/></linearGradient>
        <linearGradient id="cristal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#b9e8f4" stop-opacity=".66"/><stop offset=".52" stop-color="#7fc7df" stop-opacity=".36"/><stop offset="1" stop-color="#e6f4f4" stop-opacity=".7"/></linearGradient>
        <linearGradient id="tapizado" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#c7d2fe"/><stop offset="1" stop-color="#818cf8"/></linearGradient>
        <radialGradient id="sombraSuave"><stop stop-color="#172033" stop-opacity=".2"/><stop offset="1" stop-color="#172033" stop-opacity="0"/></radialGradient>
        <linearGradient id="cesped" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#78966a"/><stop offset=".58" stop-color="#6e8d63"/><stop offset="1" stop-color="#627f5b"/></linearGradient>
        <linearGradient id="sendero" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#d8d0c2"/><stop offset="1" stop-color="#b8ad9c"/></linearGradient>
        <linearGradient id="copa" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#91aa70"/><stop offset=".72" stop-color="#63845d"/><stop offset="1" stop-color="#4d7054"/></radialGradient>
        <pattern id="texturaCesped" width="36" height="30" patternUnits="userSpaceOnUse">
          <path d="M7 11l2-4m-2 4l-3-3m20 16l2-5m-2 5l-3-3" fill="none" stroke="#d4dfb1" stroke-opacity=".45" stroke-width="1.2" stroke-linecap="round"/>
        </pattern>
      </defs>`;
      // El terreno cubre el fondo completo; muros y piso interior se dibujan encima.
      s += `<rect x="0" y="0" width="${VW}" height="${VH}" class="jardin"/>`;
      s += `<rect x="0" y="0" width="${VW}" height="${VH}" class="textura-jardin"/>`;
      const losas = [
        [1.05, -6.9, 0.72, 0.48], [1.55, -6.4, 0.72, 0.48],
        [2.05, -5.9, 0.72, 0.48], [2.55, -5.4, 0.72, 0.48],
      ];
      for (const [x, y, w, d] of losas) {
        s += caja({ x, y, z: 0, w, d, h: 0.055, color: '#c9bda9' }, [0, 1], false, 'losa-patio');
      }
      for (const [x, y] of [[0.7, -5.7], [3.5, -6.8], [4.8, -4.9]]) {
        const [gx, gy] = iso(x, y, 0.04);
        s += `<path d="M ${gx} ${gy} q -5 -8 -8 -9 M ${gx} ${gy} q 0 -10 1 -13 M ${gx} ${gy} q 5 -8 9 -9" class="pasto"/>`;
      }
      if (noche > 0.08) {
        for (const [x, y, z] of [[0.9, -6, 1.5], [3.1, -6.5, 1.8], [4.7, -5.2, 2.2], [2, -4.9, 1.3]]) {
          const [fx, fy] = iso(x, y, z);
          s += `<circle cx="${fx}" cy="${fy}" r="8" class="halo-luciernaga" style="opacity:${noche * 1.5}"/>`;
          s += `<circle cx="${fx}" cy="${fy}" r="2" class="luciernaga" style="animation-delay:${x / 4}s;opacity:${noche * 1.8}"/>`;
        }
      }
      const arbolX = 3.65, arbolY = -6.2;
      const [sombraX, sombraY] = iso(arbolX + 0.2, arbolY + 0.2, 0.03);
      s += `<ellipse cx="${sombraX}" cy="${sombraY}" rx="26" ry="10" class="sombra-arbol"/>`;
      s += caja({ x: arbolX, y: arbolY, z: 0, w: 0.34, d: 0.34, h: 5.5, color: '#806044' }, [0, 1], false, 'tronco-arbol');
      const ramas = [
        [0.17, 0.17, 2.8, -0.35, -0.2, 4.8],
        [0.17, 0.17, 3.7, 0.55, -0.18, 5.1],
        [0.17, 0.17, 4.3, -0.12, 0.58, 5.3],
      ];
      for (const [bx, by, bz, ex, ey, ez] of ramas) {
        s += `<polyline points="${pts([iso(arbolX + bx, arbolY + by, bz), iso(arbolX + ex, arbolY + ey, ez)])}" class="rama-arbol"/>`;
      }
      const [copaX, copaY] = iso(arbolX + 0.17, arbolY + 0.17, 5.2);
      const copas = [
        [-19, 5, 17], [-9, -9, 19], [9, -11, 20], [22, -1, 17],
        [12, 12, 18], [-8, 14, 18], [-23, -8, 15], [1, 1, 21],
      ];
      copas.forEach(([dx, dy, radio], i) => {
        s += `<circle cx="${copaX + dx}" cy="${copaY + dy}" r="${radio}" class="copa copa-${i % 3}"/>`;
      });
      for (const [dx, dy] of [[-10, -8], [13, 4]]) {
        s += `<circle cx="${copaX + dx}" cy="${copaY + dy}" r="1.8" class="flor-copa"/>`;
      }

      // Muros con acabado mate y luz ambiente.
      s += `<polygon points="${pts([iso(0, 0), iso(ANCHO, 0), iso(ANCHO, 0, ALTO), iso(0, 0, ALTO)])}" fill="url(#muroA)" class="pared a"/>`;
      s += `<polygon points="${pts([iso(0, 0), iso(0, FONDO), iso(0, FONDO, ALTO), iso(0, 0, ALTO)])}" fill="url(#muroB)" class="pared b"/>`;
      s += `<polygon points="${pts([iso(0, 0, ALTO), iso(ANCHO, 0, ALTO), iso(ANCHO, -0.3, ALTO), iso(-0.3, -0.3, ALTO), iso(-0.3, FONDO, ALTO), iso(0, FONDO, ALTO)])}" class="pared-borde"/>`;
      // piso
      for (let i = 0; i < ANCHO; i++) for (let j = 0; j < FONDO; j++) {
        s += `<polygon points="${pts([iso(i, j), iso(i + 1, j), iso(i + 1, j + 1), iso(i, j + 1)])}" fill="${ambiente.piso[(i + j) % 2]}" class="baldosa"/>`;
      }
      // Molduras, paneles bajos y carpintería de pared.
      for (const [x0, x1] of [[0.35, 2.35], [2.65, 4.65], [4.95, 6.1], [10, 11.65]]) {
        s += `<polygon points="${pts([iso(x0, 0, 0.42), iso(x1, 0, 0.42), iso(x1, 0, 1.72), iso(x0, 0, 1.72)])}" class="panel pared-panel-a"/>`;
      }
      for (const [y0, y1] of [[0.35, 2.25], [2.55, 4.45], [4.75, 5.85], [8.8, 9.65]]) {
        s += `<polygon points="${pts([iso(0, y0, 0.42), iso(0, y1, 0.42), iso(0, y1, 1.72), iso(0, y0, 1.72)])}" class="panel pared-panel-b"/>`;
      }
      s += `<polyline points="${pts([iso(0, 0, 0.22), iso(ANCHO, 0, 0.22), iso(ANCHO, 0, 0.34), iso(0, 0, 0.34), iso(0, FONDO, 0.34), iso(0, FONDO, 0.22)])}" class="moldura zocalo"/>`;
      s += `<polyline points="${pts([iso(0, 0, ALTO - 0.16), iso(ANCHO, 0, ALTO - 0.16), iso(ANCHO, 0, ALTO - 0.28), iso(0, 0, ALTO - 0.28), iso(0, FONDO, ALTO - 0.28), iso(0, FONDO, ALTO - 0.16)])}" class="moldura cornisa"/>`;

      const cuadro = [iso(2.35, 0, 2.18), iso(5.35, 0, 2.18), iso(5.35, 0, 4.42), iso(2.35, 0, 4.42)];
      const lienzoArte = [iso(2.52, 0, 2.35), iso(5.18, 0, 2.35), iso(5.18, 0, 4.25), iso(2.52, 0, 4.25)];
      s += `<polygon points="${pts(cuadro)}" class="cuadro-sombra"/>`;
      s += `<polygon points="${pts(cuadro)}" class="cuadro-marco"/>`;
      s += `<polygon points="${pts(lienzoArte)}" class="cuadro-lienzo"/>`;
      s += `<polygon points="${pts([iso(2.78, 0, 2.54), iso(3.62, 0, 2.54), iso(4.06, 0, 4.06), iso(3.2, 0, 4.06)])}" class="arte-forma arte-terracota"/>`;
      s += `<polygon points="${pts([iso(3.5, 0, 2.54), iso(4.6, 0, 2.54), iso(4.95, 0, 4.06), iso(4.06, 0, 4.06)])}" class="arte-forma arte-salvia"/>`;
      s += `<polyline points="${pts([iso(2.72, 0, 2.7), iso(4.98, 0, 2.7)])}" class="arte-linea"/>`;

      const win = [iso(6.5, 0, 2.2), iso(9.6, 0, 2.2), iso(9.6, 0, 4.6), iso(6.5, 0, 4.6)];
      s += `<polygon points="${pts(win)}" fill="url(#cielo)" class="ventana"/>`;
      if (hora > 6 && hora < 19) {
        const [cloudX, cloudY] = iso(7.25, 0, 3.95);
        s += `<g class="nube"><ellipse cx="${cloudX}" cy="${cloudY}" rx="15" ry="5"/><ellipse cx="${cloudX + 10}" cy="${cloudY - 4}" rx="9" ry="7"/><ellipse cx="${cloudX + 20}" cy="${cloudY}" rx="13" ry="5"/></g>`;
        const sx = 6.8 + ((hora - 6) / 13) * 2.5, sz = 2.6 + Math.sin(((hora - 6) / 13) * Math.PI) * 1.7;
        const [cx, cy] = iso(sx, 0, sz);
        s += `<circle cx="${cx}" cy="${cy}" r="6" class="sol"/>`;
      } else {
        const [cx, cy] = iso(9, 0, 4.1);
        s += `<circle cx="${cx}" cy="${cy}" r="5" class="luna"/>`;
        for (const [x, z] of [[7.2, 4], [8.1, 3.8], [7.6, 3.1], [9.25, 3.3]]) {
          const [sx, sy] = iso(x, 0, z);
          s += `<circle cx="${sx}" cy="${sy}" r="1.5" class="estrella"/>`;
        }
      }
      s += `<polygon points="${pts([iso(6.5, 0, 2.2), iso(6.86, 0, 2.2), iso(6.86, 0, 4.6), iso(6.5, 0, 4.6)])}" class="cortina"/>`;
      s += `<polygon points="${pts([iso(9.24, 0, 2.2), iso(9.6, 0, 2.2), iso(9.6, 0, 4.6), iso(9.24, 0, 4.6)])}" class="cortina"/>`;
      s += `<polyline points="${pts([iso(6.38, 0, 2.08), iso(9.72, 0, 2.08), iso(9.72, 0, 4.72), iso(6.38, 0, 4.72), iso(6.38, 0, 2.08)])}" class="marco-ventana"/>`;
      s += `<polyline points="${pts([iso(8.05, 0, 2.2), iso(8.05, 0, 4.6)])}" class="marco"/>`;
      s += `<polyline points="${pts([iso(6.5, 0, 3.4), iso(9.6, 0, 3.4)])}" class="marco"/>`;
      s += `<polygon points="${pts([iso(6.65, 0, 4.48), iso(7.5, 0, 4.48), iso(8.15, 0, 2.32), iso(7.55, 0, 2.32)])}" class="reflejo"/>`;

      s += `<polygon points="${pts([iso(0, 6.4), iso(0, 8.4), iso(0, 8.4, 4.2), iso(0, 6.4, 4.2)])}" class="puerta"/>`;
      s += `<polyline points="${pts([iso(0, 6.25), iso(0, 8.55), iso(0, 8.55, 4.32), iso(0, 6.25, 4.32), iso(0, 6.25)])}" class="marco-puerta"/>`;
      s += `<polygon points="${pts([iso(0, 6.58, 0.35), iso(0, 8.22, 0.35), iso(0, 8.22, 3.95), iso(0, 6.58, 3.95)])}" class="panel-puerta"/>`;
      const [hx, hy] = iso(0, 8.02, 2.05);
      s += `<circle cx="${hx}" cy="${hy}" r="3.2" class="picaporte"/>`;
      s += `<polyline points="${pts([iso(ANCHO, 0), iso(0, 0), iso(0, FONDO)])}" class="contorno-piso"/>`;

      // orden de dibujo (atrás → adelante)
      const lista = objetos.map((o) => {
        const f = formaDe(o.def);
        const r = rotar(f.partes, f.W, f.D, o.rot);
        const z0 = (o.def.iso && o.def.iso.z) || 0;
        const hmax = Math.max(...r.partes.map((p) => p.z + p.h));
        const plano = hmax < 0.15;
        return { o, r, z0, hmax, luz: f.luz, key: plano ? -1000 : o.x + o.y + (r.fw + r.fd) / 2 };
      }).sort((a, b) => a.key - b.key);
      for (const it of lista) {
        const { o, r, z0, hmax } = it;
        const sel = seleccion === o.key;
        const cx = o.x + r.fw / 2, cy = o.y + r.fd / 2;
        const on = o.potencia > 0;
        s += `<g class="obj ${o.tipo} ${sel ? 'sel' : ''} ${on ? 'on' : ''}" data-key="${o.key}" data-mueble="${o.def.id || ''}" tabindex="0" role="button" aria-label="${o.label}">`;
        // sombra / huella
        const [shadowX, shadowY] = iso(cx, cy, 0);
        const shadowW = Math.max(26, (r.fw + r.fd) * TW / 4);
        s += `<ellipse cx="${shadowX}" cy="${shadowY}" rx="${shadowW}" ry="${shadowW / 2}" fill="url(#sombraSuave)" class="sombra-obj"/>`;
        s += `<polygon points="${pts([iso(o.x, o.y), iso(o.x + r.fw, o.y), iso(o.x + r.fw, o.y + r.fd), iso(o.x, o.y + r.fd)])}" class="${sel ? 'huella sel' : 'huella'}"/>`;
        if (o.tipo === 'art' && on && o.intensidad > 0) {
          const [gx, gy] = iso(cx, cy, 0);
          const rx = Math.max(30, (r.fw + r.fd) * TW / 3) * (0.8 + o.intensidad * 0.9);
          s += `<ellipse cx="${gx}" cy="${gy}" rx="${rx}" ry="${rx / 2}" fill="url(#${o.intensidad > 0.5 ? 'glowHot' : 'glow'})" class="aura" style="opacity:${0.35 + o.intensidad * 0.65}"/>`;
        }
        const partes = r.partes.slice().sort((a, b) => (a.x + a.y + a.z * 0.01) - (b.x + b.y + b.z * 0.01));
        for (const p of partes) {
          if (o.def.id === 'planta' && p.color === '#16a34a') continue;
          const color = o.tipo === 'mueble' ? colorMueble(o.def.id, p.color) : p.color;
          s += caja({ ...p, color, x: o.x + p.x, y: o.y + p.y, z: z0 + p.z }, r.front, on);
        }
        s += decoracionMueble(o, r, z0);
        if (it.luz && on) {
          const [lx, ly] = iso(cx, cy, z0 + hmax);
          s += `<circle cx="${lx}" cy="${ly}" r="70" fill="url(#luzG)" class="luz-halo"/>`;
        }
        s += '</g>';
      }

      // capa de noche
      if (noche > 0) s += `<rect x="0" y="0" width="${VW}" height="${VH}" class="noche-capa" style="opacity:${noche}"/>`;

      // globos de consumo (siempre arriba)
      for (const it of lista) {
        const { o, r, z0, hmax } = it;
        if (o.tipo !== 'art') continue;
        const [bx, by] = iso(o.x + r.fw / 2, o.y + r.fd / 2, z0 + hmax);
        const txt = o.sub;
        const w = Math.max(64, txt.length * 6.6 + 30);
        const ty = by - 30;
        const sel = seleccion === o.key;
        s += `<g class="globo ${sel ? 'sel' : ''} ${o.potencia > 0 ? 'on' : ''}" data-key="${o.key}" style="--c:${o.color}">
          <line x1="${bx}" y1="${by - 4}" x2="${bx}" y2="${ty + 11}" class="globo-pin"/>
          <rect x="${bx - w / 2}" y="${ty - 11}" width="${w}" height="22" rx="11" class="globo-bg"/>
          <circle cx="${bx - w / 2 + 11}" cy="${ty}" r="4" class="globo-led"/>
          <text x="${bx + 6}" y="${ty + 4}" text-anchor="middle" class="globo-t">${txt}</text>
        </g>`;
      }
      s += '</svg>';
      el.innerHTML = s;
    }

    el.addEventListener('pointerdown', (e) => {
      const g = e.target.closest('[data-key]');
      if (!g) { opts.onSelect && opts.onSelect(null); return; }
      const key = g.dataset.key;
      const o = opts.objetos.find((x) => x.key === key);
      if (!o) return;
      const p = aPiso(svgPunto(e));
      drag = { key, dx: p.x - o.x, dy: p.y - o.y, movio: false, id: e.pointerId };
      el.setPointerCapture(e.pointerId);
      opts.onSelect && opts.onSelect(key);
      e.preventDefault();
    });
    el.addEventListener('pointermove', (e) => {
      if (!drag) return;
      const o = opts.objetos.find((x) => x.key === drag.key);
      if (!o) return;
      const p = aPiso(svgPunto(e));
      const hu = huella(o.def, o.rot);
      const snap = (v) => Math.round(v * 4) / 4;
      let nx = snap(p.x - drag.dx), ny = snap(p.y - drag.dy);
      nx = Math.max(0, Math.min(ANCHO - hu.w, nx));
      ny = Math.max(0, Math.min(FONDO - hu.d, ny));
      if (o.def.iso && o.def.iso.montaje === 'pared') {
        if (o.rot % 4 === 3) nx = 0; else ny = 0;
      }
      if (nx !== o.x || ny !== o.y) {
        drag.movio = true;
        opts.onMove && opts.onMove(drag.key, nx, ny);
      }
    });
    const fin = () => {
      if (drag) {
        if (drag.movio) opts.onFin && opts.onFin(drag.key);
        else opts.onClic && opts.onClic(drag.key);
      }
      drag = null;
    };
    el.addEventListener('pointerup', fin);
    el.addEventListener('pointercancel', fin);

    return {
      actualizar(nuevas) { opts = { ...opts, ...nuevas }; render(); },
      render,
    };
  }

  /** Lugar libre para un objeto nuevo (busca una posición sin superposición). */
  function lugarLibre(def, rot, ocupados) {
    const hu = huella(def, rot);
    const pared = def.iso && def.iso.montaje === 'pared';
    const choca = (x, y) => ocupados.some((o) => x < o.x + o.w && x + hu.w > o.x && y < o.y + o.d && y + hu.d > o.y);
    for (let y = 0; y <= FONDO - hu.d; y += 0.5) {
      for (let x = 0; x <= ANCHO - hu.w; x += 0.5) {
        if (pared && y > 0) break;
        if (!choca(x, y)) return { x, y };
      }
      if (pared) break;
    }
    return { x: Math.max(0, (ANCHO - hu.w) / 2), y: pared ? 0 : Math.max(0, (FONDO - hu.d) / 2) };
  }

  root.SimEscena = { crear, huella, lugarLibre, ANCHO, FONDO };
})(window);
