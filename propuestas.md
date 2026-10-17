Opciones para el trabajo de aprendizaje automatico 



📌 Opción 1: Agricultura de Precisión (Rendimiento de Cultivos)
Ideal para el cinturón agrícola de Dolores, Lezama y Pila.

Campo
Respuesta del grupo
Integrantes
(Completar con nombres)
Nombre del proyecto
Predicción de Rendimiento Agrícola y Alerta Temprana de Cosecha Insuficiente.
Problema
Los productores agropecuarios necesitan estimar el rendimiento de sus lotes (ej. soja o maíz) con anticipación para planificar la logística de cosecha (silos, transporte) y la gestión financiera. Un rendimiento inesperadamente bajo genera pérdidas críticas no presupuestadas.
Usuario de la predicción
Productor agrícola o asesor agronómico de la región.
Decisión que permitirá tomar
Contratar seguro agrícola adicional, ajustar la aplicación de fertilizantes de cobertura o planificar la venta futura del grano.
Variable numérica
Rendimiento estimado del cultivo en toneladas por hectárea (ton/ha).
Umbral y justificación
< 3.0 ton/ha (para soja/maíz en la zona). Justificación: Por debajo de este valor, el productor entra en zona de "no rentabilidad" o pérdida según los costos operativos actuales de la región, requiriendo una alerta de gestión.
Variable binaria
1 = Alerta de Rendimiento Insuficiente, 0 = Rendimiento dentro de parámetros normales/altos.
Fuente de datos
Kaggle: "Crop Yield Prediction Dataset" (se puede contextualizar filtrando o adaptando las columnas para que representen la región pampeana).
Cantidad de observaciones
~3,500 a 5,000 registros (cumple el mínimo de 2000).
Variables disponibles
1) Precipitaciones acumuladas (mm), 2) Temperatura media (°C), 3) Tipo de suelo (codificado), 4) Cantidad de fertilizante aplicado (kg/ha), 5) Tamaño del lote (ha), 6) Cultivo anterior (rotación).
Posibles fugas
Incluir el "precio final de venta" o el "costo total de producción" (son posteriores a la cosecha). También el "rendimiento real final" obviamente no puede ser predictor.
Riesgos y limitaciones
El modelo no captura plagas repentinas o granizo no registrado en los datos meteorológicos. Asume que las prácticas de siembra son estándar para la zona.











📌 Opción 2 — Predicción de consumo eléctrico de un hogar

Problema: Una distribuidora eléctrica quiere anticipar el consumo diario de hogares para gestionar la red.

Usuario: Ingeniero de planificación de la distribuidora.

Decisión: Si se espera consumo pico, activar reserva de capacidad.

Variable numérica: Consumo diario en kWh (agregado desde mediciones por minuto)

Umbral: Percentil 75 del consumo diario → “Consumo pico”

Variable binaria: consumo_pico = 1 si supera el umbral

Dataset: Individual Household Electric Power Consumption — UCI / Kaggle

~2 millones de registros (se pueden agregar por día: ~1.400 días) ✅
Variables: potencia activa, reactiva, voltaje, intensidad, 3 submedidores ✅
Requiere agregación, limpieza de faltantes y feature engineering de fecha ✅

Riesgos: Requiere más trabajo de preparación (agregación temporal). El grupo debe justificar bien el umbral usando los propios datos.





















📌 Opción 3: Calidad del aire en Buenos Aires ✅

Problema: el material particulado (PM10) afecta a personas con asma, chicos y adultos mayores.

Usuario: escuelas, clubes deportivos y personas con enfermedades respiratorias.

Decisión: al final del día anterior, decidir si se suspenden las actividades físicas al aire libre.

Variable numérica: PM10 promedio del día siguiente, en µg/m³.

Umbral: 45 µg/m³, que es la guía 24 h de la OMS (2021). Es muy fácil de justificar.

Variable binaria: aire_no_saludable.

Fuente: dataset “Calidad del aire” de la Agencia de Protección Ambiental de la Ciudad (data.buenosaires.gob.ar), con promedios diarios en las estaciones La Boca, Córdoba y Parque Centenario. Se puede cruzar con el clima de Open-Meteo.

Cantidad de observaciones: 3 estaciones × muchos años, varios miles de filas.

Predictores:

PM10, NO₂ y CO de hoy;
estación de medición;
día de la semana;
viento, lluvia y humedad (la lluvia “lava” el aire);
mes.

Fugas: las mediciones del mismo día que se quiere predecir.

Para preparar los datos: hay faltantes y valores negativos o imposibles, justo lo que pide la Clase 2.

Limitación: es Ciudad de Buenos Aires y no Chascomús. Tómenla como la “metrópoli cercana”.


📌 Opción 4: Demanda horaria de bicicletas compartidas

 Problema: una operadora de bicicletas compartidas necesita anticipar la cantidad de alquileres por hora para organizar la disponibilidad de bicicletas y la redistribución entre estaciones.
Usuario: equipo de operaciones de un sistema de bicicletas compartidas.
Decisión: reforzar la disponibilidad en horarios de demanda alta y planificar la redistribución.
Variable numérica: cantidad de alquileres por hora. Clasificación: demanda_alta = 1 si los alquileres superan un umbral definido con el conjunto de entrenamiento; 0 si no lo superan. El umbral podría comenzar en el percentil 75, sujeto a análisis.
Fuente posible: UCI Machine Learning Repository, “Bike Sharing Dataset” (registros horarios y diarios de alquileres de bicicletas, con variables temporales y meteorológicas). Antes de seleccionarlo, el grupo debe confirmar la versión, el número de filas útiles y que la consigna permita este tema.
Variables posibles: hora, día, mes, estación del año, día laboral, feriado, temperatura, sensación térmica, humedad, viento y alquileres históricos. Riesgos: clima excepcional, cambios en el servicio y diferencias entre ciudades o temporadas. No deben utilizarse variables que revelen directamente el total de alquileres de la hora que se está prediciendo.

📌 Opción 5: Prediccion de ventas por periodo

Problema: un comercio necesita estimar sus ventas para planificar compras, inventario y acciones comerciales.
Usuario: responsable de un comercio o de planificación comercial.
Decisión: anticipar necesidades de reposición y revisar la planificación cuando las ventas previstas queden por debajo de un objetivo.
Variable numérica: importe total de ventas por día o por período. Clasificación: objetivo_alcanzado = 1 si las ventas del período alcanzan el objetivo definido y 0 si quedan por debajo. El objetivo debe definirse con información disponible antes del período a predecir, no elegirse mirando el conjunto de prueba.
Fuente posible: UCI Machine Learning Repository, “Online Retail” u otro conjunto público de transacciones comerciales. Antes de seleccionarlo, se verificará el tamaño, la licencia, los campos disponibles y la forma de agregar transacciones por período.
Variables posibles: fecha, hora, producto, cantidad, precio unitario, país o región agregada y ventas de períodos anteriores, según la fuente elegida. Riesgos: devoluciones, promociones, cambios de precios, estacionalidad y ausencia de información sobre costos o stock. Deben excluirse identificadores personales y evitar predictores que contengan directa o indirectamente el importe futuro.





