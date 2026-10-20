# Propuesta — Simulador interactivo de consumo eléctrico

> Documento de ideas y alcance para la app del TP Integrador de Aprendizaje Automático.
> Complementa la consigna (`Consigna_TP_Integrador_Aprendizaje_Automatico.docx`), el
> `README.md` del proyecto y la guía técnica de `simulador/README.md`.

## 0. Qué queremos hacer

En una pantalla nueva (`/simulador`) el usuario arma su casa agregando electrodomésticos y,
para cada uno, indica **cuántas horas lo tiene conectado** y **cuántas de esas horas está
realmente en uso**. Con eso la app calcula:

1. Consumo **activo** (mientras el equipo funciona) y **pasivo** (standby, equipos siempre
   enchufados y consumo de base).
2. Proyección **mensual, estacional y anual** de kWh.
3. Costo **con y sin subsidio**, incluyendo **tarifa social nacional** y **tarifa social
   provincial** (EDEA / Buenos Aires).
4. Una **maqueta** con 3 o 4 electrodomésticos y el consumo de cada uno al lado.
5. Una **ventana 3D** con muebles y artefactos que se puedan arrastrar para recrear un
   ambiente.
6. Una **tabla de consumo estándar** como referencia para cargar valores.
7. Como mejora opcional: **escanear la factura de EDEA** para leer el consumo real y
   calibrar la simulación.

La maqueta y la escena 3D son la capa visual; el cálculo y la comparación tarifaria son el
corazón de la funcionalidad.

### 0.1 Qué agrega este documento

`simulador/README.md` ya describe el catálogo, las fórmulas y el esquema tarifario. Este
documento agrega y ordena las ideas nuevas:

| Tema | Estado en `simulador/README.md` | Qué se agrega acá |
|---|---|---|
| Horas de uso | Solo `horas_dia` | Dos campos: horas conectado y horas en uso. |
| Consumo pasivo | Standby mencionado | Separación activo/pasivo y consumo de base del hogar. |
| Subsidio | Con/sin subsidio y N1/N2/N3 | Tarifa social nacional y provincial como escenarios explícitos. |
| Maqueta | Pantalla sugerida | Prompt listo para generar la maqueta con 4 artefactos. |
| 3D | No está | Ventana 3D con muebles arrastrables y modelo de datos. |
| Factura | Calibración manual | Escaneo de la factura de EDEA con OCR y confirmación. |

---

## 1. Relación con la consigna del TP

El simulador **no reemplaza** las dos tareas obligatorias del trabajo. Las complementa y les
da una explicación entendible para el usuario.

| Requisito de la consigna | Cómo se cumple |
|---|---|
| Regresión: estimar un valor numérico | El modelo de ML ya estima los kWh de las próximas 24 h con datos del medidor. |
| Clasificación: alerta por umbral | El clasificador directo y la regresión + umbral ya responden "¿me paso de la meta diaria?". |
| Comparación de los dos sistemas | Se mantiene la tabla de accuracy, precision, recall, F1, FP y FN. |
| Aplicación web en Flask | Se agrega la ruta `/simulador` al mismo `app.py`, sin reentrenar. |
| Variables disponibles al predecir | El formulario del medidor y el inventario de artefactos usan solo datos que el usuario conoce en ese momento. |
| Al menos 5 predictores y 2000 registros | Se cumplen con el dataset UCI (`household_power_consumption`). El simulador no cambia el dataset del modelo. |
| Sin base de datos | Catálogo, perfiles y tarifas en CSV/JSON; la escena 3D en `localStorage`. |
| Sin cargar `.pkl` externos | La app solo carga los modelos propios de `modelos/`. Las fotos de factura se validan aparte. |
| Privacidad | No se piden datos personales. Si se escanea una factura, se procesa localmente y no se guarda. |
| Despliegue en Vercel | Todo es estático + Flask; la escena 3D y el OCR corren en el navegador. |

**Aclaración importante para la defensa:** la proyección mensual/anual del simulador es una
**estimación determinista** basada en los supuestos del usuario, no una predicción de
aprendizaje automático. La predicción estadística es la del modelo de ML. Conviene decirlo
explícitamente para no mezclar los dos conceptos.

---

## 2. Flujo de usuario

```
1. Entrar a /simulador
2. Elegir un perfil (1 persona / pareja / familia / personalizado)
3. Agregar electrodomésticos desde el catálogo o crear uno propio
4. Para cada uno: cantidad, horas conectado/día, horas en uso/día, días por semana
5. Ver el consumo activo y pasivo, el total mensual y el anual
6. Elegir el escenario tarifario: sin subsidio / social nacional / social provincial
7. Comparar costo, ahorro y costo efectivo por kWh
8. (Opcional) Abrir la ventana 3D y arrastrar los artefactos al ambiente
9. (Opcional) Escanear la factura de EDEA para calibrar el cálculo
10. Guardar o reiniciar el escenario
```

