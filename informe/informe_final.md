# Informe final - TP Integrador de Aprendizaje Automático

**Proyecto:** "¿Me paso o no me paso?" - Asistente de consumo eléctrico para el hogar
**Integrantes:** Bulggiani · Campos · Guzman · Maidana
**Fecha:** 2026

---

## 1. El problema y el usuario

El usuario residencial consume a ciegas: conoce su consumo cuando llega la factura, uno o dos meses
después, cuando ya no puede corregir nada. Pasarse de su meta, del bloque subsidiado o tener un
coseno φ bajo encarecen la factura.

**Usuario de la predicción:** el titular del hogar, a través de una aplicación web.
**Decisión que permite tomar:** al ver la alerta "te pasás", postergar lavarropas, secarropas,
lavavajillas, termotanque, calefacción o aire; si el cos φ está en zona de recargo, revisar los
artefactos con motores o compresores y evaluar un capacitor.

**Momento de la predicción:** cualquier hora del día. Se usa todo lo medido hasta ese instante y se
estiman las **24 horas siguientes**.

## 2. Datos

- **Fuente:** UCI, *Individual Household Electric Power Consumption* (CC BY 4.0) — un hogar en
  Sceaux, Francia, dic. 2006 – nov. 2010 — cruzado con la **temperatura** diaria de Open-Meteo.
- **Volumen:** 2.075.259 mediciones por minuto. Tras agregar por hora: **34.151 horas** válidas
  (se descartan 438 con cobertura < 75% de minutos). Tras construir el objetivo: **33.936 filas**.
- **Unidad de análisis:** un momento de consulta (una fila por hora).
- **Diccionario y transformaciones:** ver `datos/README.md`.

### Preparación
- Faltantes (`?`, ~1,25%) tratados como NaN; horas con muy pocos minutos medidos descartadas.
- Energía: potencia media por hora ≈ kWh de esa hora; submedidores (Wh por minuto) sumados y pasados a kWh.
- Cos φ del período = P / √(P² + Q²) con las **energías sumadas** (como factura la distribuidora).

## 3. Objetivos y umbral

- **Variable numérica:** energía activa de las próximas 24 h (kWh).
- **Variable binaria:** `me_paso = 1` si esa energía supera la **meta diaria**.
- **Umbral (meta diaria):** promedio diario del **conjunto de entrenamiento = 25,92 kWh**. Se calcula
  solo con entrenamiento y luego queda fijo. Alerta: "en las próximas 24 h vas a consumir más que en tu día típico".

## 4. Fuga de información y protocolo

**Descartado por fuga:** `Global_intensity` (potencia/voltaje = objetivo disfrazado); toda medición de
horas futuras (potencia, reactiva, submedidores, cos φ); la fecha como número continuo.

**Protocolo:** separación **cronológica** en entrenamiento / validación / prueba con un **hueco de 48 h**,
porque las ventanas de 24 h consecutivas comparten 23 de 24 horas. El test se reserva para el final y el
modelo se elige con validación. Escalado dentro del `Pipeline`.

| Bloque | Período | Filas |
|---|---|---|
| Entrenamiento | 2006-12-24 → 2009-09-15 | 23.755 |
| Validación | 2009-09-17 → 2010-04-19 | 5.042 |
| Prueba | 2010-04-21 → 2010-11-25 | 5.043 |

## 5. Baselines

| Baseline | Resultado (validación) |
|---|---|
| DummyRegressor (media) | MAE 6,39 · RMSE 8,24 · R² −0,34 |
| DummyClassifier (estratificado) | acc 0,50 · prec 0,73 · rec 0,49 · F1 0,59 |

## 6. Regresión

Se compararon DummyRegressor, DecisionTreeRegressor (varias profundidades) y KNeighborsRegressor con
StandardScaler dentro de un Pipeline (k = 5, 15, 25). Se eligió con validación y se reentrenó con
entrenamiento + validación.

| Modelo (validación) | MAE | RMSE | R² |
|---|---|---|---|
| **KNN k=25** | **5,83** | 7,73 | −0,18 |
| DecisionTree depth=3 | 5,84 | 7,53 | −0,12 |
| DummyRegressor | 6,39 | 8,24 | −0,34 |

**Test del modelo elegido (KNN k=25):** MAE **4,57 kWh**, RMSE 6,06, R² **0,31**.
Residuos: media −0,65, desvío 6,03, p5 −10,06, p95 +8,72.

- **¿El modelo supera al baseline?** Sí: reduce el MAE de 6,39 a 4,57 kWh en test.
- **¿Qué significa el MAE?** La app se equivoca en promedio ± 4,6 kWh por día; con la tarifa asumida
  de 150 $/kWh son aproximadamente ± $690 por día.

## 7. Clasificación

Se compararon DummyClassifier, DecisionTreeClassifier (varias profundidades), KNeighborsClassifier
(Pipeline + StandardScaler) y GaussianNB.

