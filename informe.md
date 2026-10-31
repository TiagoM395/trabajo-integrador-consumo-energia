# Informe de los modelos de aprendizaje automático

## 1. Resumen ejecutivo

La aplicación incluye dos modelos para estimar el consumo eléctrico de las próximas 24 horas y
anticipar si se superará una meta diaria de **25,9 kWh**:

| Modelo | Tipo | Archivo | Resultado que entrega |
|---|---|---|---|
| K vecinos más cercanos (KNN, k = 25) con escalado estándar | Regresión | [`modelos/reg_24h.pkl`](modelos/reg_24h.pkl) | Consumo estimado en kWh para las próximas 24 horas |
| Naive Bayes gaussiano (GaussianNB) | Clasificación binaria | [`modelos/clf_me_paso.pkl`](modelos/clf_me_paso.pkl) | Si se supera o no la meta diaria |

Los modelos se evalúan con mediciones de **un solo hogar de Sceaux, Francia**, entre 2006 y
2010. La comparación reproducible y los resultados completos están en
[`notebooks/entrenamiento_modelos.ipynb`](notebooks/entrenamiento_modelos.ipynb) y
[`explicaciones/README_ANALISIS.md`](explicaciones/README_ANALISIS.md). En prueba, el KNN k=25
obtuvo MAE **4,557 kWh** y R² **0,304**; GaussianNB tuvo accuracy **0,738** y recall **0,700**.
Son resultados de un solo período de prueba y no garantizan la misma calidad para hogares de
Argentina.

## 2. Datos de entrenamiento y alcance

La fuente principal es el dataset UCI
[*Individual Household Electric Power Consumption*](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption),
que registra el consumo de un hogar en Sceaux, Francia. El proyecto también contiene datos
meteorológicos diarios del mismo lugar, preparados con Open-Meteo. Las fuentes están resumidas en
[`datos/FUENTES.md`](datos/FUENTES.md).

El notebook y el módulo descargan y preparan el dataset UCI, entrenan los candidatos y presentan
las métricas. El ZIP se almacena en la caché del usuario. La ejecución requiere las dependencias
de `requirements.txt` y conexión a Internet la primera vez; no modifica los modelos guardados de
producción.

## 3. Descripción de los modelos

### 3.1 Regresión del consumo

El modelo KNN busca los **25 ejemplos de entrenamiento más parecidos** a la entrada y estima el
consumo futuro a partir de ellos. El `StandardScaler` incluido en el Pipeline estandariza las
variables antes de comparar distancias, para que las distintas escalas de medición no dominen la
comparación.

La app compara la estimación con la meta de 25,9 kWh:

- Por encima de la meta: la regresión indica que se supera el límite.
- A una distancia igual o menor que el MAE informado (4,57 kWh): el resultado se presenta como
  una zona de incertidumbre.

**Evaluación reproducible:** KNN k=25 obtuvo MAE **4,557 kWh**, RMSE **6,041 kWh** y R² **0,304**
en prueba. El mejor por MAE de validación fue k=50, con MAE **4,372 kWh**, RMSE **5,742 kWh** y
R² **0,371** en prueba. El `DummyRegressor` obtuvo MAE **6,152 kWh**. El MAE expresa error
absoluto medio en kWh; R² no es probabilidad de acierto.

### 3.2 Clasificación de exceso

GaussianNB estima a cuál de dos clases pertenece la observación: superar o no superar la meta. A
diferencia de la regresión, entrega directamente una clase, sin calcular primero una cantidad de
kWh que luego se compare con el límite.

En la prueba cronológica, GaussianNB obtuvo accuracy **0,738**, precision **0,600**, recall
**0,700** y F1 **0,646**. La matriz de confusión fue TN=2431, FP=778, FN=501 y TP=1168.
El recall deja en evidencia que algunos excesos no son detectados; la exactitud por sí sola no
describe ese riesgo.

El umbral de exceso se fija en **25,917658 kWh** (referencia que utiliza la aplicación), no se
ajusta mirando el test. La partición fue temporal: 22.740 casos de entrenamiento, 4.854 de
validación y 4.878 de prueba. Se purgaron 24 horas entre períodos para evitar solapamiento de
objetivos y se usaron los mismos casos de prueba para comparar las alertas. Las tasas de exceso
fueron 49,1 %, 70,5 % y 34,2 % respectivamente, lo que advierte de cambios entre períodos.

Se compararon Dummy, árboles de profundidad 3/6/12/sin límite y KNN k=5/25/50; el escalado se
ajustó dentro de los Pipelines KNN y solo con entrenamiento. La tabla completa de MAE, RMSE, R²,
accuracy, precision, recall, F1 y matrices de confusión está en el notebook.

### 3.3 Comparación integrada y costo de errores

Se asigna costo relativo 3 a un falso negativo (no advertir un exceso puede dejar menos tiempo
para reaccionar a un gasto inesperado) y 1 a un falso positivo (advertencia innecesaria). Es una
ponderación explícita, no una valoración monetaria.