### 2.1 Maqueta de la pantalla principal

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ⚡ Simulador de consumo              [Sin subsidio ▾]   [Ver ambiente 3D] │
├────────────────────────────────┬─────────────────────────────────────────┤
│  Tus electrodomésticos         │  Resumen del mes                        │
│                                │                                         │
│  ┌──────────────────────────┐  │   189 kWh/mes        $ 28.350           │
│  │ 🧊 Heladera 300 L        │  │   Activo 184 kWh · Pasivo 5 kWh         │
│  │ Conectada 24 h · Uso 8 h │  │                                         │
│  │ 29 kWh/mes     $ 4.350   │  │   [gráfico de barras: 12 meses]         │
│  └──────────────────────────┘  │                                         │
│  ┌──────────────────────────┐  │   Con subsidio     $ 17.010             │
│  │ 📺 TV LED 50"            │  │   Sin subsidio     $ 28.350             │
│  │ Conectada 8 h · Uso 5 h  │  │   Ahorro           $ 11.340 (40 %)      │
│  │ 12 kWh/mes     $ 1.800   │  │                                         │
│  └──────────────────────────┘  │   Detalle por artefacto                 │
│  ┌──────────────────────────┐  │   Heladera      29 kWh   $ 4.350        │
│  │ ❄️ Aire split 3500 W     │  │   Aire          58 kWh   $ 8.700        │
│  │ Conectado 4 h · Uso 4 h  │  │   TV            12 kWh   $ 1.800        │
│  │ 58 kWh/mes     $ 8.700   │  │   Termotanque   90 kWh   $ 13.500       │
│  └──────────────────────────┘  │                                         │
│  ┌──────────────────────────┐  │   [Activo vs. pasivo]  [Por categoría]  │
│  │ 🚿 Termotanque 1500 W    │  │                                         │
│  │ Conectado 2 h · Uso 2 h  │  │   (costo de energía, sin cargo fijo     │
│  │ 90 kWh/mes    $ 13.500   │  │    ni impuestos)                        │
│  └──────────────────────────┘  │                                         │
│                                │                                         │
│  [+ Agregar electrodoméstico]  │  [Comparar escenarios]  [Reiniciar]     │
└────────────────────────────────┴─────────────────────────────────────────┘
```

Cada tarjeta de artefacto muestra, como mínimo:

- nombre e ícono;
- horas conectado y horas en uso;
- kWh/mes y costo estimado;
- botón para editar y botón para quitar.

El resumen muestra el total, la separación activo/pasivo, el gráfico de 12 meses y la
comparación tarifaria. En el celular, el resumen va arriba y el editor abajo.

---

## 3. Funcionalidad: horas conectado y horas en uso

### 3.1 Los dos campos

Pedir solo "horas conectado" no alcanza para calcular bien el consumo: un televisor puede
estar **8 h enchufado** pero **5 h encendido**. Las otras 3 h consume standby. Por eso cada
artefacto tiene:

| Campo | Unidad | Rango | Para qué sirve |
|---|---|---|---|
| `horas_conectado_dia` | h/día | 0–24 | Tiempo que está enchufado. |
| `horas_uso_dia` | h/día | 0–`horas_conectado` | Tiempo que realmente funciona. |
| `dias_semana` | días | 1–7 | Frecuencia de uso. |
| `cantidad` | unidades | 1–20 | Equipos iguales. |

La diferencia `horas_conectado_dia − horas_uso_dia` es el tiempo en que puede haber consumo
pasivo (standby). Si el equipo se desenchufa, el resto del día no consume nada.

### 3.2 Reglas de interfaz

- Al elegir un artefacto del catálogo, se precargan horas típicas y potencia.
- Un solo control (slider + campo numérico) para las horas, con presets: 1, 2, 4, 8, 12, 24.
- Si `horas_uso_dia > horas_conectado_dia`, mostrar error y no calcular.
- Si el artefacto es de ciclo (lavarropas), pedir **ciclos por semana** en lugar de horas.
- Si es de etiqueta anual (heladera), pedir **kWh/año** y usar un ciclo de trabajo estimado.
- Mostrar siempre la unidad (`kWh/mes`, no solo `kWh`).
- Un botón "no sé las horas" abre la tabla de consumo estándar con valores sugeridos.

### 3.3 Modos de uso del catálogo

| Modo | Cuándo se usa | Fórmula base |
|---|---|---|
| `horas` | TV, aire, calefactor, lámpara, termotanque | `P/1000 × horas_uso_dia` |
| `ciclos` | Lavarropas, lavavajillas, secarropas | `kWh_ciclo × ciclos_semana / 7` |
| `anual` | Heladera, freezer (etiqueta kWh/año) | `kWh_año / 365`, normalizado por mes |
| `siempre` | Router, decodificador, cargadores | `P/1000 × 24` (o standby medido) |

---

## 4. Consumo activo y consumo pasivo

### 4.1 Definiciones

- **Consumo activo:** energía que usa el artefacto mientras cumple su función. Incluye el
  compresor de la heladera cuando está enfriando.
- **Consumo pasivo:** energía que usa el equipo aunque no esté cumpliendo su función:
  standby, luces de reloj, cargadores enchufados sin celular, router siempre encendido.
- **Consumo de base del hogar:** el pasivo de todos los equipos que nunca se desenchufan.
  Se puede medir con un wattmeter cuando todo está "apagado".

> **Aclaración de vocabulario:** en la app usamos "pasivo" en sentido práctico: lo que
> consumís aunque no estés usando el artefacto. Un router siempre encendido entra en la base
> del hogar, aunque técnicamente esté funcionando. Lo importante es no contarlo dos veces.

### 4.2 Fórmulas

Para un artefacto en modo `horas`:

```
E_activo_dia  = potencia_w / 1000 × horas_uso_dia
E_pasivo_dia  = standby_w / 1000 × (horas_conectado_dia − horas_uso_dia)
E_dia         = E_activo_dia + E_pasivo_dia
E_mes         = E_dia × dias_semana × 52 / 12
```

Para el pasivo de base del hogar:

```
E_pasivo_base_mes = potencia_base_w / 1000 × 24 × dias_mes
```

Para la heladera en modo `anual`, el kWh/año de la etiqueta ya incluye el ciclo del
compresor. No hay que multiplicar la potencia por 24 h. Si la etiqueta no incluye standby,
se suma aparte; si lo incluye, no se cuenta dos veces.

### 4.3 Ejemplo

| Artefacto | Potencia | Conectado | En uso | Standby | Activo/mes | Pasivo/mes |
|---|---:|---:|---:|---:|---:|---:|
| TV LED 50" | 80 W | 8 h/día | 5 h/día | 3 W | 12,0 kWh | 0,3 kWh |
| Router | 10 W | 24 h/día | 24 h/día | — | 7,3 kWh | 0 kWh |
| Heladera 300 L | — | 24 h/día | ciclo | — | 29,2 kWh | — |
| Cargadores (3) | 2 W c/u | 24 h/día | 1 h/día | 2 W | 0,2 kWh | 4,2 kWh |

> El pasivo por equipo parece poco, pero suma. Diez equipos con 1–3 W de standby pueden
> aportar 10–25 kWh/mes, equivalentes a varias horas de aire acondicionado.

### 4.4 Cómo mostrarlo

- Tarjeta "Consumo activo" y tarjeta "Consumo pasivo" en el resumen.
- Barra apilada activo/pasivo por mes.
- Ranking "qué te consume más" y "qué te consume sin que lo uses".
- Consejo automático: "Tu standby representa el 6 % del consumo; desenchufar los cargadores
  ahorraría X kWh/mes".

---

## 5. Proyección mensual, estacional y anual

### 5.1 Cálculo

Para cada artefacto `i` y cada mes `m`:

```
consumo_mes_i(m) = base_diaria_i × factor_mes_i(m) × dias(m)
consumo_mes(m)   = Σ_i consumo_mes_i(m) + pasivo_base_mes(m)
consumo_anual    = Σ_m consumo_mes(m)
```

La `base_diaria_i` sale del modo de uso de la sección 3.3. El `factor_mes` modela la
estacionalidad:

- Aire: `1.0, 1.0, 0.8, 0.2, 0, 0, 0, 0, 0, 0.2, 0.6, 1.0`
- Calefacción: `0, 0, 0.1, 0.5, 0.8, 1.0, 1.0, 0.9, 0.6, 0.2, 0, 0`
- Heladera: `1.1, 1.1, 1.0, 0.9, 0.9, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0, 1.1`
- TV y artefactos de uso constante: todos `1`

En la interfaz, el usuario elige un preset ("todo el año", "solo verano", "solo invierno",
"personalizado"). El modo personalizado muestra 12 sliders.

Para el modo `anual`, el total de la etiqueta se reparte entre los meses para que la suma dé
exactamente el valor anual:

```
kWh_mes(m) = kWh_año × (factor_m × dias_m) / Σ_k (factor_k × dias_k)
```

### 5.2 Ejemplo verificable (4 artefactos)

Supuestos: heladera 350 kWh/año; aire 1.200 W, 4 h/día en verano; TV 80 W, 5 h/día; termotanque
1.500 W, 2 h/día; pasivo de base 12 W todo el día.

| Mes | Heladera | Aire | TV | Termotanque | Pasivo base | Total |
|---|---:|---:|---:|---:|---:|---:|
| Ene | 33,3 | 148,8 | 12,4 | 93,0 | 8,9 | 296,4 |
| Feb | 30,1 | 134,4 | 11,2 | 84,0 | 8,1 | 267,8 |
| Mar | 30,2 | 119,0 | 12,4 | 93,0 | 8,9 | 263,5 |
| Abr | 26,3 | 28,8 | 12,0 | 90,0 | 8,6 | 165,7 |
| May | 27,2 | 0,0 | 12,4 | 93,0 | 8,9 | 141,5 |
| Jun | 26,3 | 0,0 | 12,0 | 90,0 | 8,6 | 136,9 |
| Jul | 27,2 | 0,0 | 12,4 | 93,0 | 8,9 | 141,5 |
| Ago | 27,2 | 0,0 | 12,4 | 93,0 | 8,9 | 141,5 |
| Sep | 29,3 | 0,0 | 12,0 | 90,0 | 8,6 | 139,9 |
| Oct | 30,2 | 29,8 | 12,4 | 93,0 | 8,9 | 174,3 |
| Nov | 29,3 | 86,4 | 12,0 | 90,0 | 8,6 | 226,3 |
| Dic | 33,3 | 148,8 | 12,4 | 93,0 | 8,9 | 296,4 |
| **Año** | **350,0** | **696,0** | **146,0** | **1.095,0** | **105,1** | **2.392,1** |

Totales por artefacto al año: heladera 350 kWh, aire 696 kWh, TV 146 kWh, termotanque
1.095 kWh y pasivo 105 kWh. El aire explica el pico de verano; el termotanque explica la
base de todos los meses. Este ejemplo sirve como test del cálculo.

> Los totales se calculan sin redondear; las filas se muestran con un decimal, por eso la
> suma de las filas puede diferir en una décima.

### 5.3 Incertidumbre

La mayor incertidumbre está en las horas de uso, no en la potencia. Mostrar un rango, no un
número único:

- escenario típico (número grande);
- mínimo y máximo (±20–30 % en las horas);
- aclaración: "el rango depende de los hábitos que cargaste".

---

## 6. Costo con y sin subsidio

### 6.1 Principio

El subsidio **no cambia los kWh**: cambia el precio que se paga por esos kWh. Por eso se
calcula una sola vez el consumo y se aplican distintos escenarios tarifarios.

Escenarios mínimos:

| Escenario | Quién lo elige | Qué modela |
|---|---|---|
| Sin subsidio | Segmento N1 o usuario que no recibe beneficio | Precio pleno, un solo bloque. |
| Tarifa social nacional | Hogar beneficiario del régimen nacional | Precio bonificado con tope mensual. |
| Tarifa social provincial | Beneficiario de la provincia / EDEA | Bonificación provincial adicional o distinta. |
| N2 / N3 (opcional) | Segmentación energética | Subsidio parcial por tramos. |

El usuario **elige qué beneficio tiene**; la app no decide la elegibilidad. Los valores,
topes y fechas se cargan desde `tarifas.json`, nunca hardcodeados en el HTML.

### 6.2 Fórmula por bloques

```
costo_energia = Σ bloques:
    cantidad = max(0, min(kWh, hasta_kwh) − piso)
    costo    = cantidad × precio_kwh
    piso     = hasta_kwh

