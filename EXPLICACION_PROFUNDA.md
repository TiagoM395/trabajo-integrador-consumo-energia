# ⚡ ¿Me paso o no me paso?

Aplicación web en **Python + Streamlit** para armar tu casa electrodoméstico por electrodoméstico,
ver **cuánta electricidad gastás y cuánto pagás** con la factura de EDEA, y **predecir si mañana
te pasás de la meta diaria** con los dos modelos de aprendizaje automático del trabajo (regresión y
clasificación). También lee la **factura de luz** (PDF o foto, también con la cámara del celular).

> **Cómo ejecutarla:** [`EJECUTAR.md`](EJECUTAR.md) (guía completa) o [`EJECUTAR_ELIAS.md`](EJECUTAR_ELIAS.md) (paso a paso en esta PC).
> **De dónde salen los datos:** [`datos/FUENTES.md`](datos/FUENTES.md).
> **Qué falta hacer:** [`README_PENDIENTES.md`](README_PENDIENTES.md).

---

## 1. Qué problema resuelve

La factura de luz trae un solo número: los kWh del período. No dice **qué** electrodoméstico
consumió, **cuánto** cuesta cada uno, ni si **mañana** vas a pasarte de lo que querés gastar.
La app responde:

- ¿Cuánto consume cada electrodoméstico por mes, y cuánto suma a la factura?
- ¿Cuánto es consumo **en uso** y cuánto **en espera** (standby y equipos siempre enchufados)?
- ¿Cuánto pago **sin subsidio**, con **subsidio nacional (SEF)**, con **tarifa social provincial** o con las dos?
- ¿**Mañana me paso** de la meta diaria? Lo responden dos modelos: regresión + meta y clasificador directo.
- ¿Se parece lo que armé a mi factura real?

---

## 2. Las pestañas

Arriba hay un **navbar fijo** con el nombre de la app a la izquierda y las pestañas al centro,
siempre visibles (también en el celular). No hay barra lateral.

| Pestaña | Qué hace | Detalle |
|---|---|---|
| 🏠 **Mi casa** | Cuatro pasos de arriba hacia abajo: **1** tu situación (subsidio, consumo de base, reiniciar) · **2** armá tu casa (perfiles y electrodomésticos) · **3** lo que gastás por mes (**cálculo**) · **4** ¿mañana te pasás de la meta? (**predicción** con los modelos) | [`README_MI_CASA.md`](explicaciones/README_MI_CASA.md) · paso 4: [`README_PREDICCION.md`](explicaciones/README_PREDICCION.md) |
| 🧊 **Ambiente 3D** | La misma casa dibujada en tres ambientes: se arrastran muebles y electrodomésticos, cada uno muestra su consumo y el botón ▶ simula un día | [`README_AMBIENTE_3D.md`](explicaciones/README_AMBIENTE_3D.md) |
| 🧾 **Factura** | Escanea la factura (PDF, foto o cámara): consumo, período, importe, vencimiento, subsidio y QR. Calibra la simulación con el consumo real | [`README_FACTURA.md`](explicaciones/README_FACTURA.md) |
| 🔬 **Análisis** | El trabajo con el dataset y los modelos, paso a paso: datos, variables, ajustes para Argentina, separación, baselines, métricas, comparación de alertas, errores y limitaciones | [`README_ANALISIS.md`](explicaciones/README_ANALISIS.md) |

Los dos modelos de aprendizaje automático del paso 4 tienen su propio README:

| Modelo | Archivo | Explicación detallada |
|---|---|---|
| **Regresión** (KNN k=25): cuántos kWh vas a usar en las próximas 24 h | [`modelos/reg_24h.pkl`](modelos/reg_24h.pkl) | [`README_MODELO_REGRESION.md`](explicaciones/README_MODELO_REGRESION.md) |
| **Clasificación** (GaussianNB): ¿te pasás de la meta, sí o no? | [`modelos/clf_me_paso.pkl`](modelos/clf_me_paso.pkl) | [`README_MODELO_CLASIFICACION.md`](explicaciones/README_MODELO_CLASIFICACION.md) |

Arriba de *Mi casa*, *Ambiente 3D* y *Factura* aparece el recuadro **Resumen de tu casa**: consumo
del mes, lo que pagarías, el ahorro con subsidio y el consumo en espera.

### Las tarjetas de cada electrodoméstico

- El **nombre es un desplegable** con las variantes más comunes (TV 32" a 65", aire 2.250 a 6.000
  frigorías, heladera chica, mediana o grande…). Al elegir una se carga su **valor estándar** y la
  tarjeta dice de dónde sale.
- Una sola pregunta según el equipo: **horas por día** (de a 30 minutos, con 15 minutos al
  principio), **veces por semana** (lavarropas y similares) o ninguna (heladera y freezer, que
  están prendidos las 24 horas).
