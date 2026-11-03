# Análisis del dataset y de los modelos

## 1. Datos y reproducción

Los modelos usan el dataset UCI *Individual Household Electric Power Consumption*: mediciones
por minuto de un solo hogar en Sceaux, Francia, entre 2006 y 2010. No representa una muestra de
hogares argentinos: por eso su consumo se **reescala** a un hogar argentino (sección 3). La app
carga los Pipelines guardados y no los vuelve a entrenar al predecir.

El flujo reproducible está en [`notebooks/entrenamiento_modelos.ipynb`](../notebooks/entrenamiento_modelos.ipynb)
y [`entrenamiento_modelos.py`](../entrenamiento_modelos.py). El script lee el archivo
`datos/crudos/household_power_consumption.txt` (133 MB, fuera del repositorio); si no está,
descarga el ZIP público de UCI (20 MB) en la caché del usuario. `python entrenamiento_modelos.py`
entrena, informa la evaluación y guarda en `modelos/` el regresor y el clasificador elegidos en
validación, que son los que usa la app. Requiere las dependencias de `requirements.txt`.

## 2. Preparación y control de calidad

Cada fila supervisada es una hora de pronóstico. Se leen fecha/hora, potencia activa/reactiva,
voltaje y tres submedidores. Los `?` pasan a faltantes. Se auditan timestamps inválidos, filas
duplicadas exactas y valores físicos imposibles. Se excluyen potencias/reactiva/submedidores
negativos, potencia activa superior a 15 kW y voltaje no positivo; no se imputan los faltantes.
Una hora se acepta si las seis mediciones tienen al menos 45 minutos válidos de los 60. Potencia
activa/reactiva y voltaje se promedian; los submedidores (Wh/minuto) se ajustan a 60 minutos.

La corrida auditó 2.075.259 filas, 155.874 celdas faltantes, cero timestamps inválidos, cero
filas duplicadas exactas y cero filas físicamente imposibles. Quedaron 34.151 horas completas y
32.520 filas supervisadas después de exigir historial, objetivo y clima completos. El notebook
recalcula estas cifras en cada ejecución.

El objetivo de regresión es la energía activa (kWh) de las 24 horas posteriores al instante de
predicción. La clase positiva significa que ese objetivo supera **13,33 kWh** (sección 3). Los 16
predictores son: consumo de la hora; ventanas de 24 horas de energía activa/reactiva y
submedidores; consumo equivalente de la semana anterior; factor de potencia derivado; voltaje;
hora, día, mes, fin de semana y feriado; y temperaturas actual y de las próximas 24 horas.

| Predictor | Preparación en el conjunto UCI |
|---|---|
| `kwh_h` | Potencia activa media de la hora de origen, equivalente a kWh de esa hora. |
| `active_24` | Suma de la hora de origen y las 23 anteriores. |
| `active_prevweek` | Suma de las 24 horas equivalentes una semana antes. |
| `reactive_24` | Suma de potencia reactiva de la ventana actual de 24 horas. |
| `cosphi_24` | `active_24 / sqrt(active_24² + reactive_24²)`. |
| `sub1_24`, `sub2_24`, `sub3_24` | Suma de cada submedidor en la ventana actual de 24 horas. |
| `volt_24` | Voltaje medio de la ventana actual de 24 horas. |
| `hour`, `dayofweek`, `month` | Hora, día de semana y mes de la marca horaria local. |
| `is_weekend` | 1 si el día es sábado o domingo; 0 en otro caso. |
| `is_feriado` | Feriados nacionales franceses fijos y móviles para el año. |
| `temp_actual`, `temp_next24` | Promedio diario del último día completo disponible, usado como proxy de persistencia en ambos campos. |

El archivo de clima contiene promedios diarios observados, no pronósticos. Para evitar usar
información meteorológica futura, el entrenamiento usa el promedio del último día completo como
aproximación por persistencia para ambos predictores de temperatura. La app, en cambio, permite
ingresar los valores de hoy y mañana.

No se incluyen el consumo objetivo futuro ni su clase entre los predictores. La separación es
cronológica, aproximadamente 70/15/15, y se purgan 24 horas en los límites para evitar solapamiento
entre ventanas objetivo. La corrida produjo 22.740 casos de entrenamiento, 4.854 de validación y
4.878 de prueba. Validación elige candidatos; prueba se reserva para evaluación final. Todas las
comparaciones integradas usan exactamente los mismos casos de prueba. El `StandardScaler` de KNN
está en un `Pipeline` y solo se ajusta con entrenamiento.

