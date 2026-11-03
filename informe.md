# Informe de los modelos de aprendizaje automático

## 1. Resumen ejecutivo

La aplicación incluye dos modelos para estimar el consumo eléctrico de las próximas 24 horas y
anticipar si se superará una meta diaria de **13,3 kWh** (400 kWh por mes, el límite del tramo R3
del cuadro tarifario de EDEA):

| Modelo | Tipo | Archivo | Resultado que entrega |
|---|---|---|---|
| K vecinos más cercanos (KNN, k = 50) con escalado estándar | Regresión | [`modelos/reg_24h.pkl`](modelos/reg_24h.pkl) | Consumo estimado en kWh para las próximas 24 horas |
| Naive Bayes gaussiano (GaussianNB) | Clasificación binaria | [`modelos/clf_me_paso.pkl`](modelos/clf_me_paso.pkl) | Si se supera o no la meta diaria |

Los modelos se entrenan con mediciones de **un solo hogar de Sceaux, Francia**, entre 2006 y
2010, cuyo consumo se **reescaló** al de un hogar argentino (× 0,514). La comparación reproducible y
los resultados completos están en
[`notebooks/entrenamiento_modelos.ipynb`](notebooks/entrenamiento_modelos.ipynb) y
[`explicaciones/README_ANALISIS.md`](explicaciones/README_ANALISIS.md). En prueba, el KNN k=50
obtuvo MAE **2,249 kWh** y R² **0,371**; GaussianNB tuvo accuracy **0,738** y recall **0,700**.
Son resultados de un solo período de prueba y no garantizan la misma calidad para hogares de
Argentina.

## 2. Datos de entrenamiento y alcance

La fuente principal es el dataset UCI
[*Individual Household Electric Power Consumption*](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption),
que registra el consumo de un hogar en Sceaux, Francia. El proyecto también contiene datos
meteorológicos diarios del mismo lugar, preparados con Open-Meteo. Las fuentes están resumidas en
[`datos/FUENTES.md`](datos/FUENTES.md).

El script [`entrenamiento_modelos.py`](entrenamiento_modelos.py) lee el dataset de
`datos/crudos/household_power_consumption.txt` (o lo descarga de UCI si no está), lo prepara,
entrena los candidatos, presenta las métricas y guarda en `modelos/` los dos modelos elegidos en
validación. El notebook muestra la misma corrida paso a paso.

### 2.1 Reescalado a un hogar argentino

El hogar de Sceaux consume mucho más que uno argentino: la mediana de sus días es **25,92 kWh**
(unos 786 kWh por mes). Si se usara la meta de 13,3 kWh con esos datos, el 91 % de los días la
superaría y el clasificador aprendería a responder casi siempre «te pasás».

Por eso toda la energía del hogar (activa, reactiva y submedidores) se multiplica por
**13,33 ÷ 25,92 ≈ 0,514**. Así la mediana diaria queda en 13,33 kWh: la meta coincide con la
mediana y la mitad de los días la supera. El voltaje y el factor de potencia no cambian.

Los modelos usados (árboles, GaussianNB y KNN con escalado estándar) no dependen de la unidad de
los datos. Las métricas de clasificación quedan iguales a las obtenidas con el hogar original y
su mediana (25,92 kWh), y los errores de regresión quedan multiplicados por 0,514.

### 2.2 Meta