- El botón **ⓘ** explica los kWh y la plata de ese electrodoméstico con sus propios números.

---

## 3. Cómo calcula y cómo predice

**Cálculo (pasos 1 a 3 de Mi casa).** Una cuenta, sin aprendizaje automático, en
[`simulador/calculo.py`](simulador/calculo.py). Calcula **un mes de 30 días**:

| Modo | Equipos | kWh por mes |
|---|---|---|
| Por horas | TV, aire, luces, termotanque… | potencia × horas de uso × días + standby × horas enchufado sin usar |
| Por ciclos | Lavarropas, secarropas, lavavajillas | kWh por uso × veces por semana ÷ 7 × 30 |
| Etiqueta anual | Heladera, freezer | kWh por año × 30 ÷ 365 |
| Siempre encendido | Router | potencia × 24 h × 30 |

La **factura** se arma con el cuadro tarifario oficial de EDEA (tramos R1 a R7, cargo fijo, Cargo
Transición Tarifaria e impuestos). El subsidio cambia el **precio**, no los kWh. La plata de cada
electrodoméstico es su parte de la factura: kWh del equipo × (total de la factura ÷ kWh de la casa).

**Predicción (paso 4 de Mi casa).** La app **carga** los modelos ya entrenados (no entrena nada) y
arma sus 16 variables con lo que cargaste en la casa o en la factura:

| Modelo | Qué responde | Resultado en prueba |
|---|---|---|
| Regresión: KNN k=25 (StandardScaler en un Pipeline) | ¿Cuántos kWh vas a usar en las próximas 24 h? | MAE 4,57 kWh · R² 0,31 |
| Clasificación: GaussianNB | ¿Te pasás de la meta diaria (25,9 kWh)? | Accuracy 0,74 · Recall 0,63 |

El resultado es un semáforo: 🟢 no te pasás · 🟡 estás cerca o los modelos no se ponen de acuerdo
· 🔴 te pasás. Cómo se prepararon los datos y se entrenaron los modelos está en la pestaña
*Análisis* ([`README_ANALISIS.md`](explicaciones/README_ANALISIS.md)).

---

## 4. Datos

