# Informe general del proyecto

## Integrantes

- Tiago Maidana
- Elias Campos
- Romina Guzman
- Juanma Flescia
- Rodrigo Bulggiani

## 1. Resumen

**¿Me paso o no me paso?** es una aplicación web desarrollada en Python con Streamlit para
simular el consumo eléctrico de una vivienda, estimar el costo de la factura y anticipar si el
consumo de las próximas 24 horas superará una meta diaria. También permite comparar la simulación
con una factura real y explorar el consumo de los electrodomésticos en una representación
interactiva de la casa.

El proyecto combina dos enfoques:

1. **Cálculos deterministas:** estiman el consumo mensual y el importe de la factura a partir de
   los electrodomésticos, los hábitos ingresados y las tarifas configuradas.
2. **Aprendizaje automático:** utiliza dos modelos ya entrenados para estimar los kWh de las
   próximas 24 horas y clasificar si se superará la meta.

La aplicación no entrena los modelos cuando una persona la utiliza. Carga los archivos
entrenados `modelos/reg_24h.pkl` y `modelos/clf_me_paso.pkl` y calcula una predicción con los
datos disponibles.

## 2. Objetivo y funcionamiento general

La propuesta busca hacer más comprensible la factura eléctrica, que normalmente informa el
consumo total del período sin detallar cuánto aporta cada equipo. El usuario puede armar una
vivienda virtual, definir cantidades y hábitos de uso, estimar el consumo y el costo, y contrastar
el resultado con sus propios datos.

La aplicación organiza sus funciones en estas secciones:

- **Inicio:** presenta la aplicación.
- **Mi casa:** permite elegir perfiles y electrodomésticos, ajustar su uso, consultar el consumo
  mensual y obtener la predicción de exceso.
- **Ambiente 3D:** muestra los equipos en una escena interactiva y permite simular su uso.
- **Factura:** admite cargar datos manualmente o leer una factura en PDF, foto o cámara; luego
  permite calibrar la simulación con el consumo del período.
- **Análisis:** explica el dataset de entrenamiento, las variables, los modelos, la evaluación y
  sus limitaciones.

La meta usada por la aplicación es aproximadamente **13,3 kWh por día**, equivalente a
**400 kWh en un mes de 30 días**. En el proyecto se relaciona con el límite del tramo R3 del cuadro
tarifario de EDEA considerado para el trabajo.

## 3. De dónde salen los datos

El proyecto utiliza distintas fuentes según la función. Es importante diferenciar los datos de
entrenamiento de los datos usados para completar el catálogo y calcular una factura.

| Datos | Fuente y uso |
|---|---|
| Consumo eléctrico para entrenar los modelos | Dataset público de UCI, *Individual Household Electric Power Consumption*. Contiene mediciones de un único hogar de Sceaux, Francia, entre 2006 y 2010. Se utiliza para construir los ejemplos de entrenamiento y las etiquetas de exceso. |
| Temperatura histórica para el entrenamiento | Datos diarios históricos de Open-Meteo para Sceaux, almacenados en `clima_sceaux.csv`. Se incorporan como variables climáticas del dataset de entrenamiento. |
| Modelos y referencias de electrodomésticos | Dataset *Energy Rating for Household Appliances* del Gobierno de Australia, descargado desde data.gov.au. El CSV procesado `datos/electrodomesticos_eficiencia.csv` reúne 15.342 modelos y se usa para establecer valores de referencia de equipos, no para entrenar los dos modelos predictivos. |
| Tarifas eléctricas | Cuadros tarifarios residenciales de EDEA publicados por OCEBA, correspondientes a la Resolución MIySP N.º 682/2026 y con vigencia indicada desde el 1 de septiembre de 2026. Se procesan para generar `datos/tarifas_edea.csv`. |
| Impuestos | Tabla de impuestos residenciales de OCEBA y referencias de facturas de EDEA documentadas por el proyecto. Se almacenan en `datos/impuestos_residenciales.csv`; el informe de fuentes aclara los supuestos empleados. |
| Catálogo y perfiles de la casa | `simulador/datos/datos.json`, `simulador/variantes.py` y los datos procesados de electrodomésticos. Algunos valores provienen de medianas de modelos publicados; otros son valores típicos o supuestos editables. |
| Factura del usuario | La persona puede introducir los valores manualmente o cargar una factura. El texto de un PDF se lee con `pypdf`; las imágenes pueden procesarse con Tesseract OCR. También se intenta leer el QR o código de barras cuando está disponible. Los datos extraídos deben revisarse y confirmarse antes de usarse. |

Las fuentes, enlaces, criterios y limitaciones están detallados en [`datos/FUENTES.md`](datos/FUENTES.md).