costo_total = cargo_fijo + costo_energia + impuestos
```

Detalles que hay que respetar:

- El tope subsidiado es **mensual**: se aplica mes a mes, no al total anual.
- Si la factura es bimestral, el tope se prorratea (verificar en la fuente).
- Los impuestos pueden calcularse sobre energía o sobre el total; el esquema lo indica.
- La tarifa social nacional y la provincial **no siempre se acumulan**. La app aplica un
  escenario por vez y muestra una advertencia.
- Mostrar `vigencia_desde`, `fuente_id` y una leyenda: "estimación orientativa; no reemplaza
  la factura ni el asesoramiento de la distribuidora".

### 6.3 Ejemplo ilustrativo (400 kWh/mes, valores NO vigentes)

| Concepto | Sin subsidio | Social nacional | Social provincial |
|---|---:|---:|---:|
| Consumo | 400 kWh | 400 kWh | 400 kWh |
| Precio pleno | 150 $/kWh | 150 $/kWh | 150 $/kWh |
| Precio bonificado | — | 90 $/kWh | 72 $/kWh |
| Tope bonificado | — | 350 kWh | 350 kWh |
| Energía | 60.000 | 39.000 | 32.700 |
| Cargo fijo | 5.000 | 5.000 | 5.000 |
| Subtotal | 65.000 | 44.000 | 37.700 |
| IVA 21 % | 13.650 | 9.240 | 7.917 |
| **Total** | **78.650** | **53.240** | **45.617** |
| Costo efectivo | 196,6 $/kWh | 133,1 $/kWh | 114,0 $/kWh |
| Ahorro vs. sin subsidio | — | **25.410 (32,3 %)** | **33.033 (42,0 %)** |

> Los números son solo para mostrar el mecanismo. Reemplazarlos por el cuadro tarifario
> vigente de EDEA y por los valores nacionales/provinciales con su fecha.

### 6.4 Qué mostrar en pantalla

- Costo mensual con cada escenario.
- Costo anual con cada escenario (sumando mes a mes, respetando el tope).
- Ahorro en pesos y en porcentaje.
- kWh dentro y fuera del tope bonificado.
- Costo efectivo ($/kWh) para comparar peras con peras.
- Gráfico de costo vs. consumo con el quiebre del tope subsidiado.
- Aviso si el consumo supera el tope: "te pasaste 50 kWh del bloque subsidiado".

---

## 7. Tabla de consumo estándar

Sirve para que el usuario que no conoce la potencia de su equipo pueda empezar. Son **valores
de arranque**, no universales: hay que verificarlos contra la etiqueta, el manual o una
medición.

| Artefacto | Potencia típica (W) | Uso típico | kWh/mes aprox. | Modo |
|---|---:|---|---:|---|
| Heladera con freezer 300–400 L | 100–250 | 24 h por ciclos | 25–45 | anual |
| Freezer | 100–250 | 24 h por ciclos | 20–40 | anual |
| Aire split 3500 W (frío) | 900–1.500 | 4 h/día en verano | 100–180 (solo verano) | horas |
| Calefactor eléctrico 2.000 W | 2.000 | 3–6 h/día en invierno | 180–360 (solo invierno) | horas |
| Termotanque eléctrico 1.500 W | 1.500 | 2–4 h/día | 90–180 | horas |
| Lavarropas 8 kg | 400–700 | 4 ciclos/semana | 10–20 | ciclos |
| Secarropas 2.000 W | 1.800–2.500 | 2–3 ciclos/semana | 25–65 | ciclos |
| Lavavajillas | 1.200–1.500 | 1 ciclo/día | 30–65 | ciclos |
| Horno eléctrico | 2.000–3.000 | 4–8 h/mes | 8–24 | horas |
| Microondas | 800–1.200 | 15 min/día | 6–9 | horas |
| TV LED 50" | 60–120 | 4–6 h/día | 7–22 | horas |
| Notebook | 45–90 | 4–8 h/día | 5–22 | horas |
| Iluminación LED (8 × 9 W) | 72 | 4 h/día | 9 | horas |
| Router / standby total | 5–15 | 24 h | 4–11 | siempre |

Recomendaciones:

- Medir al menos 3 artefactos con un wattmeter y anotar la fuente.
- Para la heladera, usar el kWh/año de la etiqueta antes que la potencia nominal.
- No sumar el standby dos veces: revisar si la etiqueta ya lo incluye.
- Para el aire, usar la potencia eléctrica de entrada, no la capacidad de frío.

---

## 8. Maqueta con 3 o 4 electrodomésticos

### 8.1 Alcance

Una primera pantalla estática (HTML + CSS, sin lógica compleja) para validar el diseño antes
de programar todo. Debe incluir:

- 4 artefactos: heladera, TV, aire y termotanque;
- el consumo de cada uno al lado del nombre;
- el total mensual y anual;
- el toggle de subsidio;
- un gráfico simple de 12 meses (barras CSS o SVG);
- diseño responsive.

### 8.2 Prompt para pedirle la maqueta a una IA

```text
Actuá como diseñador UX/UI. Generá una maqueta en HTML + CSS (sin frameworks) de una
pantalla de simulador de consumo eléctrico hogareño, en español rioplatense.

