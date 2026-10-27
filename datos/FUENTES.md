# Fuentes de datos

Cada número que usa la app sale de una de estas fuentes. Si un valor es un supuesto
(no medido ni oficial), se marca como **supuesto**.

Fecha de consulta: 21/10/2026.

---

## 1. Dataset de eficiencia de electrodomésticos (datos reales por modelo)

| | |
|---|---|
| **Nombre** | Energy Rating for Household Appliances — Labelled Products |
| **Publica** | Gobierno de Australia (programa Energy Rating / GEMS), portal oficial de datos abiertos |
| **Página del dataset** | https://data.gov.au/data/dataset/energy-rating-for-household-appliances |
| **API usada para descargar** | https://data.gov.au/data/api/3/action/package_show?id=energy-rating-for-household-appliances |
| **Licencia** | Creative Commons Attribution 3.0 Australia (se puede usar citando la fuente) |
| **Qué es** | Registro de todos los modelos con etiqueta energética que se venden en Australia y Nueva Zelanda. Cada fabricante declara el consumo medido con ensayos normalizados. |
| **Archivo generado** | [`electrodomesticos_eficiencia.csv`](electrodomesticos_eficiencia.csv) (15.342 modelos) |
| **Cómo se generó** | [`preparar_dataset.py`](preparar_dataset.py) — descarga, limpia y clasifica. Se puede volver a ejecutar para actualizarlo. |

Archivos originales usados (CSV, versión del 21/10/2026):

| Archivo | Electrodoméstico | Enlace |
|---|---|---|
| `ac_2026_10_21.csv` | Aires acondicionados | https://data.gov.au/data/dataset/559708e5-480e-4f94-8429-c49571e82761/resource/0973a476-eb0c-45e6-9a18-054f74307843 |
| `rf_2026_10_21.csv` | Heladeras y freezers | https://data.gov.au/data/dataset/559708e5-480e-4f94-8429-c49571e82761/resource/0eabca18-49bb-4a9e-8019-28d5d56501c4 |
| `cw_2026_10_21.csv` | Lavarropas | https://data.gov.au/data/dataset/559708e5-480e-4f94-8429-c49571e82761/resource/eb3b9d8e-f39d-47b7-9db0-309856176951 |
| `cd_2026_10_21.csv` | Secarropas | https://data.gov.au/data/dataset/559708e5-480e-4f94-8429-c49571e82761/resource/f734c56b-a255-4c4e-a3c1-e835c38b8774 |
| `dw_2026_10_21.csv` | Lavavajillas | https://data.gov.au/data/dataset/559708e5-480e-4f94-8429-c49571e82761/resource/cbe7057d-e132-4297-b8be-eecf8322d4e6 |
| `tv_2026_10_21.csv` | Televisores | https://data.gov.au/data/dataset/559708e5-480e-4f94-8429-c49571e82761/resource/93a615e5-935e-4713-a4b0-379e3f6dedc9 |

Cada CSV tiene su diccionario de datos (DOCX) en la misma página del dataset.

### Qué se tomó de cada archivo

| Columna del CSV generado | Columna original | Notas |
|---|---|---|
| `kwh_anio_etiqueta` | `Labelled energy consumption (kWh/year)` | Consumo comparativo de la etiqueta. En heladeras es el consumo de 24 h × 365 días. |
| `potencia_w` (aires) | `C-Power_Inp_Rated` × 1000 | Potencia eléctrica de entrada en frío, a capacidad nominal. |
| `capacidad` (aires) | `C-Total Cool Rated` | kW de frío. `frigorias` = kW × 860. |
| `tecnologia` (aires) | `Is variable speed` | "Yes" = **Inverter**, "No" = **Velocidad fija**. |
| `eer` (aires) | `C-Total Cool Rated / C-Power_Inp_Rated` | Eficiencia en frío (más alto = mejor). |
| `potencia_w` (TV) | `Avg_mode_power` | Potencia media encendida. |
| `capacidad` (TV) | `screensize` ÷ 2,54 | El registro informa la diagonal en cm. |
| `estrellas` | `Star2010_Cool`, `Star2009`, `New Star`, `Star` | Calificación oficial australiana (más estrellas = más eficiente). |
| `standby_w` | `avg_pwr_standby_mode`, `standbyPowerUsage`, `Pasv_stnd_power` | Cuando el fabricante lo informa. |

