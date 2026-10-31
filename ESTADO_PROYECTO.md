# Estado del proyecto

**Corte:** 28 de octubre de 2026  
**Proyecto:** ¿Me paso o no me paso?

## Resumen

El proyecto es una aplicación web en Python y Streamlit para simular el consumo eléctrico de
una vivienda, estimar su factura residencial de EDEA y ofrecer una predicción de consumo para
las próximas 24 horas. También incluye lectura de facturas, una visualización 3D de ambientes,
un catálogo de electrodomésticos y una sección explicativa sobre datos y modelos.

La aplicación tiene varias funcionalidades implementadas y modelos entrenados guardados. La
predicción debe considerarse **experimental**: los modelos se basan en un único hogar de
Francia y la entrada actual utiliza supuestos que reducen su representatividad para hogares
argentinos.

## Funcionalidades implementadas

- **Mi casa:** permite definir una vivienda, elegir electrodomésticos y perfiles, y calcular
  consumos mensuales y costos estimados.
- **Tarifas y factura:** calcula importes usando los datos tarifarios residenciales de EDEA y
  contempla escenarios de subsidio. La aplicación también permite cargar una factura para
  comparar el consumo registrado con la simulación.
- **Predicción:** aplica una regresión para estimar kWh y un clasificador para evaluar si se
  supera una meta diaria. Presenta las respuestas con un semáforo.
- **Ambiente 3D:** visualiza ambientes con muebles y equipos, y permite explorar el consumo.
- **Eficiencia energética:** ofrece información de modelos de electrodomésticos y sus
  características de eficiencia.
- **Análisis:** documenta el origen de los datos, las variables usadas, las métricas conocidas
  y las limitaciones de los modelos.

## Modelos de aprendizaje automático

Los artefactos se encuentran en `modelos/` y se cargan para predecir; la aplicación no los
entrena nuevamente:

| Modelo | Uso | Métricas documentadas |
|---|---|---|
| KNN con `StandardScaler` (k = 25) | Estimar el consumo de las próximas 24 horas | MAE: 4,57 kWh; R²: 0,31 |
| GaussianNB | Clasificar si se supera la meta diaria de aproximadamente 25,9 kWh | Exactitud: 0,74; recall: 0,63 |

Las métricas disponibles son referencias del proceso de evaluación descrito en la documentación.
En el repositorio no está el flujo de entrenamiento completo ni información suficiente para
reproducir esa evaluación de forma independiente.

### Limitaciones principales de la predicción

1. Los modelos se entrenaron con mediciones de **un solo hogar de Sceaux, Francia**, entre 2006
   y 2010. No representan una muestra de hogares argentinos.
2. La entrada imputa variables que la aplicación no mide: historial de la semana anterior,
   energía reactiva, factor de potencia y voltaje. Las temperaturas se ingresan manualmente.
3. La meta diaria se basa en el hogar de referencia y puede ser alta para muchas viviendas.
4. El clasificador recibe actualmente un factor de potencia fijo de **0,95**. El proyecto
   documenta que este supuesto puede hacer que responda “no te pasás” incluso en situaciones de
   exceso; por eso, su clasificación y el semáforo combinado requieren cautela.
5. El error medio de la regresión es relevante cerca de la meta, y se documenta que puede
   sobreestimar consumos muy bajos.

## Datos y fuentes

- Los modelos de consumo se basan en el dataset UCI *Individual Household Electric Power
  Consumption*.
- El catálogo de eficiencia contiene modelos registrados en Australia y Nueva Zelanda; sus
  valores no equivalen necesariamente a los de productos vendidos o ensayados en Argentina.
- Las tarifas residenciales se preparan a partir de cuadros oficiales de EDEA/OCEBA.
- El catálogo de consumos de electrodomésticos combina datos de referencia y supuestos; no todos
  los valores son mediciones de una vivienda concreta.

## Pruebas y validación

El repositorio contiene pruebas automatizadas para el cálculo y la lectura de facturas en
`tests/`. En este relevamiento no se ejecutó la suite, por lo que no se afirma aquí que pase en
el entorno actual. Tampoco se encontró una prueba automatizada específica de la calidad
predictiva, la preparación de variables o la compatibilidad de los modelos con hogares locales.

## Próximos pasos recomendados

1. Revisar y resolver el problema del factor de potencia fijo que afecta al clasificador.
2. Separar y documentar con precisión el flujo de entrenamiento, validación y prueba; conservar
   métricas reproducibles y baselines.
3. Evaluar las predicciones con datos de más hogares y, de ser posible, con mediciones locales.
4. Revisar cómo se construyen las variables de entrada y comunicar claramente qué datos son
   supuestos.
5. Ejecutar y mantener las pruebas automatizadas para los cálculos, las facturas y el flujo de
   predicción.

Para instrucciones de ejecución, fuentes y una lista de pendientes mantenida por el proyecto,
consultar `EJECUTAR.md`, `datos/FUENTES.md` y `README_PENDIENTES.md`, respectivamente.