Requisitos:
- Encabezado: "Simulador de consumo" y un selector "Sin subsidio / Tarifa social nacional /
  Tarifa social provincial".
- Columna izquierda: lista de 4 electrodomésticos con ícono, nombre, horas conectado, horas
  en uso, kWh/mes y costo.
  Artefactos: heladera 300 L (24 h conectada, 8 h en uso, 29 kWh/mes), TV LED 50" (8 h
  conectada, 5 h en uso, 12 kWh/mes), aire split 3500 W (4 h conectado, 4 h en uso, 58
  kWh/mes), termotanque 1500 W (2 h conectado, 2 h en uso, 90 kWh/mes).
- Botón "+ Agregar electrodoméstico".
- Columna derecha: tarjetas con total mensual (189 kWh), total anual (2.268 kWh),
  consumo activo vs. pasivo, costo con subsidio, costo sin subsidio y ahorro.
- Gráfico de barras de los 12 meses.
- Tabla "Detalle por artefacto" con kWh y costo.
- Pie: "Estimación orientativa. No reemplaza la factura."
- Paleta: fondo claro, acento verde/azul, tarjetas con sombra suave, tipografía legible.
- Responsive: en el celular, resumen arriba y lista abajo.

Entregá un solo archivo HTML con el CSS incluido. No uses JavaScript.
```

### 8.3 Prompt para una maqueta visual / 3D

```text
Generá una imagen de maqueta de una habitación moderna en vista isométrica, con una heladera,
un televisor, un aire acondicionado y un termotanque. Cada artefacto debe tener una etiqueta
flotante con su consumo mensual en kWh. Estilo limpio, colores claros, sin texto pequeño,
formato 16:9. La imagen se usará como referencia para una escena 3D interactiva.
```

---

## 9. Ventana 3D con muebles interactivos

### 9.1 Objetivo

Que el usuario recree un ambiente y vea el consumo "en contexto": arrastra un sofá, una cama,
un televisor o una heladera, y la app actualiza el consumo del artefacto y el total.

### 9.2 Interacciones mínimas

- Arrastrar muebles y artefactos sobre el piso.
- Rotar con una tecla o un botón.
- Agregar un artefacto desde el catálogo y colocarlo en la escena.
- Hacer clic en un artefacto para abrir su tarjeta de horas y consumo.
- Mostrar un globo con los kWh/mes sobre cada artefacto.
- Botones "reiniciar escena" y "modo presentación".
- Guardar la posición en `localStorage` (no hace falta cuenta ni base de datos).

### 9.3 Tecnología

| Opción | Ventaja | Costo |
|---|---|---|
| Three.js + GLTF + `DragControls` | Control total, corre en el navegador, compatible con Vercel | Más código y assets. |
| `react-three-fiber` | Cómodo si se usa React | Agrega React al proyecto Flask. |
| Spline | Muy rápido de prototipar | Dependencia externa y peso. |
| 2D isométrico (SVG/CSS) | Liviano, accesible, fácil de mantener | Menos impacto visual. |

Recomendación: empezar por un **2D isométrico arrastrable** (fase 4A) y, si el tiempo
alcanza, pasar a **Three.js** (fase 4B). La consigna no exige 3D; es una mejora de
presentación, no un requisito académico.

### 9.4 Modelo de datos de la escena

```json
{
  "version": 1,
  "ambiente": "living",
  "objetos": [
    { "id": "obj-1", "tipo": "heladera", "x": 2.4, "y": 0, "z": -1.5, "rot": 90 },
    { "id": "obj-2", "tipo": "tv", "x": 0.5, "y": 1.1, "z": -2.8, "rot": 0 },
    { "id": "obj-3", "tipo": "aire", "x": 2.4, "y": 2.6, "z": -2.9, "rot": 0 },
    { "id": "obj-4", "tipo": "sofa", "x": 0, "y": 0, "z": 0, "rot": 180 }
  ]
}
```

Cada `tipo` se vincula al `id` del catálogo de electrodomésticos. Los muebles que no consumen
(sofá, mesa, cama) solo aportan contexto visual.

### 9.5 Buenas prácticas

- Assets low-poly y texturas livianas (menos de 5 MB en total).
- Carga diferida: la escena 3D se descarga solo al abrirla.
- Soporte de touch para celular y teclado para accesibilidad.
- Alternativa en lista/tabla si el dispositivo no soporta WebGL.
- Respetar `prefers-reduced-motion`.
- No subir modelos 3D externos: los assets van en `public/`.

### 9.6 Riesgo de alcance

La escena 3D puede consumir más tiempo que el cálculo y las tarifas juntas. Dejarla para el
final y no bloquear la entrega por ella. Si no llega a estar terminada, mostrar una imagen
isométrica con hotspots (puntos clickeables) cumple el mismo objetivo narrativo.

---

## 10. Mejora opcional: escanear la factura de EDEA

### 10.1 Para qué sirve

Leer de la factura el **consumo real del período** y compararlo con la simulación. Eso permite:

- calibrar las horas o la potencia que el usuario cargó;
- mostrar "tu factura es 1,15× la simulación";
- usar el importe real como control del costo estimado;
- detectar si el usuario se pasó del tope subsidiado.

### 10.2 Datos a extraer

| Campo | Uso | ¿Se guarda? |
|---|---|---|
| Consumo del período (kWh) | Calibrar y comparar | Sí, solo el número. |
| Período (desde/hasta) | Calcular días y prorratear | Sí. |
| Tarifa / segmento | Elegir escenario | Sí. |
| Importe total | Control del costo | Sí. |
| Cargo fijo e impuestos | Detalle de la factura | Opcional. |
| NIS, titular, dirección | No son necesarios | **No**. Se descartan. |

### 10.3 Opciones técnicas

| Opción | Cómo funciona | Ventaja | Limitación |
|---|---|---|---|
| **Tesseract.js** en el navegador | OCR en WASM, sin servidor | Privacidad, gratis, compatible con Vercel | Menos preciso en fotos; descarga ~15 MB de datos de idioma. |
| `pytesseract` en el servidor | OCR en Python | Fácil de integrar con Flask | Requiere binario de Tesseract; pesado para Vercel. |
| OCR en la nube (Google Vision, Textract, OCR.space) | API externa | Mejor precisión | Necesita clave, costo y subir la imagen. |
| Carga manual asistida | El usuario tipea los datos | Siempre funciona | No es "escaneo". |

Recomendación: **Tesseract.js + confirmación manual + fallback manual**. La imagen se procesa
en el navegador, no se sube a ningún servidor y se descarta al terminar.

### 10.4 Flujo

```
1. Botón "Escanear factura"
2. Arrastrar o seleccionar una foto/PDF
3. Vista previa + recorte de la zona útil
4. OCR en el navegador (barra de progreso)
5. Campos detectados en un formulario editable:
   período, kWh, tarifa, importe, vencimiento