| Sistema aplicado a los mismos 4.878 casos de prueba | Accuracy | Precision | Recall | F1 | TN | FP | FN | TP | Costo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Regresión KNN k=50 + umbral | 0,735 | 0,621 | 0,577 | 0,598 | 2621 | 588 | 706 | 963 | 2706 |
| GaussianNB directo | 0,738 | 0,600 | 0,700 | 0,646 | 2431 | 778 | 501 | 1168 | 2281 |

Las alertas coincidieron en 83,8 % de los casos. Con el costo elegido y en este período, el
clasificador directo conviene más: detecta más excesos y su costo observado es menor, aunque
produce más falsas alarmas. No se recomienda como decisión automática por el cambio temporal de
la tasa de excesos (34,2 % en test frente a 70,5 % en validación).

El 4/6/2010 a las 13 h el consumo real fue 25,932 kWh, apenas 0,014 kWh sobre el umbral; ambas
alertas no detectaron el exceso. El 17/10/2010 a las 22 h el real fue 44,667 kWh y la regresión
estimó 18,216 kWh. El 21/11/2010 a las 7 h el real fue 14,882 kWh y la regresión estimó
40,035 kWh. También hubo un falso positivo cercano: el 12/5/2010 a las 23 h el real fue
25,906 kWh (0,012 kWh por debajo del umbral) y GaussianNB indicó exceso. El notebook incluye
las listas de errores y casos próximos al umbral.

## 4. Variables que recibe la aplicación

La implementación arma una fila de **16 variables** antes de consultar ambos modelos. Algunas
provienen de la casa simulada o de la factura; otras se aproximan porque la app no cuenta con un
medidor doméstico que las registre.

| Variable | Cómo se obtiene en la app |
|---|---|
| `kwh_h` | Consumo estimado de la hora seleccionada, según la curva de la casa; si se parte de una factura, se ajusta al consumo diario facturado. |
| `active_24` | Consumo diario de la casa o consumo de la factura dividido por los días del período. |
| `active_prevweek` | Se aproxima con el mismo consumo diario actual porque la app no tiene historial de la semana anterior. |
| `reactive_24` | Se deriva del consumo activo suponiendo un factor de potencia de 0,95. |
| `cosphi_24` | Valor fijo de 0,95; no se mide en la casa. |
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
- **Amarillo:** las respuestas difieren o la regresión queda dentro de 4,57 kWh de la meta.
- **Verde:** ambos indican que no se supera la meta y la regresión está fuera de esa zona gris.

El semáforo facilita la lectura, pero no sustituye las predicciones individuales ni convierte la
estimación en una garantía. La lógica está en
[`simulador/prediccion.py`](simulador/prediccion.py) y
[`simulador/vista_prediccion.py`](simulador/vista_prediccion.py).

## 6. Limitaciones y riesgos de interpretación

1. **Un solo hogar y otro contexto.** Los patrones de Sceaux no representan necesariamente los de
   hogares argentinos. La diferencia de clima, vivienda, equipamiento y hábitos puede reducir la
   precisión.
2. **Meta poco representativa localmente.** Los 25,9 kWh diarios reflejan el consumo típico del
   hogar de referencia y pueden ser altos para muchas casas de Argentina.
3. **Datos aproximados.** El historial semanal, la energía reactiva, el factor de potencia y el
   voltaje no se miden en la casa del usuario; se completan con valores asumidos o constantes. Las
   temperaturas también dependen de la entrada manual.
4. **Problema documentado en el clasificador.** El proyecto registra que usar `cosphi_24 = 0,95`
   puede hacer que GaussianNB responda «no te pasás» casi siempre, incluso en situaciones de
   exceso. En una prueba documentada con la casa Familia en julio, la probabilidad estimada de
   «sí» fue 0 % con 0,95, frente a 95 % con 0,98 y 99,9 % con 0,99. Por lo tanto, el clasificador
   y el semáforo deben interpretarse con cautela hasta corregir esta entrada. El detalle está en
   [`README_PENDIENTES.md`](README_PENDIENTES.md).
5. **Límite inferior de las predicciones de regresión.** El proyecto también señala que KNN no
   predice por debajo de los valores bajos observados durante el entrenamiento. Para consumos muy
   inferiores al hogar de referencia puede sobreestimar el consumo.
6. **Cambio entre períodos.** La proporción de excesos varía entre entrenamiento, validación y
   prueba. El conjunto representa un hogar y una serie temporal concretos, por lo que la calidad
   puede cambiar en otras estaciones y viviendas.

## 7. Conclusión

Los dos modelos ofrecen enfoques complementarios: KNN estima energía y GaussianNB clasifica si se
supera la meta. En esta evaluación, la alerta directa del clasificador tiene menor costo ponderado
que derivar la alerta de la regresión, pero existen falsos negativos, falsos positivos y cambio de
distribución entre períodos. Ambos dependen de datos de un hogar francés y supuestos de entrada;
sus resultados son **orientativos**, no una medición ni una garantía para una vivienda argentina.