Filtros: solo registros aprobados; aires split, de ventana y portátiles de hasta 10,5 kW
(el mismo alcance que la norma argentina); se descartan valores imposibles.

### Clase relativa A–G (cálculo propio)

`indice_rel` = consumo del modelo ÷ mediana de su categoría y tamaño (1 = típico; en aires se
usa la mediana de EER ÷ EER del modelo). `clase_rel` divide cada categoría en 7 grupos iguales
(A = el 14 % más eficiente, G = el 14 % menos eficiente).

**No es la etiqueta IRAM argentina.** Es una clase estimada para comparar modelos dentro del
dataset. Las tablas oficiales de clases están en las normas IRAM (ver punto 2).

### Limitaciones

- Son modelos del mercado australiano y neozelandés: muchas marcas coinciden con las de
  Argentina, pero no todos los modelos se venden acá.
- Los diccionarios de datos no indican cuántos usos por año suponen las etiquetas de lavarropas,
  secarropas, lavavajillas y TV. Por eso, de esos equipos no se usa el kWh/año absoluto: los
  lavarropas, secarropas y lavavajillas usan valores típicos, y las TV, la potencia encendida (W).
- La potencia de entrada de los aires es a plena carga. La ventaja del inverter es todavía mayor
  a carga parcial (cuando el ambiente ya está frío), y eso este dato no lo refleja.

---

## 2. Normativa argentina de etiquetado de eficiencia energética

| Fuente | Enlace | Qué se tomó |
|---|---|---|
| Resolución 438/2024 (Secretaría de Industria y Comercio) — texto completo | https://www.argentina.gob.ar/normativa/nacional/norma-406558/texto | Escala de clases A a G (se eliminan A+, A++ y A+++); productos alcanzados; supuestos de cálculo: aires 500 h/año, lavarropas 200 ciclos/año, lavavajillas 280 ciclos/año, TV 4 h/día, microondas 8 min/día. |
| Etiquetado en eficiencia energética — Secretaría de Energía | https://www.argentina.gob.ar/node/169584 | Contexto: normas IRAM por producto y clases mínimas. |
| Resolución 438/2024 — resumen de CIRA | https://www.cira.org.ar/es/servicios/normativas-servicios/resolucion/resolucion-438-2024 | Resumen del alcance. |

Las tablas con los umbrales de cada clase están en las normas IRAM citadas por la resolución
(IRAM 2404-3 heladeras, IRAM 62406 aires, IRAM 2141-3 lavarropas, IRAM 62410 termotanques,
IRAM 62411 televisores, IRAM 2294-3 lavavajillas, IRAM 62412 microondas). Esas normas son
pagas y en la resolución aparecen como imágenes, por eso no se cargaron como datos.

No se encontró un dataset argentino abierto con el consumo por modelo: la Res. 438/2024
prevé una base de datos con la información de fabricantes e importadores, pero no está
publicada en datos abiertos a la fecha de consulta.

---

## 3. Catálogo de electrodomésticos del simulador

Archivo: [`../simulador/datos/datos.json`](../simulador/datos/datos.json)

Potencias, standby y horas de uso por defecto son **valores de arranque (supuestos)** tomados
de la tabla de consumo estándar de la propuesta del proyecto. Cada uno se muestra en la app
como supuesto, con su rango de referencia. Se pueden reemplazar por el dato de la etiqueta.

### Consumo estándar de heladeras y freezers por tamaño