6. El usuario revisa y corrige
7. "Usar estos datos" → calibra la simulación
8. La imagen se descarta; solo quedan los números confirmados
```

### 10.5 Reglas de extracción

- Aceptar solo imágenes JPG/PNG/WebP y PDF de una página; límite de 10 MB.
- Preprocesar: escala de grises, contraste, rotación y recorte.
- Buscar patrones como `Consumo`, `kWh`, `Período`, `Importe`, `Vencimiento`.
- Interpretar números argentinos: `1.234,56` = 1234,56.
- Validar: kWh entre 0 y 2.000; período de 25 a 65 días; importe mayor que 0.
- Si la confianza es baja, no completar nada y pedir carga manual.
- Nunca aplicar los datos sin confirmación del usuario.
- No registrar la imagen ni datos personales en logs.

### 10.6 Calibración

```
factor = kWh_factura / kWh_simulado
```

Si el factor se aleja de 1, revisar en este orden: horas de uso, potencia, cantidad de
artefactos. Mostrar el factor en pantalla ("ajustado a tu factura por 1,15") y no modificar
el catálogo para que cierre un solo mes.

### 10.7 Plan de prueba

- Probar con 3 a 6 facturas reales de EDEA, de distintos meses y layouts.
- Medir aciertos por campo (kWh, período, importe).
- Incluir fotos borrosas, rotadas y con sombras.
- Documentar la precisión obtenida y los casos en que conviene la carga manual.

---

## 11. Arquitectura propuesta

```
simulador/
├── README.md
├── calculo.py                 # funciones puras: consumo, costos, proyección
├── tarifas.py                 # carga y validación de tarifas.json
├── ocr_factura.py             # opcional, si se usa OCR del lado servidor
├── datos/
│   ├── catalogo_electrodomesticos.csv
│   ├── perfiles_uso.csv
│   ├── tarifas.json
│   └── fuentes.csv
├── tests/
│   └── test_calculo.py
└── static/
    ├── simulador.js
    ├── escena3d.js
    └── modelos/               # assets GLTF/GLB low-poly