### Preparación del dataset de entrenamiento

El script [`entrenamiento_modelos.py`](entrenamiento_modelos.py) procesa el archivo de UCI
(`datos/crudos/household_power_consumption.txt`) o lo descarga desde el repositorio público si no
está disponible localmente. Resume las mediciones de un minuto en registros horarios, depura
marcas temporales y mediciones inválidas, y descarta horas con menos de 45 mediciones válidas de
60 para las variables requeridas.

Para cada hora crea variables con información disponible hasta ese momento y un objetivo que
representa la energía consumida durante las **24 horas siguientes**. La clasificación marca como
exceso los casos cuyo consumo futuro supera la meta de 13,33 kWh.

Como el hogar de Francia tiene un consumo mediano diario de unos 25,92 kWh, el proyecto multiplica
las variables de energía por aproximadamente **0,514**. De esta manera, esa mediana se aproxima a
13,33 kWh. Es un reescalado para adaptar la escala del problema, no una medición de hogares
argentinos.

Los ejemplos se separan cronológicamente en entrenamiento, validación y prueba. Se dejan
intervalos de 24 horas entre particiones para reducir el solapamiento entre objetivos futuros.
Los modelos candidatos se comparan primero en validación; la partición de prueba se usa para
informar el desempeño final.

## 4. Cómo funcionan los cálculos de consumo y factura

El consumo de la vivienda se estima a partir de los datos cargados por el usuario. Según el tipo
de equipo, el cálculo mensual puede basarse en:

- **Horas de uso:** potencia, horas de uso y días por semana, incluyendo el consumo en espera
  cuando corresponde.
- **Ciclos:** energía por ciclo y cantidad de usos semanales.
- **Consumo anual de etiqueta:** se distribuye el consumo de heladeras y freezers a lo largo del
  año.
- **Funcionamiento continuo:** potencia multiplicada por las horas conectadas.

El motor de cálculo está en [`simulador/calculo.py`](simulador/calculo.py). El resultado depende de
los valores y hábitos ingresados; por eso es una simulación y no una lectura directa de un medidor
de la vivienda.

Para estimar la factura, el sistema selecciona un tramo residencial según el consumo mensual y
aplica cargo fijo, cargo variable, cargos tarifarios adicionales, bonificaciones e impuestos
según el escenario de subsidio elegido. Los archivos de tarifas se generan con
[`datos/preparar_tarifas.py`](datos/preparar_tarifas.py). Las tarifas no cambian los kWh estimados,
sino el importe que se calcula para ellos.

La lectura de una factura sirve para comparar el consumo simulado con el real y ajustar la
simulación. El archivo se procesa en memoria según la implementación; el código documenta que el
texto personal extraído se descarta y que la persona debe revisar los campos detectados.

## 5. Cómo funcionan los modelos

Los dos modelos reciben una fila con **16 variables**. Entre ellas se encuentran el consumo
horario y de las últimas 24 horas, la referencia de consumo de la semana anterior, energía
reactiva, factor de potencia, consumos agrupados por submedidor, voltaje, hora, día, mes,
indicadores de fin de semana y feriado, y temperatura.

Cuando la aplicación no dispone de una medición equivalente a la del dataset, aproxima algunos
valores: por ejemplo, usa el consumo diario actual como referencia de la semana anterior, una
energía reactiva típica del dataset reescalado y el voltaje promedio observado allí. Los
electrodomésticos de la casa virtual se agrupan en categorías equivalentes a los submedidores del
dataset. La aplicación ajusta también el mes para invertir las estaciones entre hemisferios. Los
ajustes pueden consultarse en la pestaña **Análisis**.

### Modelo de regresión: K vecinos más cercanos

El regresor elegido es **KNeighborsRegressor con k = 50**, integrado con `StandardScaler` en un
Pipeline. Primero se estandarizan las variables para que las diferencias de escala no dominen la
comparación. Luego se buscan los 50 registros de entrenamiento más parecidos a la entrada y se
estima el consumo de las próximas 24 horas a partir de esos vecinos.

La aplicación compara el valor estimado con la meta de 13,3 kWh. La regresión indica exceso si la
estimación es superior a la meta. Si la diferencia con el límite es menor o igual al MAE de prueba
(aproximadamente 2,25 kWh), el resultado se considera una zona de incertidumbre.

### Modelo de clasificación: GaussianNB

El clasificador elegido es **GaussianNB** (Naive Bayes gaussiano). En lugar de estimar directamente
una cantidad de kWh, determina cuál de estas dos clases corresponde a las variables recibidas:

- **No supera la meta.**
- **Supera la meta.**

Es una predicción directa de clase y, por lo tanto, puede no coincidir con la alerta obtenida al
comparar la salida del regresor con el umbral. La interfaz considera esa discrepancia al presentar
el semáforo.