La meta de **400 kWh por mes = 13,33 kWh por día** sale del cuadro tarifario de EDEA
([Res. MIySP N° 682/2026](https://oceba.gba.gov.ar/nueva_web/adjuntos/ct202609/IF-2026-27778457-GDEBA-GMOCEBA.pdf)):
el tramo R3 llega hasta 400 kWh. Por encima, la factura pasa al tramo R4, con cargo fijo y precio
por kWh más altos. Superar la meta tiene así una consecuencia directa en lo que se paga.

## 3. Descripción de los modelos

### 3.1 Regresión del consumo

El modelo KNN busca los **50 ejemplos de entrenamiento más parecidos** a la entrada y estima el
consumo futuro a partir de ellos. El `StandardScaler` incluido en el Pipeline estandariza las
variables antes de comparar distancias, para que las distintas escalas de medición no dominen la
comparación.

La app compara la estimación con la meta de 13,3 kWh:

- Por encima de la meta: la regresión indica que se supera el límite.
- A una distancia igual o menor que el MAE informado (2,25 kWh): el resultado se presenta como
  una zona de incertidumbre.

**Evaluación reproducible:** KNN k=50, el mejor por MAE de validación, obtuvo MAE **2,249 kWh**,
RMSE **2,954 kWh** y R² **0,371** en prueba. KNN k=25 obtuvo MAE **2,345 kWh**, RMSE
**3,108 kWh** y R² **0,304**. El `DummyRegressor` obtuvo MAE **3,165 kWh**. El MAE expresa error
absoluto medio en kWh; R² no es probabilidad de acierto.

### 3.2 Clasificación de exceso

GaussianNB estima a cuál de dos clases pertenece la observación: superar o no superar la meta. A
diferencia de la regresión, entrega directamente una clase, sin calcular primero una cantidad de
kWh que luego se compare con el límite.

En la prueba cronológica, GaussianNB obtuvo accuracy **0,738**, precision **0,600**, recall
**0,700** y F1 **0,646**. La matriz de confusión fue TN=2430, FP=779, FN=501 y TP=1168.
El recall deja en evidencia que algunos excesos no son detectados; la exactitud por sí sola no
describe ese riesgo.

La meta de exceso se fija en **13,33 kWh** antes de evaluar y no se ajusta mirando el test. La
partición fue temporal: 22.740 casos de entrenamiento, 4.854 de validación y 4.878 de prueba. Se
purgaron 24 horas entre períodos para evitar solapamiento de objetivos y se usaron los mismos
casos de prueba para comparar las alertas. Las tasas de exceso fueron 49,1 %, 70,5 % y 34,2 %
respectivamente, lo que advierte de cambios entre períodos.

Se compararon Dummy, árboles de profundidad 3/6/12/sin límite y KNN k=5/25/50; el escalado se
ajustó dentro de los Pipelines KNN y solo con entrenamiento. La tabla completa de MAE, RMSE, R²,
accuracy, precision, recall, F1 y matrices de confusión está en el notebook.

### 3.3 Comparación integrada y costo de errores

Se asigna costo relativo 3 a un falso negativo (no advertir un exceso puede dejar menos tiempo
para reaccionar a un gasto inesperado) y 1 a un falso positivo (advertencia innecesaria). Es una
ponderación explícita, no una valoración monetaria.

| Sistema aplicado a los mismos 4.878 casos de prueba | Accuracy | Precision | Recall | F1 | TN | FP | FN | TP | Costo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Regresión KNN k=50 + meta | 0,735 | 0,621 | 0,577 | 0,598 | 2621 | 588 | 706 | 963 | 2706 |
| GaussianNB directo | 0,738 | 0,600 | 0,700 | 0,646 | 2430 | 779 | 501 | 1168 | 2282 |

Las alertas coincidieron en 83,8 % de los casos. Con el costo elegido y en este período, el
clasificador directo conviene más: detecta más excesos y su costo observado es menor, aunque
produce más falsas alarmas. No se recomienda como decisión automática por el cambio temporal de
la tasa de excesos (34,2 % en test frente a 70,5 % en validación).

El 4/6/2010 a las 13 h el consumo real fue 13,341 kWh, apenas 0,007 kWh sobre la meta; ambas
alertas no detectaron el exceso. El 17/10/2010 a las 22 h el real fue 22,979 kWh y la regresión
estimó 9,371 kWh. El 21/11/2010 a las 7 h el real fue 7,656 kWh y la regresión estimó
20,596 kWh. También hubo un falso positivo cercano: el 12/5/2010 a las 23 h el real fue
13,327 kWh (0,006 kWh por debajo de la meta) y GaussianNB indicó exceso. El notebook incluye
las listas de errores y casos próximos a la meta.

## 4. Variables que recibe la aplicación

La implementación arma una fila de **16 variables** antes de consultar ambos modelos. Algunas
provienen de la casa simulada o de la factura; otras se aproximan porque la app no cuenta con un
medidor doméstico que las registre.

| Variable | Cómo se obtiene en la app |
|---|---|
| `kwh_h` | Consumo estimado de la hora seleccionada, según la curva de la casa; si se parte de una factura, se ajusta al consumo diario facturado. |
| `active_24` | Consumo diario de la casa o consumo de la factura dividido por los días del período. |
| `active_prevweek` | Se aproxima con el mismo consumo diario actual porque la app no tiene historial de la semana anterior. |
| `reactive_24` | Valor típico del dataset reescalado: 1,5 kVArh por día (en el hogar casi no cambia con el consumo). |
| `cosphi_24` | Se calcula como en el entrenamiento: `active_24 / sqrt(active_24² + reactive_24²)`. |
| `sub1_24` | Consumo diario agrupado para cocina. |
| `sub2_24` | Consumo diario agrupado para lavadero, heladera y luces. |
| `sub3_24` | Consumo diario agrupado para termotanque y climatización. |
| `volt_24` | Valor fijo de 240 V, la media indicada para el dataset. |
| `hour` | Hora seleccionada, expresada como número entero. |
| `dayofweek` | Día de la semana de la fecha elegida. |
| `month` | Mes desplazado seis meses para invertir las estaciones entre hemisferios. |
| `is_weekend` | Indicador de fin de semana derivado del día de la semana. |
| `is_feriado` | Indicador de feriado; combina la selección de la persona con una lista de fechas nacionales fijas. |
| `temp_actual` | Temperatura de hoy ingresada en la app; el valor inicial es 20 °C. |
| `temp_next24` | Temperatura de mañana ingresada en la app; el valor inicial es 20 °C. |

La construcción de estas variables y los valores asumidos están en
[`simulador/prediccion.py`](simulador/prediccion.py). La predicción se ejecuta con los Pipelines ya
guardados; la aplicación no vuelve a entrenar los modelos.

## 5. Cómo se presenta el resultado

La app muestra ambas respuestas y las combina en un semáforo:

- **Rojo:** ambos modelos indican que se supera la meta.
- **Amarillo:** las respuestas difieren o la regresión queda dentro de 2,25 kWh de la meta.
- **Verde:** ambos indican que no se supera la meta y la regresión está fuera de esa zona gris.

Con los perfiles de la app, una persona sola o una pareja dan verde todo el año; un hogar de
unos 320 kWh por mes da rojo en invierno (calefactor) y verde o amarillo el resto del año; una
familia con termotanque y calefactor eléctricos da rojo casi todo el año.

El semáforo facilita la lectura, pero no sustituye las predicciones individuales ni convierte la
estimación en una garantía. La lógica está en
[`simulador/prediccion.py`](simulador/prediccion.py) y
[`simulador/vista_prediccion.py`](simulador/vista_prediccion.py).

## 6. Mejoras pendientes

| Qué falla hoy | Cómo mejorarlo |
|---|---|
| En verano el modelo estima de menos: el hogar de Francia no tenía aire acondicionado | Entrenar con un hogar que use aire o sumar una variable de temperatura alta |
| Aprendió de un solo hogar | Sumar más hogares: otros datasets públicos o el historial bimestral de facturas reales de EDEA |
| Los feriados del entrenamiento son franceses | Reentrenar marcando los feriados argentinos |
| El consumo de la semana anterior, la energía reactiva y el voltaje se completan con valores típicos | Guardar el historial de la casa y estimar la reactiva por electrodoméstico |
| La temperatura se carga a mano | Traer la temperatura y el pronóstico desde Open-Meteo |
| KNN sobreestima casas de muy poco consumo | Comparar en validación un modelo que extrapole (regresión lineal o árbol) |
| La proporción de excesos cambia entre períodos (49 %, 70 % y 34 %) | Evaluar con validación por estaciones para ver en qué época falla más |

## 7. Conclusión

Los dos modelos ofrecen enfoques complementarios: KNN estima energía y GaussianNB clasifica si se
supera la meta. En esta evaluación, la alerta directa del clasificador tiene menor costo ponderado
que derivar la alerta de la regresión, pero existen falsos negativos, falsos positivos y cambio de
distribución entre períodos. Las mejoras de la sección 6 apuntan a que el modelo aprenda de hogares
con aire acondicionado y de más de una casa.