| Modelo (validación) | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| **GaussianNB** | 0,757 | 0,768 | 0,951 | 0,850 |
| DecisionTree depth=5 | 0,758 | 0,778 | 0,932 | 0,848 |
| DecisionTree depth=3 | 0,765 | 0,798 | 0,904 | 0,847 |
| DummyClassifier | 0,501 | 0,732 | 0,489 | 0,586 |

**Test del modelo elegido (GaussianNB):** accuracy 0,74 · precision 0,61 · recall 0,63 · F1 0,62.
Matriz de confusión: TN 2666, FP 680, FN 630, TP 1067.

## 8. Comparación integrada (mismos casos de test)

| Sistema | Accuracy | Precision | Recall | F1 | FP | FN |
|---|---|---|---|---|---|---|
| Clasificador directo | 0,740 | 0,611 | 0,629 | 0,620 | 680 | 630 |
| Regresión + umbral | 0,741 | 0,614 | 0,621 | 0,617 | 662 | 644 |

**Esquema de costos 3:1** (un FN cuesta 3× un FP, porque el exceso se paga a precio pleno y agrava el
recargo por cos φ; el FP solo cuesta comodidad).

| Sistema | Costo (3·FN + FP) |
|---|---|
| Clasificador directo | 2.570 |
| Regresión + umbral | 2.594 |

Los dos sistemas son prácticamente equivalentes y coinciden en el 83,6% de los casos. Los desacuerdos
(16,4%) caen en un **84% dentro de la zona gris** (|predicho − meta| ≤ MAE): el sistema de alerta solo
diverge cuando el caso está cerca del umbral.

### Preguntas del informe (desde el usuario)

- **¿Qué modelo detecta mejor los casos críticos?** El clasificador directo (GaussianNB), que prioriza el recall.
- **¿Qué errores son más costosos?** Los falsos negativos: son plata y el recargo por cos φ los agrava.
- **¿Qué pasa cerca del umbral?** Se concentran los desacuerdos; por eso la app muestra una "zona gris".
- **¿Buen MAE y mala clasificación?** Sí: errores chicos cerca de la meta cambian la alerta.
- **¿Qué sistema recomiendan?** El de menor costo total (aquí el clasificador directo, por muy poco) sin
  que la precisión caiga al punto de que el usuario ignore las alertas.
- **¿Cuándo no usarlo?** En otro hogar sin reentrenar, con artefactos nuevos, sin los datos de las últimas
  24 h, o para reclamar formalmente un recargo.

## 9. Tarea complementaria - comparador estacional de enero

Se compara el gasto del mes de **enero** de los últimos años y se estima el **enero de 2011** (el siguiente
al dataset). Modelo diario con calendario + rezago largo (`kwh_year_ago`), validado en enero 2010.

| Modelo (validación: enero 2010) | MAE | RMSE |
|---|---|---|
| **KNN k=5** | **5,22** | 7,59 |
| DecisionTree depth=5 | 6,48 | 7,88 |
| Regresión lineal | 7,41 | 9,07 |
| Estacional ingenuo (año anterior) | 10,34 | 12,19 |

| Año | Días | kWh | kWh/día | Costo (150 $/kWh) | Var.% |
|---|---|---|---|---|---|
| 2007 | 31 | 1150,3 | 37,11 | $172.545 | — |
| 2008 | 31 | 1086,2 | 35,04 | $162.933 | −5,6% |
| 2009 | 31 | 1049,2 | 33,85 | $157.383 | −3,4% |
| 2010 | 28 | 958,1 | 34,22 | $143.712 | +1,1% |
| **2011 (estimado)** | 31 | **1074,5** | 34,66 | $161.173 | +1,3% |

**Enero 2011 estimado: 1074,5 kWh (±42,3 kWh)**, aproximadamente $161.173 con la tarifa asumida.

## 10. La aplicación

Flask (`app.py`) que carga los Pipelines ya entrenados con `joblib` y ejecuta `predict`. No reentrena ni
usa base de datos. Incluye formulario, validación de rangos, predicción numérica, las dos alertas,
coincidencia/zona gris, cos φ medido, costo estimado y el comparador de enero. Publicada en Vercel
(URL: _completar tras el despliegue_).

## 11. Limitaciones

- Un solo hogar (Sceaux, Francia 2006–2010): no generaliza a otra vivienda sin reentrenar.
- Solo hay 4 eneros completos: el pronóstico de un mes entero es de baja confianza; se reporta con su rango.
- La temperatura se usa como valor real (simplificación declarada).
- El costo en pesos depende de una tarifa asumida, no del dataset.
- Cambios de hábito (concept drift) y vacaciones generan falsos positivos (errores baratos).
- No sirve para reclamar formalmente un recargo: vale la medición de la distribuidora.