### Evaluación informada por el proyecto

En el período de prueba cronológico documentado, los resultados fueron:

| Modelo / enfoque | Métricas de prueba |
|---|---|
| KNN k=50, regresión | MAE: **2,249 kWh**; RMSE: **2,954 kWh**; R²: **0,371**. |
| GaussianNB, clasificación | Accuracy: **0,738**; precision de exceso: **0,600**; recall de exceso: **0,700**; F1: **0,646**. |

El análisis también compara el costo de errores, asignando un costo relativo mayor a los falsos
negativos que a los falsos positivos. En la prueba descrita, el clasificador detectó más excesos,
pero también generó más falsas alarmas que la alerta basada en la regresión. Las métricas son
resultados sobre ese dataset y ese período; no garantizan la misma precisión en otros hogares.
La evaluación completa se encuentra en [`informe.md`](informe.md) y
[`explicaciones/README_ANALISIS.md`](explicaciones/README_ANALISIS.md).

## 6. Flujo de una predicción en la aplicación

1. La persona configura su vivienda y sus electrodomésticos o carga los datos de consumo de una
   factura.
2. El simulador estima el consumo diario y horario a partir de esa configuración.
3. La aplicación completa las variables requeridas por los modelos, incluidas las aproximaciones
   necesarias cuando no existe historial o medición doméstica.
4. [`simulador/prediccion.py`](simulador/prediccion.py) carga los dos archivos entrenados y prepara
   la fila de entrada en el orden de variables esperado.
5. El regresor estima los kWh de las próximas 24 horas y el clasificador predice directamente si
   se excede la meta.
6. La interfaz compara ambas respuestas, informa si coinciden y señala la cercanía al umbral o la
   zona de incertidumbre.

## 7. Alcances y limitaciones

- Los modelos de aprendizaje automático se entrenan con mediciones de **un solo hogar francés**;
  no con una muestra representativa de viviendas argentinas.
- El factor de escala ajusta el nivel de consumo, pero no reproduce por sí solo las diferencias de
  clima, equipamiento, hábitos, tarifas o condiciones de cada hogar.
- Algunas variables que en el dataset original provienen de mediciones reales se sustituyen en la
  aplicación por valores típicos o estimaciones. Esa diferencia entre entrenamiento y uso real
  puede afectar las predicciones.
- La temperatura del dataset de entrenamiento proviene de observaciones diarias históricas. En el
  proceso de preparación se usa el día previo como referencia para las variables meteorológicas;
  no equivale a disponer de una previsión meteorológica horaria exacta.
- Los datos de consumo por electrodoméstico del catálogo no son todos mediciones locales: algunos
  son medianas de modelos de Australia y Nueva Zelanda, mientras que otros son supuestos típicos.
  El propio proyecto aclara que sus clases relativas A–G no son el etiquetado IRAM argentino.
- La predicción se refiere a las **próximas 24 horas**, no constituye una garantía sobre el
  consumo real ni reemplaza la lectura del medidor.
- La extracción de facturas por OCR puede cometer errores; por eso la aplicación solicita
  verificar y confirmar los datos identificados.
- Los cuadros tarifarios e impuestos dependen de su vigencia, distribuidora, categoría y
  situación del usuario. La factura simulada es una estimación basada en los archivos y supuestos
  documentados por el proyecto.

## 8. Conclusión

El proyecto integra una herramienta didáctica de simulación energética con una experiencia
interactiva y dos modelos de aprendizaje automático. Su principal aporte es permitir explorar
cómo los equipos y hábitos modifican el consumo y el costo, y mostrar cómo se genera una alerta
de exceso a partir de datos históricos.

La regresión estima una cantidad de energía y GaussianNB clasifica directamente el posible
exceso. Ambos se evalúan con una separación temporal y métricas explícitas. Para interpretar sus
resultados correctamente, es fundamental tener presente que el dataset procede de un único hogar
francés y que la adaptación al uso argentino se realiza mediante reescalado y aproximaciones de
variables.

## Archivos principales

- Aplicación: [`streamlit_app.py`](streamlit_app.py).
- Preparación y entrenamiento: [`entrenamiento_modelos.py`](entrenamiento_modelos.py).
- Predicción en la aplicación: [`simulador/prediccion.py`](simulador/prediccion.py).
- Cálculo de consumo y factura: [`simulador/calculo.py`](simulador/calculo.py).
- Fuentes: [`datos/FUENTES.md`](datos/FUENTES.md).
- Análisis de modelos: [`explicaciones/README_ANALISIS.md`](explicaciones/README_ANALISIS.md).
- Evaluación de modelos: [`informe.md`](informe.md).