En *Mi casa*, la heladera y el freezer preguntan el **tamaño** en lugar del dato de la etiqueta.
Cada tamaño usa un **valor estándar**: la **mediana** del consumo de etiqueta (`kwh_anio_etiqueta`)
de los modelos reales del dataset del punto 1, agrupados por capacidad (`capacidad`, en litros) y
redondeada a 10 kWh. Para las heladeras se toman solo los modelos *Refrigerator/Freezer*
(heladera con freezer).

| Equipo | Tamaño | Litros | kWh por año | Modelos |
|---|---|---|---:|---:|
| Heladera con freezer | Chica | hasta 300 | 240 | 442 |
| Heladera con freezer | Mediana | 300 a 450 | 320 | 688 |
| Heladera con freezer | Grande | más de 450 | 410 | 866 |
| Freezer | Chico | hasta 200 | 200 | 305 |
| Freezer | Mediano | 200 a 350 | 260 | 230 |
| Freezer | Grande | más de 350 | 370 | 212 |

El catálogo arranca con el tamaño mediano (320 y 260 kWh por año). El perfil «Ejemplo de la
propuesta» mantiene 350 kWh por año, que es el valor de su ejemplo verificado.
Limitación: son modelos ensayados con la norma de Australia y Nueva Zelanda, no con la IRAM 2404-3.

### Variantes de cada electrodoméstico (nombre desplegable)

En cada tarjeta, el nombre es un desplegable con las variantes más comunes
([`../simulador/variantes.py`](../simulador/variantes.py)). Origen de cada valor:

| Equipo | Variantes | Valor | Fuente |
|---|---|---|---|
| Heladera / freezer | Chica · mediana · grande | kWh por año | Mediana del dataset del punto 1 (tabla de arriba) |
| Aire split | 2.250 · 3.000 · 4.500 · 6.000 frigorías | Potencia de entrada (W) | Mediana del dataset del punto 1: aires *Split* con frigorías dentro de ±15 % (352, 335, 622 y 769 modelos) |
| TV | 32" · 43" · 50" · 55" · 65" | Potencia encendida (W) y standby | Mediana del dataset del punto 1: TV de ±1 pulgada (294, 406, 429, 778 y 867 modelos) |
| Termotanque, lavarropas, secarropas, lavavajillas, microondas, horno, calefactor, ventilador, notebook, PC, lámparas, bomba | 2 o 3 tamaños | W o kWh por ciclo | **Valor típico (supuesto)**: tabla de consumo estándar de la propuesta o potencia nominal habitual. Bomba: ½ HP = 370 W, ¾ HP = 550 W, 1 HP = 750 W |

Los aires del dataset son casi todos inverter y su potencia es a plena carga: un aire común
(velocidad fija) del mercado argentino puede consumir más.

---

## 4. Tarifas de EDEA (cuadro tarifario oficial)

Archivos: [`tarifas_edea.csv`](tarifas_edea.csv) (30 filas: 4 situaciones × tramos) e
[`impuestos_residenciales.csv`](impuestos_residenciales.csv), generados por
[`preparar_tarifas.py`](preparar_tarifas.py) a partir de los PDF oficiales.

| | |
|---|---|
| **Norma** | Resolución MIySP N° 682/2026 de la Provincia de Buenos Aires (Boletín Oficial del 31/08/2026) — https://oceba.gba.gov.ar/nueva_web/adjuntos/ct202609/Reso_682_26.pdf |
| **Publica** | OCEBA (Organismo de Control de Energía Eléctrica de la Provincia de Buenos Aires) — https://oceba.gba.gov.ar/nueva_web/s.php?i=17 |
| **Vigencia** | Consumos a partir del 1° de septiembre de 2026 (cuadros "vigentes" en la página del OCEBA al 21/10/2026) |
| **Categoría** | T1R — Residencial (menos de 10 kW) |