templates/
└── simulador.html
public/
└── simulador.css
```

Rutas Flask:

| Ruta | Método | Para qué |
|---|---|---|
| `/simulador` | GET | Pantalla principal. |
| `/api/simulador` | POST | Recibe el inventario y devuelve kWh y costos en JSON. |
| `/api/factura` | POST | Opcional: recibe la imagen y devuelve los campos detectados (si el OCR es del lado servidor). |

Recomendación: que el cálculo viva en Python (`calculo.py`) y que el navegador lo consulte con
`fetch` (con *debounce*). Así hay una sola fuente de verdad y el cálculo se puede testear. Si
se quiere respuesta instantánea sin red, se duplica la fórmula en JS y se valida contra el
servidor; es más mantenimiento y más riesgo de divergencia.

No hace falta base de datos:

- catálogo y perfiles: CSV;
- tarifas: JSON con `version` y `vigencia_desde`;
- selección del usuario: `localStorage`;
- escena 3D: `localStorage`;
- factura: se procesa y se descarta.

---

## 12. Modelo de datos de la selección

```json
{
  "perfil": "personalizado",
  "escenario": "tarifa_social_provincial",
  "mes": 10,
  "electrodomesticos": [
    {
      "id": "heladera_freezer_300l",
      "cantidad": 1,
      "horas_conectado_dia": 24,
      "horas_uso_dia": 8,
      "dias_semana": 7
    },
    {
      "id": "tv_led_50",
      "cantidad": 1,
      "horas_conectado_dia": 8,
      "horas_uso_dia": 5,
      "dias_semana": 7
    },
    {
      "id": "aire_split_3500",
      "cantidad": 1,
      "horas_conectado_dia": 4,
      "horas_uso_dia": 4,
      "dias_semana": 7
    },
    {
      "id": "termotanque_1500",
      "cantidad": 1,
      "horas_conectado_dia": 2,
      "horas_uso_dia": 2,
      "dias_semana": 7
    }
  ],
  "pasivo_base_w": 12
}
```

Validaciones:

- `cantidad` entero entre 1 y 20.
- `horas_uso_dia ≤ horas_conectado_dia`.
- `horas_conectado_dia` entre 0 y 24.
- `dias_semana` entre 1 y 7.
- `pasivo_base_w` entre 0 y 200.
- `id` existente en el catálogo.
- `escenario` existente en `tarifas.json`.

---

## 13. Fases de implementación

| Fase | Alcance | Entregable | Riesgo |
|---|---|---|---|
| **0** | Catálogo, fórmulas y tests | `calculo.py` + ejemplo verificado | Bajo |
| **1** | Pantalla interactiva: agregar/quitar artefactos, horas, activo/pasivo, mensual/anual | `/simulador` funcionando | Medio |
| **2** | Tarifas: sin subsidio, social nacional y provincial; comparación y gráficos | `tarifas.json` + tabla comparativa | Medio |
| **3** | Maqueta visual con 4 artefactos y consumo al lado | `simulador.html` + CSS | Bajo |
| **4** | Escena 3D o 2D isométrica arrastrable | `escena3d.js` + assets | Alto |
| **5** | Escaneo de factura EDEA | OCR + confirmación + calibración | Alto |
| **6** | Modo presentación y prueba en celular | Demo estable | Bajo |

Orden recomendado: **0 → 1 → 2 → 3 → 6 → 4 → 5**. La maqueta y el modo presentación dan
resultado visual rápido; el 3D y el OCR son lo más costoso y lo menos exigido por la consigna.

### 13.1 Definición de terminado del MVP

- [ ] Se pueden agregar y quitar artefactos sin recargar la página.
- [ ] Cambiar horas conectado/uso actualiza kWh y costo.
- [ ] Se ve el consumo activo y el pasivo por separado.
- [ ] Se ven mes, temporada y año.
- [ ] El toggle de subsidio cambia el costo, no el consumo.
- [ ] Se comparan al menos tres escenarios tarifarios.
- [ ] Cada número tiene una fuente o un supuesto visible.
- [ ] El ejemplo de la sección 5.2 coincide con el test.
- [ ] Funciona en celular y en notebook.
- [ ] La app no reentrena ni necesita base de datos.

---

## 14. Riesgos y limitaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Las horas de uso son un supuesto | El resultado puede variar mucho | Mostrar rango y permitir calibrar con la factura. |
| Tarifas y topes cambian | Costos desactualizados | `tarifas.json` con vigencia y fuente; no hardcodear. |
| Tarifa social nacional vs. provincial | Se pueden sumar beneficios que no corresponden | Aplicar un escenario por vez y advertir. |
| Tope mensual aplicado al año | Sobreestima el subsidio | Calcular mes a mes. |
| Factura mensual vs. bimestral | Tope mal prorrateado | Detectar el período y prorratear. |
| OCR impreciso | Datos incorrectos | Confirmación manual y validación de rangos. |
| Privacidad de la factura | Exposición de datos personales | Procesar localmente, no guardar, descartar PII. |
| La escena 3D crece de más | Retrasa la entrega | Fase separada y fallback 2D. |
| Confundir simulación con ML | Crítica metodológica | Aclarar la diferencia en la app y en el informe. |
| Un solo hogar en el dataset | No generaliza | Declararlo en limitaciones. |

---

## 15. Decisiones pendientes

1. ¿La tarifa social provincial se modela como un precio distinto, como un porcentaje de
   descuento o como un tope diferente?
2. ¿Se incluye N2/N3 además de "sin subsidio" y las dos tarifas sociales?
3. ¿La factura de EDEA es mensual o bimestral en el caso que van a usar?
4. ¿La escena 3D se hace con Three.js o alcanza con una vista isométrica 2D?
5. ¿Los muebles son solo decorativos o también se puede elegir entre distintos ambientes
   (living, cocina, dormitorio)?
6. ¿El escaneo de factura se hace con Tesseract.js en el navegador o se deja como carga
   manual para la primera versión?
7. ¿Se muestra un número único o una banda de incertidumbre?
8. ¿El simulador va en la misma página del TP o en una ruta separada `/simulador`?
9. ¿Se usa una librería de gráficos o barras CSS/SVG para simplificar el despliegue?
10. ¿Se incluyen artefactos a gas (sin sumar kWh) para comparar?

---

## Anexo A. Fuentes recomendadas

| Fuente | Qué se puede obtener |
|---|---|
| Etiqueta energética del fabricante | kWh/año, kWh/ciclo, potencia y standby del modelo exacto. |
| Manual o ficha técnica | Potencia nominal, standby y duración de ciclos. |
| ENRE — https://www.enre.gov.ar/ | Cuadros tarifarios, segmentos y guías. |
| Secretaría de Energía — https://www.argentina.gob.ar/energia | Etiquetado, eficiencia y segmentación. |
| EDEA — https://www.edea.com.ar/ | Tarifas, factura y requisitos de la tarifa social provincial. |
| INTI — https://www.inti.gob.ar/ | Eficiencia energética en artefactos. |
| IRAM — https://www.iram.org.ar/ | Normas de etiquetado y ensayo. |
| DOE Energy Saver — https://www.energy.gov/energysaver | Metodología de estimación. |
| ENERGY STAR — https://www.energystar.gov/ | Rangos por categoría. |
| UCI — https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption | Serie medida del hogar usada por el TP. |

Cada dato del catálogo debe tener `fuente_id`, fecha de consulta y una nota de qué se extrajo.
Un dato sin fuente no entra; si es un supuesto, se marca como `supuesto` y se muestra en la app.

## Anexo B. Glosario

- **Activo:** energía usada mientras el artefacto funciona.
- **Pasivo / standby:** energía usada con el artefacto enchufado pero sin cumplir su función.
- **Consumo de base:** pasivo de todos los equipos siempre conectados.
- **Ciclo de trabajo:** fracción del tiempo que un equipo funciona (por ejemplo, el compresor
  de la heladera).
- **Tope bonificado:** kWh por mes que reciben el precio subsidiado.
- **Costo efectivo:** costo total dividido por los kWh; incluye cargo fijo e impuestos.
- **Factor mensual:** multiplicador de uso de un artefacto en un mes (0 = no se usa, 1 = uso
  normal).
- **Calibración:** ajuste de la simulación a partir del consumo real de una factura.

## Anexo C. Prompt para implementar el MVP

```text
Implementá la fase 1 y 2 de la propuesta "Propuesta_Simulador_Interactivo.md" en este
repositorio Flask, sin romper la app actual.