| Archivo | Qué tiene | Fuente |
|---|---|---|
| [`simulador/datos/datos.json`](simulador/datos/datos.json) | Catálogo de 26 electrodomésticos, perfiles (ejemplo de la propuesta, 1 persona, pareja, familia) y muebles del 3D | Valores típicos de la propuesta y valores estándar de [`simulador/variantes.py`](simulador/variantes.py) |
| [`simulador/variantes.py`](simulador/variantes.py) | Variantes de cada electrodoméstico y su valor estándar | Mediana de modelos reales del dataset de eficiencia (heladera, freezer, aire, TV) o valor típico (el resto) |
| [`datos/tarifas_edea.csv`](datos/tarifas_edea.csv) y [`datos/impuestos_residenciales.csv`](datos/impuestos_residenciales.csv) | Cuadro tarifario residencial oficial de EDEA e impuestos | [OCEBA — Res. MIySP 682/2026](https://oceba.gba.gov.ar/nueva_web/s.php?i=17) |
| [`datos/electrodomesticos_eficiencia.csv`](datos/electrodomesticos_eficiencia.csv) | 15.342 modelos reales con su consumo de etiqueta | [data.gov.au — Energy Rating](https://data.gov.au/data/dataset/energy-rating-for-household-appliances) (CC BY 3.0 AU) |
| [`modelos/`](modelos/) | Pipelines entrenados de regresión y clasificación | Dataset UCI *Individual Household Electric Power Consumption* (CC BY 4.0) |
| [`clima_sceaux.csv`](clima_sceaux.csv) | Temperatura diaria 2006–2011 del hogar del dataset (Sceaux, Francia) | Open-Meteo, usada para entrenar los modelos |

Todas las fuentes, con enlaces, columnas usadas y limitaciones: [`datos/FUENTES.md`](datos/FUENTES.md).

---

## 5. Estructura del proyecto

```
streamlit_app.py              ← punto de entrada: navbar, navegación y resumen de la casa
app_pages/
  casa.py                     ← Mi casa (pasos 1 a 4)
  ambiente.py                 ← Ambiente 3D
  factura.py                  ← Factura (escaneo y calibración)
  analisis.py                 ← Análisis (muestra explicaciones/README_ANALISIS.md)
  dia.py, tarifas.py,
  eficiencia.py, referencias.py ← pantallas anteriores, fuera del menú
simulador/
  calculo.py                  ← motor de cálculo (funciones puras)
  estado.py                   ← estado de la sesión, perfiles y ubicación en el ambiente
  ui.py                       ← navbar, estilos, resumen, tarjetas, catálogo y consejos
  variantes.py                ← variantes de cada electrodoméstico y su valor estándar
  prediccion.py               ← carga de los modelos y armado de las 16 variables
  vista_prediccion.py         ← paso 4 de Mi casa en pantalla
  factura.py                  ← lectura de la factura (PDF, OCR, QR) y extracción de datos
  graficos.py                 ← gráficos Plotly
  guardado.py                 ← guarda la casa (sesiones/<código>.json) para no perderla al recargar
  escena.py, componentes/     ← Ambiente 3D (componente de Streamlit, JS y CSS)
  datos/datos.json            ← catálogo, perfiles y muebles
modelos/                      ← reg_24h.pkl y clf_me_paso.pkl
explicaciones/                ← un README detallado por pestaña y por modelo
datos/                        ← tarifas, impuestos, dataset de eficiencia, scripts y FUENTES.md
tests/
  test_calculo.py             ← pruebas del cálculo y de la factura de EDEA
  test_factura.py             ← pruebas de la lectura de facturas (texto, QR y subsidio)
.streamlit/config.toml        ← tema claro/oscuro y límite de subida de 10 MB
requirements.txt              ← paquetes de Python con versiones
packages.txt                  ← Tesseract con español, para Streamlit Community Cloud
abrir_simulador.bat           ← abre la app con doble clic (Windows)
```

---

## 6. Tecnologías

| Para qué | Qué |
|---|---|
| Aplicación web | Streamlit 1.57 (páginas múltiples, navbar propio, diálogos, componentes v2) |
| Modelos | scikit-learn 1.8 y joblib (solo `predict`, sin entrenar) |
| Datos y gráficos | pandas, numpy y Plotly |
| Ambiente 3D | SVG isométrico propio en JavaScript, conectado con Streamlit Components v2 |
| Factura en PDF | pypdf |
| Factura en foto | Tesseract OCR (pytesseract) + Pillow |
| Códigos QR y de barras | zxing-cpp |

---

## 7. Verificación

19 pruebas automáticas (`python -m unittest discover -s tests -v`), entre ellas los ejemplos de la
propuesta:

| Ejemplo | Esperado | Resultado |
|---|---|---|
| 5.2 — enero (4 electrodomésticos) | 296,4 kWh | 296,4 kWh ✅ |
| 5.2 — año | 2.392,1 kWh | 2.392,1 kWh ✅ |
| 6.3 — 400 kWh sin subsidio / nacional / provincial | $ 78.650 / 53.240 / 45.617 | iguales ✅ |
| Factura de EDEA, 273 kWh sin subsidio | $ 103.118 (cuenta a mano) | igual ✅ |

---

## 8. Limitaciones

- **Horas de uso y valores típicos:** el cálculo depende de lo que se carga. Para comparar con la
  realidad está la factura.
- **Modelos:** aprendieron de **un solo hogar** (Sceaux, Francia, 2006–2010). La meta de 25,9 kWh
  por día es alta para muchos hogares de acá. Algunos datos que piden los modelos (voltaje, energía
  reactiva, consumo de la semana anterior) se completan con valores típicos; están listados en
  *Análisis*, sección 3.
- **Tarifas:** cuadro oficial de EDEA para consumos desde el 1/9/2026. Cuando salga uno nuevo, se
  regeneran con `python datos/preparar_tarifas.py`.
- **Valores estándar:** los de heladera, freezer, aire y TV vienen del registro de Australia y Nueva
  Zelanda, no de etiquetas IRAM argentinas.
- **Fotos de facturas:** el OCR puede fallar con fotos borrosas, torcidas o con sombras. Siempre se
  confirman los datos; el PDF digital es lo más preciso.
- **Sin base de datos:** todo vive en la sesión del navegador; al cerrar la pestaña se pierde.


# EXPLICACIÓN A PROFUNDIDAD (NARRATIVA)

## 1) Objetivo del proyecto
"¿Me paso o no me paso?" es una app web (Streamlit) que permite armar la casa electrodoméstico por electrodoméstico, calcular consumo mensual y costo con la factura de EDEA (con/sin subsidios), y predecir si mañana se va a superar una meta diaria usando dos modelos de ML ya entrenados (regresión + clasificación). También permite escanear/leer la factura (PDF/foto/cámara) para calibrar con consumo real, y visualizar la casa en ambiente 3D.

## 2) Arquitectura general
- Entrada: streamlit_app.py configura la app, inicializa estado (simulador/estado.py), restaura sesión guardada (simulador/guardado.py), aplica estilos y navbar propio (simulador/ui.py), navega por páginas ocultas con st.navigation y muestra resumen con ui.hero. Guarda al final con G.guardar().
- Páginas: app_pages/casa.py (4 pasos), app_pages/ambiente.py (3D), app_pages/factura.py (escaneo), app_pages/analisis.py (explicación del trabajo con dataset/modelos).
- Motor de cálculo: simulador/calculo.py funciones puras para consumo por mes (30 días) y facturación EDEA con subsidios/impuestos.
- Predicción: simulador/prediccion.py carga modelos/reg_24h.pkl y modelos/clf_me_paso.pkl (pipelines con StandardScaler/transformaciones), arma 16 features.
- Datos/catálogo: simulador/datos/datos.json, simulador/variantes.py (valores estándar). Tarifas/impuestos en datos/. Modelos en modelos/. Clima en clima_sceaux.csv.

## 3) Flujo de ejecución
1. st.set_page_config (ancho completo). 2. E.iniciar() inicializa session_state. 3. G.restaurar() lee código guardado en URL/estado y reconstruye casa. 4. E.sincronizar() asegura coherencia. 5. ui.estilos() CSS. 6. Navbar propio + navegación oculta. 7. Se ejecuta página seleccionada. 8. Si no es "Análisis", muestra ui.hero(E.resultados()) (resumen). 9. G.guardar() persiste estado.

## 4) Motor de cálculo (simulador/calculo.py)
Calcula mes de 30 días. Modos:
- Por horas: potencia(kW)*horas_uso*30 + potencia_standby(kW)*horas_enchufado_sin_uso*30
- Por ciclos/veces: kWh_por_uso*(veces_semana/7)*30
- Etiqueta anual (heladera, freezer): kWh_anual/365*30
- Siempre encendido (router): potencia*24*30

Facturación EDEA: tramos R1-R7, cargo fijo, Cargo Transición Tarifaria, impuestos (datos/tarifas_edea.csv, datos/impuestos_residenciales.csv). El subsidio modifica precio, no kWh. Costo por electrodoméstico: kWh_equip*(total_factura/kWh_casa).

## 5) Estado y datos
- estado.py: gestiona session_state (perfil, electrodomésticos, subsidios/base, ambiente, factura).
- datos.json: 26 electrodomésticos, perfiles ejemplo, muebles 3D.
- variantes.py: variantes con valor estándar (heladera/freezer/aire/TV basados en dataset eficiencia Australia/NZ).
- guardado.py: serializa casa a JSON/URL para restaurar.

## 6) Predicción (paso 4 Mi casa)
Carga modelos entrenados (solo predict):
- Regresión reg_24h.pkl (KNN k=25, StandardScaler): predice kWh próximos 24h. MAE 4,57 kWh, R² 0,31.
- Clasificación clf_me_paso.pkl (GaussianNB): ¿me paso de meta diaria (25,9 kWh)? Accuracy 0,74, Recall 0,63.

Arma 16 variables combinando casa/factura con valores típicos cuando faltan. Semáforo verde/amarillo/rojo según acuerdo y cercanía.

## 7) Páginas
- casa.py: 1) Situación 2) Armá tu casa 3) Lo que gastás por mes 4) ¿Mañana me paso de la meta? (vista_prediccion.py)
- factura.py: PDF/foto/cámara. pypdf + pytesseract + Pillow + zxing-cpp. Extrae datos y permite calibrar.
- ambiente.py: SVG isométrico propio + JS (simulador/escena.py/componentes/). Arrastrar, consumo, simular día.
- analisis.py: explicación dataset/modelos.