| Situación en la app | Anexo oficial | PDF |
|---|---|---|
| Sin subsidio | Anexo 44 — Demanda residencial | https://oceba.gba.gov.ar/nueva_web/adjuntos/ct202609/IF-2026-27778457-GDEBA-GMOCEBA.pdf |
| Con subsidio nacional (SEF) | Anexo 52 — Residencial hasta 150 kWh/mes beneficiaria del SEF (+ Anexo 44 para el excedente) | https://oceba.gba.gov.ar/nueva_web/adjuntos/ct202609/IF-2026-27784547-GDEBA-GMOCEBA.pdf |
| Tarifa social provincial | Anexo 60 — Tarifa Social Grupo 1 (incluye la bonificación fija) | https://oceba.gba.gov.ar/nueva_web/adjuntos/ct202609/IF-2026-27787960-GDEBA-GMOCEBA.pdf |
| Tarifa social + SEF | Anexo 68 — Tarifa Social Grupo 1 y beneficiaria del SEF | https://oceba.gba.gov.ar/nueva_web/adjuntos/ct202609/IF-2026-27790623-GDEBA-GMOCEBA.pdf |
| Cargo Transición Tarifaria | Anexo 87 — CTT ($/kWh) | https://oceba.gba.gov.ar/nueva_web/adjuntos/ct202609/IF-2026-27797883-GDEBA-GMOCEBA.pdf |
| Impuestos | Tabla "Impuestos y FPCT" del OCEBA (revisada el 31/01/2026) | https://oceba.gba.gov.ar/nueva_web/s.php?i=19 |

**Cómo se calcula la factura** (igual que en el CSV):
1. El **tramo** (R1 a R7) se elige por el consumo total del mes.
2. Cargo fijo del tramo + kWh × precio del tramo.
3. **SEF:** los primeros 150 kWh van al precio del Anexo 52; el resto, al precio pleno del Anexo 44
   (nota (1) y (2) del Anexo 87). **Tarifa social:** desde 150 kWh, los primeros 150 van al precio
   "primeros 150" del anexo y el resto al precio del tramo; se resta la bonificación fija.
4. + Cargo Transición Tarifaria: 17,506 $/kWh (residencial), 7,445 $/kWh (primeros 150 kWh SEF),
   2,987 $/kWh (tarifa social).
5. + Impuestos sobre el subtotal: 36,501 % (residencial) o 32,511 % (tarifa social, que paga 0,01 %
   del Decreto-Ley 7290 en lugar del 4 %, Res. MIySP 771/24 art. 52).

**Simplificaciones (declaradas):**
- Todos los impuestos se aplican sobre el mismo subtotal; en la factura real algunas bases pueden
  diferir y la tasa municipal (Ley 11769 art. 75) depende del municipio.
- No incluye otros conceptos que pueden aparecer en la factura (tasas municipales de alumbrado,
  intereses, cargos de reconexión).
- La tarifa social modelada es la del **Grupo 1**.
- El bloque subsidiado del SEF puede cambiar mes a mes por resolución de la Secretaría de Energía
  de la Nación; el valor cargado (150 kWh) es el de los anexos vigentes del OCEBA.

Para actualizar cuando salga un cuadro nuevo: cambiar las URLs en `preparar_tarifas.py` y ejecutar
`python datos/preparar_tarifas.py`.

El esquema de la sección 6.3 de la propuesta (precio pleno + tope bonificado) queda solo como
ejemplo en `simulador/datos/datos.json` y en las pruebas; la app usa el cuadro real.

---

## 5. Datos del modelo de aprendizaje automático del TP

| Fuente | Enlace |
|---|---|
| UCI — Individual Household Electric Power Consumption (hogar de Sceaux, Francia, 2006–2010) | https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption |
| `clima_sceaux.csv` (temperatura diaria 2006–2011 del mismo lugar, en la carpeta del proyecto) | Open-Meteo Historical Weather API — https://open-meteo.com/ (punto lat 48,78, lon 2,29) |
| `modelos/reg_24h.pkl` y `modelos/clf_me_paso.pkl` (Pipelines entrenados) | Notebook del trabajo, entrenado con los dos datos de arriba. Métricas y preparación: [`../README_ANALISIS.md`](../explicaciones/README_ANALISIS.md) |
