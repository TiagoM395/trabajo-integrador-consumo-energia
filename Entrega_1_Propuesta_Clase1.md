# Trabajo Práctico Integrador - Aprendizaje Automático
**Entrega 1 - Clase 1: Investigación y Propuesta**

## Datos del Trabajo

| Campo | Respuesta |
|---|---|
| Integrantes | Bulggiani - Campos - Guzman - Maidana |
| Curso | 2do año |
| Fecha de inicio | 13/10/2026 |
| Fecha de entrega 1 | 15/10/2026 |
| Fecha de actualización | 16/10/2026 (revisión de la propuesta elegida) |

---

## 3.1 Clase 1: Investigación y Propuesta

### Alternativa 1: Asistente de consumo eléctrico del hogar (OPCIÓN ELEGIDA)

| Campo | Respuesta del grupo |
|---|---|
| **Nombre del proyecto** | "¿Me paso o no me paso?": asistente para anticipar el consumo eléctrico de las próximas 24 h y el riesgo de recargo por factor de potencia en un hogar con medidor inteligente. |
| **Problema** | El usuario residencial consume a ciegas: conoce su consumo recién cuando llega la factura, cuando ya no puede corregir nada. Pasarse de su meta, del bloque subsidiado o tener el coseno φ bajo encarecen la factura. |
| **Usuario de la predicción** | El titular del hogar, a través de una aplicación web. |
| **Momento de la predicción** | Cualquier hora del día, cuando el usuario abre la app. Usa todo lo medido hasta ese instante y estima las **24 horas siguientes**. |
| **Decisión que permitirá tomar** | Si la alerta da "te pasás": reducir o postergar lavarropas, secarropas, lavavajillas, termotanque, calefacción y aire. Si el cos φ está en zona de recargo: revisar los artefactos con motores o compresores y evaluar un capacitor. |
| **Variable numérica** | Energía activa consumida en las **próximas 24 h** (kWh). |
| **Umbral y justificación** | **Meta diaria** = consumo diario promedio del **conjunto de entrenamiento**. Justificación desde el usuario: su criterio natural es su propia meta (ahorro, presupuesto o bloque subsidiado). Se calcula solo con entrenamiento (regla 5) y queda fija. Alerta: "en las próximas 24 h vas a consumir más que en tu día típico". |
| **Variable binaria** | `me_paso = 1` si el consumo de las próximas 24 h supera la meta diaria; `0` si no. |
| **Indicador complementario (no es modelo)** | Coseno φ de las últimas 24 h (medido) y su franja de recargo según Res. ENRE 85/2024. No es el objetivo: entra como predictor, como indicador en la app y en el esquema de costos. |
| **Fuente de datos** | [UCI - Individual Household Electric Power Consumption](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption) (CC BY 4.0) + [Open-Meteo Historical Weather API](https://open-meteo.com/) para la temperatura de la misma ubicación. |
| **Cantidad de observaciones** | ~2.075.259 mediciones por minuto (dic. 2006 - nov. 2010). Al agregar por hora quedan ~34.500 filas; al agregar por día, ~1.400. En todos los casos se supera el mínimo de 2.000 registros. |
| **Variables disponibles al momento de predecir** | **Medidor:** energía activa de la última hora y de las últimas 24 h; energía activa de las mismas 24 h de la semana anterior; energía reactiva de las últimas 24 h; coseno φ de las últimas 24 h; voltaje promedio; energía de las últimas 24 h por submedidor (cocina, lavadero, termotanque/aire). **Calendario:** hora, día de la semana, mes, fin de semana o feriado. **Clima:** temperatura actual y prevista. |
| **Posibles fugas** | Potencia, reactiva, intensidad y submedidores de horas **futuras** (son el objetivo). `Global_intensity` como atajo (= potencia / voltaje, objetivo disfrazado). Fecha como número continuo (no generaliza). **Ventanas superpuestas:** la consulta de las 19:00 y la de las 20:00 comparten 23 de 24 horas, por lo que se exige **separación cronológica** (no split al azar) con un día de hueco. El umbral se calcula solo con entrenamiento. Escalado dentro del Pipeline. |
| **Riesgos y limitaciones** | Un solo hogar (Sceaux, Francia 2006-2010): no generaliza a otro hogar sin reentrenar. Otro clima, artefactos y tarifas. Muy pocos eneros completos para el módulo estacional. La temperatura se usa como valor real (simplificación declarada). Cambios de hábito (concept drift) y vacaciones generan falsos positivos (errores baratos). Faltantes ~1,25% con días enteros sin medir. |

---

### Alternativa 2: Calidad del aire en Buenos Aires

| Campo | Respuesta del grupo |
|---|---|
| **Nombre del proyecto** | Predicción de PM10 y alerta de calidad del aire para actividades al aire libre. |
| **Problema** | El material particulado (PM10) afecta a personas con asma, niños y adultos mayores. Es necesario anticipar si el nivel de partículas será elevado para tomar decisiones preventivas. |
| **Usuario de la predicción** | Escuelas, clubes deportivos y personas con enfermedades respiratorias. |
| **Decisión que permitirá tomar** | Al final del día anterior, decidir si se **suspenden las actividades físicas al aire libre** para el día siguiente. |
| **Variable numérica** | PM10 promedio del día siguiente, en µg/m³. |
| **Umbral y justificación** | **45 µg/m³**, basado en la guía 24 hs de la **OMS (2021)** para PM10. Es justificable desde el punto de vista sanitario. |
| **Variable binaria** | `aire_no_saludable = 1` si PM10 promedio del día siguiente > 45 µg/m³, caso contrario 0. |
| **Fuente de datos** | Dataset "Calidad del aire" de la Agencia de Protección Ambiental de la Ciudad de Buenos Aires ([data.buenosaires.gob.ar](https://data.buenosaires.gob.ar/)), cruzado con datos climáticos de [Open-Meteo](https://open-meteo.com/). |
| **Cantidad de observaciones** | Varios miles de registros diarios, considerando **3 estaciones** (La Boca, Córdoba y Parque Centenario) y varios años. Supera el mínimo requerido (≥2.000). |
| **Variables disponibles** | PM10, NO₂ y CO del día actual; estación de medición; día de la semana; mes; variables climáticas (viento, lluvia, humedad). |
| **Posibles fugas** | No se deben incluir mediciones del **mismo día** que se quiere predecir. Solo información disponible al momento de la predicción (día anterior y anteriores). |
| **Riesgos y limitaciones** | Datos con faltantes y posibles valores atípicos. Corresponde a CABA (no a Chascomús). No captura eventos puntuales (incendios, obras) no registrados. |

---

### Alternativa 3: Agricultura de Precisión (Rendimiento de Cultivos)

| Campo | Respuesta del grupo |
|---|---|
| **Nombre del proyecto** | Predicción de rendimiento agrícola y alerta temprana de cosecha insuficiente. |
| **Problema** | Los productores necesitan estimar el rendimiento con anticipación para planificar logística y gestión financiera. Un rendimiento bajo genera pérdidas no presupuestadas. |
| **Usuario de la predicción** | Productor agrícola o asesor agronómico de la región pampeana. |
| **Decisión que permitirá tomar** | Contratar seguro agrícola adicional, ajustar fertilizantes de cobertura o planificar la venta futura del grano. |
| **Variable numérica** | Rendimiento estimado en toneladas por hectárea (ton/ha). |
| **Umbral y justificación** | **< 3,0 ton/ha** (para soja/maíz). Por debajo de este valor se entra en zona de no rentabilidad según costos operativos de la región. |
| **Variable binaria** | `rendimiento_insuficiente = 1` si rendimiento < 3,0 ton/ha, 0 caso contrario. |
| **Fuente de datos** | [Kaggle - Crop Yield Prediction Dataset](https://www.kaggle.com/datasets). |
| **Cantidad de observaciones** | ~3.500 – 5.000 registros. Cumple con el mínimo requerido. |
| **Variables disponibles** | Precipitaciones acumuladas (mm), temperatura media (°C), tipo de suelo (codificado), fertilizante aplicado (kg/ha), tamaño del lote (ha), cultivo anterior (rotación). |
| **Posibles fugas** | Precio final de venta, costo total de producción y, obviamente, el rendimiento real. |
| **Riesgos y limitaciones** | No captura plagas repentinas ni granizo no registrado. Asume prácticas de siembra estándar para la zona. |

---

## Comparación entre alternativas

| Criterio | Alt. 1: Consumo Eléctrico | Alt. 2: Calidad del Aire | Alt. 3: Agricultura |
|---|---|---|---|
| **Cumplimiento ≥2000 registros** | **Excelente** (~34.500 horarios). | Bueno (miles). | Bueno (~3.5k–5k). |
| **Preparación de datos (pide consigna)** | **Muy adecuada** (agregación, faltantes, fechas, energía reactiva). | Adecuada (faltantes). | Adecuada. |
| **Justificación de umbral** | Justificable desde el usuario (meta diaria). | Muy clara (OMS). | Justificada (rentabilidad). |
| **Disponibilidad de variables predictoras (≥5)** | Sí (16 predictoras). | Sí. | Sí. |
| **Reproducibilidad y origen claro** | **Excelente** (UCI + Open-Meteo, bien documentado). | Bueno (Buenos Aires). | Bueno (Kaggle). |
| **Ajuste a Regresión + Clasificación (comparación)** | **Óptimo** (relación directa kWh 24 h vs alerta). | Adecuado. | Adecuado. |

---

## Proyecto seleccionado

**Alternativa 1: Asistente de consumo eléctrico del hogar.**

**Justificación de elección:** es la que mejor se ajusta a los requisitos de la consigna. Permite trabajar la **agregación temporal**, el **feature engineering** (energía, cos φ, calendario, clima), la **justificación del umbral** desde el usuario y la **comparación obligatoria** (clasificador directo vs regresión + umbral), además de sumar un **esquema de costos** con significados claros para falsos positivos y falsos negativos. El dataset es público, documentado y de tamaño suficiente.

---

## Bitácora de decisiones (Clase 1)

| Fecha | Decisión | Alternativas | Justificación | Resultado |
|---|---|---|---|---|
| 15/10/2026 | Seleccionar el proyecto de consumo eléctrico | Alt.1, Alt.2, Alt.3 | Mejor ajuste a requisitos, dataset sólido y justificación del umbral con datos. | Aprobada para continuar. |
| 15/10/2026 | Definir granularidad horaria para la tarea principal | Agregación diaria (~1.400) vs horaria (~34.500) | La diaria no alcanza variedad de casos; la horaria da un momento de consulta por fila. | Definido trabajo por hora. |
| 16/10/2026 | **Revisar el proyecto elegido** | Propuesta inicial (usuario = distribuidora, umbral = percentil 75, kWh/h) vs `trabajo.md` (usuario = titular, umbral = meta diaria, kWh/24 h) | Se reescribe el proyecto desde el usuario final. El umbral como meta diaria permite un esquema de costos realista (FN cuesta plata, FP cuesta comodidad) y habilita el indicador de coseno φ y el comparador estacional. La versión anterior (percentil 75 para la distribuidora) se descarta. | Propuesta actualizada; se continúa con la versión del usuario. |

---

**Nota:** Se continúa únicamente con el proyecto aprobado (Alternativa 1), conforme al punto 3.1.

**Proyecto complementario agregado (Clase 2 en adelante):** comparador estacional que compara el gasto del mes de **enero** de los últimos años y estima el enero siguiente. Se documenta como tarea complementaria para no alterar las dos tareas obligatorias (regresión y clasificación).
