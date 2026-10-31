# Análisis del dataset y de los modelos

## 1. Datos y reproducción

Los modelos usan el dataset UCI *Individual Household Electric Power Consumption*: mediciones
por minuto de un solo hogar en Sceaux, Francia, entre 2006 y 2010. No representa una muestra de
hogares argentinos. La app carga los Pipelines guardados y no los vuelve a entrenar al predecir.

El flujo reproducible está en [`notebooks/entrenamiento_modelos.ipynb`](../notebooks/entrenamiento_modelos.ipynb)
y [`entrenamiento_modelos.py`](../entrenamiento_modelos.py). Ejecutar todas las celdas del notebook
desde el repositorio. Requiere las dependencias de `requirements.txt` y conexión a Internet la
primera vez; descarga el ZIP público de UCI (20 MB) en la caché del usuario, no en el repositorio.
El notebook no reemplaza los modelos de producción.

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
predicción. La clase positiva significa que ese objetivo supera 25,917658 kWh. Los 16 predictores
son: consumo de la hora; ventanas de 24 horas de energía activa/reactiva y submedidores; consumo
equivalente de la semana anterior; factor de potencia derivado; voltaje; hora, día, mes, fin de
semana y feriado; y temperaturas actual y de las próximas 24 horas.

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

## 3. Umbral y selección de modelos

Se mantiene el umbral existente de la aplicación (25,917658 kWh/24 h), fijado antes de evaluar;
no se optimiza mirando el conjunto de prueba. Es una referencia del proyecto, no una recomendación
universal para hogares argentinos. La proporción de excesos fue 49,1 % en entrenamiento, 70,5 %
en validación y 34,2 % en prueba, señal de cambio entre períodos.

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
| Dummy regresión (media), MAE | 6,339 kWh | 6,152 kWh |
| KNN k=25, MAE / RMSE / R² | 5,840 / 7,833 / -0,167 | 4,557 / 6,041 / 0,304 |
| KNN k=50, MAE / RMSE / R² | 5,531 / 7,367 / -0,032 | 4,372 / 5,742 / 0,371 |
| GaussianNB, accuracy / precision / recall / F1 | 0,757 / 0,771 / 0,932 / 0,844 | 0,738 / 0,600 / 0,700 / 0,646 |

El KNN k=50 es el regresor elegido por validación. En prueba obtuvo mejor MAE que el baseline
(4,372 frente a 6,152 kWh). El árbol de profundidad 6 obtuvo MAE 4,655 kWh, RMSE 6,235 kWh y R²
0,258 en prueba. El MAE de KNN k=25 en prueba (4,557 kWh) reproduce el valor redondeado informado
previamente. R² no es probabilidad de acierto.

GaussianNB fue el clasificador elegido en validación. En prueba, su matriz de confusión fue
TN=2431, FP=778, FN=501 y TP=1168. El baseline mayoritario tuvo accuracy 0,658 y no detectó
excesos (recall 0; 1669 falsos negativos). Las métricas completas de todos los modelos están en
el notebook.

## 5. Comparación de alertas y costo de errores

Se asigna costo relativo **3** a un falso negativo: omitir una advertencia de exceso puede dejar
menos tiempo para reaccionar a un gasto inesperado. Un falso positivo cuesta **1** por ser una
advertencia innecesaria. Es una ponderación explícita de decisión, no una estimación monetaria.

En los mismos 4.878 casos de prueba, el KNN k=50 elegido en validación, seguido por el umbral,
obtuvo accuracy 0,735, precision 0,621, recall 0,577, F1 0,598 y costo 2706
(TN=2621, FP=588, FN=706, TP=963). GaussianNB obtuvo costo 2281
(TN=2431, FP=778, FN=501, TP=1168), accuracy 0,738, precision 0,600, recall 0,700 y F1 0,646.
Ambas alertas coincidieron en 83,8 % de los casos. Con esta ponderación y en esta prueba, el
clasificador directo conviene más: detectó más excesos y su costo observado fue menor, aunque
produjo más falsas alarmas.

Hay errores muy cerca del umbral. El 4/6/2010 a las 13 h el consumo real fue 25,932 kWh (exceso
por 0,014 kWh), pero ambas alertas dijeron que no. En errores más alejados, el 17/10/2010 a las
22 h el real fue 44,667 kWh y KNN estimó 18,216 kWh; el 21/11/2010 a las 7 h el real fue
14,882 kWh y estimó 40,035 kWh. Como falso positivo cercano, el 12/5/2010 a las 23 h el real fue
25,906 kWh (0,012 kWh por debajo del umbral) y GaussianNB indicó exceso. El notebook lista casos
cercanos, residuos, falsos positivos y falsos negativos.

La app muestra ambas respuestas: rojo si coinciden en exceso, amarillo si discrepan o la
regresión queda dentro del MAE de la meta y verde si ambas indican que no se supera. El amarillo
comunica incertidumbre, no una probabilidad ni una garantía.

## 6. Limitaciones

- Los datos reflejan un solo hogar francés. Las proporciones de excesos cambian entre períodos y
  una partición temporal no garantiza el desempeño en otras estaciones o viviendas.
- El umbral puede ser alto para muchas casas argentinas.
- En la app, historial semanal, energía reactiva, cos φ y voltaje se aproximan con supuestos; la
  temperatura se ingresa manualmente. El clasificador puede ser sensible al cos φ fijo de 0,95;
  ver [`README_PENDIENTES.md`](../README_PENDIENTES.md).
- KNN puede sobreestimar consumos muy inferiores a los observados durante el entrenamiento.
- Los datos no tienen zona horaria explícita para distinguir una hora local repetida por el cambio
  estacional; la preparación agrupa mediciones con la misma hora local.
- El notebook entrena candidatos en memoria y no sobrescribe los `.pkl` de producción.

La implementación de las variables de entrada y predicción en la app está en
[`simulador/prediccion.py`](../simulador/prediccion.py).