## 3. Reescalado a un hogar argentino y meta

**Meta**

La meta es **13,33 kWh por día = 400 kWh por mes**: el límite del tramo R3 del cuadro tarifario
de EDEA ([Res. MIySP N° 682/2026](https://oceba.gba.gov.ar/nueva_web/adjuntos/ct202609/IF-2026-27778457-GDEBA-GMOCEBA.pdf)).
Por encima de 400 kWh por mes la factura pasa al tramo R4, con cargo fijo y precio por kWh más
altos. Pasarse de la meta tiene entonces una consecuencia concreta en la factura.

**Reescalado**

El hogar de Sceaux consume mucho más que uno argentino: la mediana de sus días completos es
**25,92 kWh** (unos 786 kWh por mes en promedio). Con la meta de 13,33 kWh y los datos sin tocar,
el 91 % de los días quedaría por encima y el clasificador aprendería a decir casi siempre «te
pasás».

Por eso toda la energía del hogar (activa, reactiva y los tres submedidores) se multiplica por

> factor = 13,33 ÷ 25,92 ≈ **0,514**

La mediana diaria pasa de 25,92 a 13,33 kWh: la meta sigue siendo la mediana y la mitad de los
días la supera. El voltaje no es energía y no cambia; el cos φ tampoco, porque activa y reactiva
se escalan igual. El reescalado se aplica antes de armar las filas supervisadas
(`escalar_a_hogar_argentino` en el script).

Los árboles, GaussianNB y KNN con `StandardScaler` no dependen de la unidad de los datos: las
métricas de clasificación son las mismas que con el umbral original de 25,92 kWh, y los errores de
regresión quedan multiplicados por 0,514 (pasan a la escala argentina).

La proporción de excesos fue 49,1 % en entrenamiento, 70,5 % en validación y 34,2 % en prueba,
señal de cambio entre períodos. La meta se fijó antes de evaluar; no se optimiza mirando el
conjunto de prueba.

**Selección de modelos**

Se comparan:

- **Regresión:** `DummyRegressor` (media), `DecisionTreeRegressor` con profundidad 3, 6, 12 y sin
  límite, y `KNeighborsRegressor` con k=5, 25 y 50. Los KNN llevan `StandardScaler` dentro de un
  `Pipeline`.
- **Clasificación:** `DummyClassifier` (prior), `DecisionTreeClassifier` con las mismas
  profundidades, `KNeighborsClassifier` con k=5, 25 y 50, y `GaussianNB`. El KNN usa escalado en
  un `Pipeline`.

Regresión selecciona por menor MAE en validación. Clasificación selecciona por menor costo
relativo y, ante empate, mayor F1. El notebook presenta las tablas completas de validación y
prueba para todos los candidatos.

## 4. Resultados reproducibles

| Sistema/candidato | Validación | Prueba |
|---|---|---|
| Dummy regresión (media), MAE | 3,261 kWh | 3,165 kWh |
| KNN k=25, MAE / RMSE / R² | 3,004 / 4,029 / -0,167 | 2,345 / 3,108 / 0,304 |
| KNN k=50, MAE / RMSE / R² | 2,846 / 3,790 / -0,032 | 2,249 / 2,954 / 0,371 |
| GaussianNB, accuracy / precision / recall / F1 | 0,757 / 0,771 / 0,932 / 0,844 | 0,738 / 0,600 / 0,700 / 0,646 |

El KNN k=50 es el regresor elegido por validación y el que usa la app. En prueba obtuvo mejor MAE
que el baseline (2,249 frente a 3,165 kWh). El árbol de profundidad 6 obtuvo MAE 2,395 kWh, RMSE
3,208 kWh y R² 0,258 en prueba. R² no es probabilidad de acierto.

GaussianNB fue el clasificador elegido en validación y el que usa la app. En prueba, su matriz de
confusión fue TN=2430, FP=779, FN=501 y TP=1168. El baseline mayoritario tuvo accuracy 0,658 y no
detectó excesos (recall 0; 1669 falsos negativos). Las métricas completas de todos los modelos
están en el notebook.

## 5. Comparación de alertas y costo de errores

Se asigna costo relativo **3** a un falso negativo: omitir una advertencia de exceso puede dejar
menos tiempo para reaccionar a un gasto inesperado. Un falso positivo cuesta **1** por ser una
advertencia innecesaria. Es una ponderación explícita de decisión, no una estimación monetaria.

En los mismos 4.878 casos de prueba, el KNN k=50 elegido en validación, seguido por la meta,
obtuvo accuracy 0,735, precision 0,621, recall 0,577, F1 0,598 y costo 2706
(TN=2621, FP=588, FN=706, TP=963). GaussianNB obtuvo costo 2282
(TN=2430, FP=779, FN=501, TP=1168), accuracy 0,738, precision 0,600, recall 0,700 y F1 0,646.
Ambas alertas coincidieron en 83,8 % de los casos. Con esta ponderación y en esta prueba, el
clasificador directo conviene más: detectó más excesos y su costo observado fue menor, aunque
produjo más falsas alarmas.

Hay errores muy cerca de la meta. El 4/6/2010 a las 13 h el consumo real fue 13,341 kWh (exceso
por 0,007 kWh), pero ambas alertas dijeron que no. En errores más alejados, el 17/10/2010 a las
22 h el real fue 22,979 kWh y KNN estimó 9,371 kWh; el 21/11/2010 a las 7 h el real fue
7,656 kWh y estimó 20,596 kWh. Como falso positivo cercano, el 12/5/2010 a las 23 h el real fue
13,327 kWh (0,006 kWh por debajo de la meta) y GaussianNB indicó exceso. El notebook lista casos
cercanos, residuos, falsos positivos y falsos negativos.

La app muestra ambas respuestas: rojo si coinciden en exceso, amarillo si discrepan o la
regresión queda dentro del MAE de la meta y verde si ambas indican que no se supera. El amarillo
comunica incertidumbre, no una probabilidad ni una garantía.

## 6. Datos de entrada en la app

La app no tiene medidor: arma los 16 predictores con lo que se carga en *Mi casa* o en *Factura*.

- **Mes:** se corre 6 meses (julio de acá entra como enero), porque las estaciones están invertidas.
- **Energía reactiva:** se usa la típica del dataset reescalado, 1,5 kVArh por día, que casi no
  cambia con el consumo. El cos φ se calcula con ella, igual que en el entrenamiento
  (`active_24 / sqrt(active_24² + 1,5²)`).
- **Consumo de la semana anterior:** se usa el mismo consumo diario.
- **Voltaje:** la media del dataset (240 V).
- **Submedidores:** los electrodomésticos se agrupan como en el dataset (cocina / lavadero,
  heladera y luces / termotanque y clima).

## Mejoras pendientes de los modelos

| Qué falla hoy | Cómo mejorarlo |
|---|---|
| En verano el modelo estima de menos: el hogar de Francia no tenía aire acondicionado y en verano consumía poco | Entrenar con un hogar que use aire (otro dataset público) o agregar una variable de temperatura alta que sume el consumo del aire cargado en *Mi casa* |
| Aprendió de un solo hogar | Sumar más hogares: otros datasets públicos o el historial bimestral de facturas reales de EDEA (cada boleta trae los últimos 7 períodos) |
| Los feriados del entrenamiento son franceses y la app usa los argentinos | Al reentrenar, marcar como feriado los días de la lista argentina (con el calendario ya corrido 6 meses) |
| El consumo de la semana anterior se completa con el de hoy | Guardar el consumo de cada día en la sesión de la casa, o usar el de la factura anterior |
| La energía reactiva es un valor fijo del dataset | Estimarla por electrodoméstico con su factor de potencia (pasos B a D de la sección 1 de [`README_PENDIENTES.md`](../README_PENDIENTES.md)) |
| La temperatura viene en 20 °C hasta que la persona la cambia | Traer la temperatura de hoy y el pronóstico de mañana desde Open-Meteo, la misma fuente del clima del entrenamiento |
| KNN no baja de los días de menor consumo del hogar: sobreestima casas muy chicas | Probar un modelo que extrapole (regresión lineal o árbol con más profundidad) y compararlo en validación |
| Las horas repetidas por el cambio de hora se agrupan juntas | Usar la zona horaria de París al leer el dataset |

La implementación de las variables de entrada y predicción en la app está en
[`simulador/prediccion.py`](../simulador/prediccion.py).