## 8) UI y utilidades
- ui.py: navbar fijo, estilos, hero() resumen, tarjetas with variantes+info+inputs.
- guardado.py: persistencia.
- graficos.py: gráficos Plotly.

## 9) Datos, fuentes y modelos
- Tarifas OCEBA Res. MIySP 682/2026. Regenerar con datos/preparar_tarifas.py.
- Eficiencia data.gov.au Energy Rating (CC BY 3.0 AU).
- Modelos UCI Individual Household Electric Power Consumption (CC BY 4.0), clima_sceaux.csv Open-Meteo.

## 10) Limitaciones
- Modelos de un solo hogar francés 2006-2010; meta 25,9 kWh/día alta para muchos hogares AR.
- Algunos features con valores típicos.
- Valores estándar heladera/freezer/aire/TV de Australia/NZ (no IRAM AR).
- OCR puede fallar con fotos malas; PDF digital más preciso.
- Sin BD (sesión/navegador).
- Tarifas vigentes desde 1/9/2026.

## 11) Verificación y ejecución
- Tests: tests/test_calculo.py, tests/test_factura.py (19 pruebas). python -m unittest discover -s tests -v.
- Ejecución: streamlit run streamlit_app.py o abrir_simulador.bat. requirements.txt + packages.txt (Tesseract).

## 12) Para qué sirve
Conciencia de consumo/costo con/sin subsidio, alerta anticipada (¿me paso mañana?), validación con factura real, visualización 3D. Herramienta educativa/analítica para entender desglose y impacto tarifario EDEA (Argentina).
