# Prioridades completadas

**Proyecto:** ¿Me paso o no me paso?  
**Actualizado:** 30 de octubre de 2026

Este documento registra el trabajo realizado para las prioridades marcadas como completadas en
[`PENDIENTES_ENTREGA.md`](PENDIENTES_ENTREGA.md).

## Prioridad 1: completar la evidencia de aprendizaje automático

### Trabajo realizado

- Se incorporó el notebook ejecutable
  [`notebooks/entrenamiento_modelos.ipynb`](notebooks/entrenamiento_modelos.ipynb) y su módulo
  de preparación, entrenamiento y evaluación
  [`entrenamiento_modelos.py`](entrenamiento_modelos.py). El flujo descarga el dataset UCI la
  primera vez y guarda el archivo en la caché local, sin agregarlo al repositorio ni reemplazar
  los modelos `.pkl` de producción.
- Se documentaron la fuente de datos, el significado de cada fila, los predictores y objetivos,
  los faltantes, duplicados y valores imposibles, y las medidas tomadas para evitar usar el
  objetivo futuro como predictor.
- Se fijó para la evaluación el umbral de exceso que ya utiliza la aplicación: **25,917658 kWh
  en las próximas 24 horas**. Se explicó que es una referencia del proyecto, no una recomendación
  universal.
- Se implementó una separación temporal de entrenamiento, validación y prueba, con purga de
  ventanas de 24 horas en los límites. Regresión, clasificación y comparación de alertas utilizan
  los mismos casos de evaluación.
- Se compararon los baselines y algoritmos requeridos: `DummyRegressor`,
  `DecisionTreeRegressor`, `KNeighborsRegressor` con escalado en un `Pipeline`,
  `DummyClassifier`, `DecisionTreeClassifier`, `KNeighborsClassifier` con escalado en un
  `Pipeline` y `GaussianNB`.
- El notebook informa MAE, RMSE, R², residuos y errores destacados para regresión; accuracy,
  precision, recall, F1 y matriz de confusión para clasificación; además de falsos positivos,
  falsos negativos y casos próximos al umbral.
- Se definieron costos relativos de **3** para un falso negativo y **1** para un falso positivo,
  y se comparó la alerta del clasificador directo con la derivada de la regresión.
- Se actualizaron el [análisis detallado](explicaciones/README_ANALISIS.md), el
  [informe](informe.md), el [README del proyecto](README.md) y
  [las fuentes de datos](datos/FUENTES.md) para reflejar el flujo reproducible y sus resultados.
- Se actualizó el documento de pendientes para marcar esta prioridad como completada y dejar
  explícito que la evaluación no sobrescribe los modelos de producción.

### Resultados de la evaluación reproducible

- El modelo de regresión KNN con `k=25`, correspondiente al artefacto existente, obtuvo en la
  partición de prueba **MAE 4,557 kWh, RMSE 6,041 kWh y R² 0,304**.
- El KNN con `k=50`, seleccionado por validación, obtuvo en prueba **MAE 4,372 kWh,
  RMSE 5,742 kWh y R² 0,371**. El `DummyRegressor` obtuvo MAE **6,152 kWh**.
- `GaussianNB`, seleccionado por costo en validación, obtuvo en prueba **accuracy 0,738,
  precision 0,600, recall 0,700 y F1 0,646**; matriz de confusión: **TN=2431, FP=778,
  FN=501, TP=1168**.
- En los mismos casos, la alerta directa de `GaussianNB` tuvo costo total **2281**, frente a
  **2706** para la alerta obtenida del KNN `k=50` comparado con el umbral. Las alertas
  coincidieron en **83,8 %** de los casos.
- La recomendación del análisis es preferir la alerta directa bajo la ponderación de costos
  definida, con cautela: las proporciones de excesos cambian entre períodos y los datos proceden
  de un único hogar francés.

### Verificación

- El notebook se ejecutó completo y generó sus tablas y análisis.
- `python entrenamiento_modelos.py` terminó correctamente.
- `python -m unittest discover -s tests -v`: **23 pruebas aprobadas**, incluidas pruebas de
  preparación de ventanas y separación temporal.
- Se validó la estructura JSON y la sintaxis de las celdas de código del notebook.

## Prioridad 2: resolver la tecnología y el despliegue

### Trabajo realizado

- Se confirmó Streamlit como tecnología aceptada para la entrega y se eligió Streamlit Community
  Cloud.
- Se publicó la app desde la rama `main`, usando Python 3.12:
  <https://me-paso-consumo-energia-tiago.streamlit.app/>.
- Se comprobó que la app se ve bien en teléfonos.
- Se documentaron en [`EJECUTAR.md`](EJECUTAR.md) el despliegue, las dependencias y la limitación
  de persistencia del disco local de Community Cloud.

### Seguimiento posterior al despliegue

- La página **Análisis** necesita `explicaciones/README_ANALISIS.md`, que todavía no está en `main`.
  La app se redeplegará al subir los cambios pendientes; falta comprobar que la página quede
  funcionando.
- Falta verificar los modelos en la app publicada y decidir si las casas guardadas requieren
  almacenamiento persistente.

## Prioridades aún abiertas

Los entregables pendientes de la Prioridad 3 (presentación, bitácora y distribución de tareas)
siguen abiertos.