Contexto:
- La app existente está en app.py y templates/index.html; usa modelos en modelos/.
- No reentrenar modelos ni agregar base de datos.
- Mantener la estética y el estilo de public/style.css.

Tareas:
1. Crear simulador/calculo.py con funciones puras para:
   - consumo activo y pasivo por artefacto;
   - proyección mensual, estacional y anual;
   - costo por bloques con tope mensual;
   - comparación sin subsidio / tarifa social nacional / tarifa social provincial.
2. Crear simulador/datos/catalogo_electrodomesticos.csv con al menos 12 artefactos y
   simulador/datos/tarifas.json con tres escenarios y valores ilustrativos marcados como
   tales.
3. Agregar la ruta /simulador en app.py y templates/simulador.html.
4. La pantalla debe permitir agregar/quitar artefactos, editar horas conectado, horas en uso,
   días por semana y cantidad; actualizar los totales sin recargar.
5. Mostrar kWh/mes, kWh/año, activo vs. pasivo, costo con y sin subsidio, ahorro y costo
   efectivo.
6. Agregar tests en simulador/tests/test_calculo.py que verifiquen el ejemplo de la sección
   5.2 (enero ≈ 296,4 kWh; año ≈ 2.392,1 kWh) y los tres escenarios tarifarios.
7. Validar entradas y mostrar mensajes claros. No usar datos personales.
8. Documentar en el README cómo levantar la nueva ruta.

Entregá un resumen de archivos creados/modificados y el resultado de los tests.
```
