# Pendientes para completar el proyecto

**Corte:** 30 de octubre de 2026  
**Proyecto:** ¿Me paso o no me paso?

Este documento resume lo que falta según la comparación entre
[`README_PENDIENTES.md`](README_PENDIENTES.md) y
[`Consigna_TP_Integrador_Aprendizaje_Automatico.docx`](Consigna_TP_Integrador_Aprendizaje_Automatico.docx).
El detalle del trabajo terminado en las prioridades completadas está en
[`PRIORIDADES_COMPLETADAS.md`](PRIORIDADES_COMPLETADAS.md).

## Prioridad 1: completar la evidencia de aprendizaje automático

**Estado: completada.** El flujo ejecutable está en
[`notebooks/entrenamiento_modelos.ipynb`](notebooks/entrenamiento_modelos.ipynb) y su implementación
en [`entrenamiento_modelos.py`](entrenamiento_modelos.py). La preparación, el umbral, la
separación temporal, los modelos, las métricas, los errores y la recomendación están documentados
en [`explicaciones/README_ANALISIS.md`](explicaciones/README_ANALISIS.md) y
[`informe.md`](informe.md). El notebook entrena/evalúa candidatos en memoria y no sobrescribe los
modelos usados por la aplicación.

## Prioridad 2: resolver la tecnología y el despliegue

**Estado: completada (despliegue y prueba en teléfono).** La tecnología Streamlit fue aceptada
por el curso y la app está publicada en
<https://me-paso-consumo-energia-tiago.streamlit.app/> desde `main`, con Python 3.12. El usuario
confirmó que se ve bien en teléfonos.

**Seguimiento posterior:** **Análisis** todavía muestra un error porque falta
`explicaciones/README_ANALISIS.md` en `main`. Al subir ese archivo y los demás cambios pendientes,
Community Cloud debería redeplegar y corregirlo; todavía falta comprobarlo en la URL publicada.
También queda verificar modelos/dependencias y decidir si se necesita almacenamiento persistente
para las casas guardadas. La guía está en [`EJECUTAR.md`](EJECUTAR.md); el estado local de `tiago2`
contiene cambios aún no subidos.

## Prioridad 3: completar los entregables

La entrega final solicita repositorio, notebook, modelos, aplicación publicada, informe,
presentación, bitácora y distribución de tareas. El notebook de entrenamiento y evaluación ya se
incorporó en la Prioridad 1; todavía falta confirmar o agregar la presentación, la bitácora y la
distribución de tareas.

## Pendientes funcionales del proyecto

Estos puntos están anotados en [`README_PENDIENTES.md`](README_PENDIENTES.md); no todos son
requisitos explícitos de la consigna:

- Revisar el factor de potencia fijo de 0,95 que afecta al clasificador. Estimar el cos φ de la
  vivienda, mostrarlo y usarlo en las variables del modelo. Investigar la norma de OCEBA antes de
  calcular un posible recargo.
- Probar el escaneo y el código de barras con una factura real de EDEA.
- Decidir cómo persistir las casas guardadas cuando la aplicación se publique.
- Evaluar el uso de temperatura real, explicar las limitaciones de la predicción para casas de
  bajo consumo y agregar pruebas automáticas para la preparación de variables y los modelos.
- Revisar valores estacionales y supuestos del catálogo, controles de uso y diferencias entre el
  precio estimado por electrodoméstico y la factura calculada.

## Orden sugerido

1. Confirmar con el docente los requisitos de Flask y Vercel.
2. Recuperar o preparar el notebook y dejar reproducible la evaluación completa.
3. Completar las comparaciones, métricas, análisis de errores y costos.
4. Completar informe, presentación, bitácora y distribución de tareas.
5. Corregir y verificar **Análisis** en la app publicada; comprobar modelos y dependencias.
6. Abordar los pendientes funcionales restantes según su prioridad.
