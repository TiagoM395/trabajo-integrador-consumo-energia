# Explicación completa del TP Integrador
## “¿Me paso o no me paso?” — Asistente de consumo eléctrico para el hogar

> Este documento explica **todo** el trabajo: qué problema resuelve, qué datos usa, cómo los prepara, qué modelos entrena, cómo los evalúa, cómo se comparan, cómo funciona la aplicación y qué limitaciones tiene. Está pensado para que puedas entenderlo y defenderlo sin depender de leer el notebook línea por línea.

---

## Índice

1. [Resumen en 60 segundos](#1-resumen-en-60-segundos)
   - [Conceptos básicos: regresión, clasificación y métricas](#conceptos-básicos-regresión-clasificación-y-métricas)
2. [El problema, contado desde el usuario](#2-el-problema-contado-desde-el-usuario)
3. [Qué pide la consigna y cómo se cumple](#3-qué-pide-la-consigna-y-cómo-se-cumple)
4. [Los datos](#4-los-datos)
5. [De 2 millones de filas a una tabla de 33.936](#5-de-2-millones-de-filas-a-una-tabla-de-33936)
6. [Las 16 variables predictoras](#6-las-16-variables-predictoras)
7. [Fuga de información: el error que hay que evitar](#7-fuga-de-información-el-error-que-hay-que-evitar)
8. [La variable objetivo y el umbral](#8-la-variable-objetivo-y-el-umbral)
9. [División temporal: train, validación y test](#9-división-temporal-train-validación-y-test)
10. [Baselines: el “modelo tonto” de comparación](#10-baselines-el-modelo-tonto-de-comparación)
11. [Regresión: ¿cuánto voy a consumir?](#11-regresión-cuánto-voy-a-consumir)
12. [Clasificación: ¿me paso o no?](#12-clasificación-me-paso-o-no)
13. [Comparación integrada y costos](#13-comparación-integrada-y-costos)
14. [El coseno φ (factor de potencia)](#14-el-coseno-φ-factor-de-potencia)
15. [Comparador estacional de enero](#15-comparador-estacional-de-enero)
16. [La aplicación web](#16-la-aplicación-web)
17. [Despliegue en Vercel](#17-despliegue-en-vercel)
18. [Reproducibilidad](#18-reproducibilidad)
19. [Qué hace cada archivo del repositorio](#19-qué-hace-cada-archivo-del-repositorio)
20. [Limitaciones y riesgos](#20-limitaciones-y-riesgos)
21. [Las 8 preguntas del informe, respondidas](#21-las-8-preguntas-del-informe-respondidas)
22. [Números clave para memorizar](#22-números-clave-para-memorizar)
23. [Preguntas probables de defensa](#23-preguntas-probables-de-defensa)
24. [Glosario](#24-glosario)
25. [Cómo ejecutar el trabajo paso a paso](#25-cómo-ejecutar-el-trabajo-paso-a-paso)
26. [Checklist contra la consigna](#26-checklist-contra-la-consigna)
27. [Detalles a corregir o mejorar antes de la entrega](#27-detalles-a-corregir-o-mejorar-antes-de-la-entrega)
28. [Pitch final de 60 segundos](#28-pitch-final-de-60-segundos)

---

## 1. Resumen en 60 segundos

El trabajo usa las mediciones minuto a minuto de **un hogar real en Sceaux, Francia** (diciembre 2006 – noviembre 2010) para responder dos preguntas que se hace cualquier persona que paga la luz:

| Pregunta | Tarea de machine learning | Salida |
|---|---|---|
| ¿Cuánta energía voy a consumir en las próximas 24 horas? | **Regresión** | Un número: kWh |
| ¿Me voy a pasar de mi meta diaria? | **Clasificación** | Sí / No |

Además, la alerta “te pasás” se genera de **dos maneras** y se comparan:

1. **Clasificador directo:** un modelo que responde directamente sí o no.
2. **Regresión + umbral:** primero estima los kWh y después los compara con la meta.

Eso es la **comparación obligatoria** de la consigna.

Como extras, el trabajo agrega:

- Un **indicador de coseno φ** (factor de potencia) para avisar si hay riesgo de recargo en la factura.
- Un **costo estimado en pesos** (con una tarifa configurable).
- Una **zona gris** alrededor de la meta, para avisar cuando la alerta es poco confiable.
- Un **comparador estacional**: cuánto se gastó en enero de cada año y cuánto se estima para enero de 2011.
- Una **aplicación web en Flask**, publicable en Vercel, que carga los modelos ya entrenados y hace predicciones con datos nuevos.

**Resultado principal:** el mejor regresor es un **KNN con k=25** (MAE 4,57 kWh por día en test) y el mejor clasificador es **GaussianNB** (accuracy 0,740; recall 0,629). Los dos sistemas de alerta son casi equivalentes: coinciden en el **83,6 %** de los casos y, cuando no coinciden, el **84 %** de las veces es porque el caso está cerca de la meta (zona gris).

---

## Conceptos básicos: regresión, clasificación y métricas

> Si nunca trabajaste con machine learning, esta es la sección más importante del documento. Explica desde cero qué es un modelo, qué diferencia hay entre regresión y clasificación, qué significa cada métrica y cómo funcionan KNN y GaussianNB. Si ya los conocés, podés saltearla y volver cuando necesites repasar un término.

### A.1 ¿Qué es un modelo?

Un **modelo** es una función que aprende a partir de ejemplos:

```text
entrada (datos del medidor, calendario, clima)  →  salida (kWh o sí/no)
```

La idea es la misma que aprende una persona con experiencia: si vio muchos martes a las 19:00 con la heladera y el aire prendidos, puede estimar cuánto se va a consumir un martes a las 19:00. El modelo hace eso, pero con números y de forma sistemática.

Conviene distinguir tres palabras que se usan todo el tiempo:

| Palabra | Qué es | En este trabajo |
|---|---|---|
| **Algoritmo** | La receta o el método | KNN, árbol de decisión, GaussianNB |
| **Modelo** | La receta ya entrenada, con sus números | El `.pkl` que carga la app |
| **Entrenamiento** | El proceso de ajustar el modelo con ejemplos | Lo que hace el notebook |
| **Predicción** | Aplicar el modelo a un caso nuevo | Lo que hace la app cuando el usuario aprieta “Predecir” |

**En criollo:** el algoritmo es la receta de cocina; el modelo es el plato ya cocinado; entrenar es cocinar; predecir es servirle el plato a un cliente nuevo.

Todos los modelos de este trabajo usan las **mismas 16 entradas**. En la etapa de comparación se entrenan con los **23.755 momentos de entrenamiento**; después, el modelo ganador se reentrena con **entrenamiento + validación** (28.797 momentos) antes de la evaluación final en test. Lo que cambia entre un modelo de regresión y uno de clasificación es **qué salida aprenden a producir**.

### A.2 Los dos tipos de modelos de este trabajo

|  | **Regresión** | **Clasificación** |
|---|---|---|
| Pregunta | ¿Cuánto? | ¿De qué clase? |
| Salida | Un número continuo | Una categoría discreta |
| Ejemplo | “27,4 kWh en las próximas 24 h” | “Te pasás: sí / no” |
| Variable objetivo | `y_reg` (kWh) | `me_paso` (0 o 1) |
| Métricas | MAE, RMSE, R² | Accuracy, precision, recall, F1, matriz de confusión |
| Modelo elegido | **KNN k=25** | **GaussianNB** |

La clave: son **dos miradas del mismo fenómeno**. Usan las mismas filas y las mismas variables, pero una aprende a estimar el número y la otra aprende directamente la respuesta sí/no.

### A.3 ¿Qué es un modelo de regresión?

Un **modelo de regresión** predice un **número**. No dice “te pasás” ni “no te pasás”: dice **cuánto**.

En este trabajo:

```text
entrada: 16 variables medidas hasta el momento de la consulta
salida:  kWh que se van a consumir en las próximas 24 horas
modelo:  KNN k=25
```

Ejemplo: el modelo recibe los datos de un martes a las 19:00 y responde **“27,4 kWh”**. Después, la app compara ese número con la meta (25,92 kWh) y concluye “te pasás”. Pero esa conclusión es una **regla posterior**, no la salida del regresor.

**Cómo aprende:** ajusta sus parámetros para que sus predicciones se parezcan lo más posible a los valores reales. El error se mide con MAE, RMSE y R².

**Por qué se usa acá:** porque el usuario no solo quiere saber si se pasa, también quiere saber **por cuánto** y **cuánta plata** representa. Eso solo lo da un número.

### A.4 ¿Qué es un modelo de clasificación?

Un **modelo de clasificación** predice una **categoría**. En este trabajo hay dos clases:

```text
0 = no me paso de la meta
1 = me paso de la meta
```

En este trabajo:

```text
entrada: las mismas 16 variables
salida:  clase 0 o clase 1
modelo:  GaussianNB
```

Ejemplo: el modelo recibe los datos del mismo martes a las 19:00 y responde directamente **“1”** (te pasás), sin pasar por el número.

**Cómo aprende:** busca una frontera (o una probabilidad) que separe los casos de clase 0 de los de clase 1. GaussianNB, en particular, estima la probabilidad de cada clase y elige la más probable.

**Por qué se usa acá:** porque a veces lo único que el usuario necesita es la alerta rápida. Además, permite cumplir la comparación obligatoria: ¿conviene predecir la clase directamente o predecir el número y después aplicar el umbral?

#### No confundir los dos umbrales

Hay dos umbrales distintos y es fácil mezclarlos:

1. **El umbral del problema:** la meta diaria de **25,92 kWh**. Define si una fila es clase 1 o clase 0. Es una decisión del negocio, no del algoritmo.
2. **El umbral interno del clasificador:** cuando GaussianNB calcula probabilidades, `predict` elige la clase más probable. En un problema binario, eso equivale a cortar en **0,5**: si la probabilidad de “me pasás” es mayor que 0,5, predice 1.

El primero es “la meta del usuario”. El segundo es “cómo decide el modelo”. No son lo mismo.

### A.5 MAE: el error promedio en kWh

**MAE** significa *Mean Absolute Error* (error absoluto medio). Responde:

> “En promedio, ¿por cuánto me equivoco, sin importar si me quedé corto o me pasé?”

Fórmula:

```text
MAE = (1/n) × Σ |valor_real − valor_predicho|
```

Ejemplo con cuatro días:

| Día | Real | Predicho | Error (predicho − real) | Error absoluto |
|---|---|---|---|---|
| 1 | 25 | 28 | +3 | 3 |
| 2 | 30 | 25 | −5 | 5 |
| 3 | 22 | 24 | +2 | 2 |
| 4 | 27 | 31 | +4 | 4 |

```text
MAE = (3 + 5 + 2 + 4) / 4 = 14 / 4 = 3,5 kWh
```

**En este trabajo:** MAE = **4,57 kWh**. Significa que la app se equivoca, en promedio, **±4,57 kWh por día**.

Traducido a plata, con la tarifa asumida de 150 $/kWh:

```text
4,57 kWh × 150 $/kWh ≈ 685 $ por día
```

**Por qué se eligió el modelo por MAE:** porque está en las mismas unidades que el problema (kWh) y se traduce directamente a pesos. Es fácil de explicar y no exagera el efecto de un caso raro.

**Limitación:** trata todos los errores igual. Un error de 1 kWh y uno de 10 kWh pesan 1 y 10, pero no castiga especialmente los errores grandes. Para eso está el RMSE.

### A.6 RMSE: el error que castiga los errores grandes

**RMSE** significa *Root Mean Squared Error* (raíz del error cuadrático medio).

Fórmula:

```text
RMSE = sqrt( (1/n) × Σ (valor_real − valor_predicho)² )
```

Con el mismo ejemplo:

```text
RMSE = sqrt( (3² + 5² + 2² + 4²) / 4 )
     = sqrt( (9 + 25 + 4 + 16) / 4 )
     = sqrt( 54 / 4 )
     = sqrt( 13,5 )
     ≈ 3,67 kWh
```

Fijate que el RMSE (3,67) es mayor que el MAE (3,5) porque los errores grandes pesan más al elevarlos al cuadrado. Cuanto más grande sea la diferencia entre RMSE y MAE, más errores grandes hay.

**En este trabajo:** RMSE = **6,06 kWh**, mayor que el MAE de 4,57. Eso indica que existen algunos errores grandes, no solo errores chicos.

**En criollo:** el MAE es “el error típico”; el RMSE es “el error típico, pero poniendo el foco en los papelones”.

### A.7 R²: cuánto de la variabilidad se explica

**R²** (coeficiente de determinación) responde:

> “¿Cuánto mejor soy que predecir siempre el promedio?”

Fórmula:

```text
R² = 1 − Σ(real − predicho)² / Σ(real − promedio)²
```

Interpretación:

| R² | Significado |
|---|---|
| **1** | Predicción perfecta |
| **0** | Tan bueno como predecir siempre el promedio |
| **Entre 0 y 1** | Explica esa proporción de la variabilidad |
| **Negativo** | Peor que predecir siempre el promedio |

**En este trabajo:**

- R² en test = **0,308** → el modelo explica el **30,8 %** de la variabilidad del consumo.
- R² en validación = **−0,175** → en ese período fue peor que el promedio, porque el nivel de consumo cambió (invierno) y el modelo quedó descalibrado.

**Por qué no alcanza el R²:** un R² bajo no siempre significa un modelo inútil. Si el objetivo es avisar si se supera una meta, el MAE y el recall pueden ser más relevantes que explicar toda la variabilidad.

### A.8 Accuracy: el porcentaje de aciertos

**Accuracy** (exactitud) responde:

> “De todos los casos, ¿qué porcentaje respondí bien?”

Fórmula:

```text
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

**En este trabajo:**

```text
Accuracy = (2.666 + 1.067) / 5.043
         = 3.733 / 5.043
         = 0,740
```

Es decir, **74,0 %** de los casos de test fueron clasificados correctamente.

**El problema de la accuracy:** puede ser alta y el modelo ser inútil. Ejemplo: en test hay 3.346 casos de clase 0 y 1.697 de clase 1. Un modelo que **siempre** diga “no te pasás” acertaría 3.346 de 5.043 = **66,3 %**. Parece “bastante bueno”, pero **nunca detecta un solo caso crítico**. Por eso no se usa accuracy sola.

### A.9 Precision: cuando alerta, ¿cuánto acierta?

**Precision** (precisión) responde:

> “De todos los casos en los que dije ‘te pasás’, ¿qué porcentaje realmente se pasó?”

Fórmula:

```text
Precision = TP / (TP + FP)
```

**En este trabajo:**

```text
Precision = 1.067 / (1.067 + 680)
          = 1.067 / 1.747
          = 0,611
```

Es decir, **61,1 %**. De 1.747 alertas, 1.067 fueron correctas y **680 fueron falsas alarmas**.

**En criollo:** precision alta = cuando la app molesta, tiene razón.

### A.10 Recall: de los casos críticos, ¿cuántos detecta?

**Recall** (sensibilidad o exhaustividad) responde:

> “De todos los casos que realmente se pasaron, ¿qué porcentaje detecté?”

Fórmula:

```text
Recall = TP / (TP + FN)
```

**En este trabajo:**

```text
Recall = 1.067 / (1.067 + 630)
       = 1.067 / 1.697
       = 0,629
```

Es decir, **62,9 %**. De 1.697 casos que realmente se pasaron, detectó 1.067 y **se le escaparon 630**.

**En criollo:** recall alto = no se le escapan los casos críticos. Para este problema es la métrica más importante, porque un caso escapado cuesta plata.

### A.11 F1: el equilibrio entre precision y recall

**F1** combina precision y recall en un solo número. Es la **media armónica**, no la media común:

```text
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

**En este trabajo:**

```text
F1 = 2 × (0,611 × 0,629) / (0,611 + 0,629)
   ≈ 0,620
```

**¿Por qué media armónica?** Porque castiga los extremos. Si un modelo tiene precision 1,0 y recall 0,0, la media común daría 0,5 (parece aceptable), pero la media armónica da 0 (refleja que el modelo es inútil para detectar casos). F1 solo es alto cuando **ambas** son razonablemente altas.

### A.12 FP y FN: los dos errores que importan

En clasificación binaria, “positivo” es la clase que nos interesa detectar. Acá:

```text
positivo = 1 = “me paso de la meta”
negativo = 0 = “no me paso”
```

La matriz de confusión de este trabajo, con **filas = real** y **columnas = predicho**:

|  | Predicho 0 | Predicho 1 |
|---|---|---|
| **Real 0** | **TN = 2.666** | **FP = 680** |
| **Real 1** | **FN = 630** | **TP = 1.067** |

| Sigla | Nombre | Qué pasó | Historia del usuario |
|---|---|---|---|
| **TP** | Verdadero positivo | Dijo “te pasás” y se pasó | Acertó la alerta |
| **TN** | Verdadero negativo | Dijo “no te pasás” y no se pasó | Acertó la tranquilidad |
| **FP** | Falso positivo | Dijo “te pasás” y **no** se pasó | Postergó el lavarropas o pasó frío sin necesidad: perdió **comodidad** |
| **FN** | Falso negativo | Dijo “no te pasás” y **sí** se pasó | No cambió nada: pagó el exceso a precio pleno y, si el cos φ es bajo, el recargo se calcula sobre una factura más grande. Perdió **plata** |

**En este trabajo:** 680 FP y 630 FN. Por eso el costo se define como:

```text
costo = 3 × FN + FP = 3 × 630 + 680 = 2.570
```

El FN pesa 3 porque cuesta plata real; el FP pesa 1 porque cuesta comodidad.

**Ojo:** si se invirtiera la definición de “positivo” (por ejemplo, positivo = “no me paso”), FP y FN se intercambiarían. Siempre hay que decir cuál es la clase positiva.

### A.13 KNN: los K vecinos más cercanos

**KNN** significa *K-Nearest Neighbors* (“los K vecinos más cercanos”). Es uno de los modelos más intuitivos que existen.

**La idea:** para predecir un caso nuevo, buscar en la historia los **K casos más parecidos** y usar lo que pasó con ellos.

- En **regresión**: se promedian los valores de esos vecinos.
- En **clasificación**: se vota la clase mayoritaria (o se promedian las probabilidades).

**Analogía:** querés saber cuánto va a consumir un martes a las 19:00. Buscás los 25 martes a las 19:00 más parecidos de la historia (por consumo reciente, semana anterior, clima, etc.) y promediás lo que consumieron en las 24 h siguientes. Ese promedio es la predicción.

**Qué significa “parecido”:** se mide con una **distancia** (normalmente euclidiana) entre las 16 variables del caso nuevo y las de cada caso histórico.

**Por qué hace falta escalar:** si una variable está en kWh (0 a 40) y otra es la hora (0 a 23), la distancia quedaría dominada por la variable de mayor escala. El `StandardScaler` lleva todas a una escala comparable (media 0, desvío 1). Por eso el KNN va dentro de un `Pipeline` con `StandardScaler`.

**Qué pasa con K:**

| K | Efecto |
|---|---|
| **Muy chico** (ej. 5) | Muy sensible al ruido; puede “copiar” un caso raro |
| **Muy grande** (ej. 100) | Demasiado suave; mezcla casos que no se parecen |
| **Intermedio** (ej. 25) | Buen equilibrio |

**En este trabajo:**

- Regresión: se probaron K = 5, 15 y 25. Ganó **K = 25** (MAE 5,831 en validación; K=5 daba 6,946).
- Clasificación: también se probó KNN, pero ganó GaussianNB. KNN k=25 quedó cerca (F1 0,826 en validación vs 0,850 de GaussianNB).
- Estacional: se usó **K = 5**, porque el problema diario tiene menos datos y necesita reaccionar más.

**Ventajas:** simple, no supone una forma específica de la relación, se adapta a patrones nuevos.

**Desventajas:** guarda todos los datos de entrenamiento, predice más lento con muchos registros, es sensible a la escala y a variables irrelevantes, y sufre la “maldición de la dimensionalidad” cuando hay muchas variables.

### A.14 GaussianNB: Naive Bayes con distribución normal

**GaussianNB** es un clasificador basado en el **teorema de Bayes**. La idea es estimar:

```text
P(clase | datos) ∝ P(clase) × P(datos | clase)
```

En palabras:

- **P(clase):** ¿qué tan frecuente es cada clase? (prior)
- **P(datos | clase):** si el caso es de esa clase, ¿qué tan probables son estos valores? (verosimilitud)
- **P(clase | datos):** ¿qué tan probable es cada clase dado lo que veo? (posterior)

El modelo calcula eso para clase 0 y clase 1, y elige la más probable.

**¿Por qué “Naive” (ingenuo)?** Porque supone que las variables son **independientes entre sí** dada la clase. Es un supuesto fuerte y casi siempre falso: por ejemplo, `active_24` y `reactive_24` están correlacionadas. Aun así, el modelo suele funcionar bien en la práctica.

**¿Por qué “Gaussian”?** Porque supone que, dentro de cada clase, cada variable sigue una **distribución normal** (campana de Gauss). Para entrenar, estima la media y el desvío de cada variable en cada clase. No necesita más.

**Cómo predice:**

1. Calcula la probabilidad de clase 0 y de clase 1.
2. Elige la clase con mayor probabilidad.
3. En un problema binario, eso equivale a cortar en 0,5.

**En este trabajo:**

- En validación: recall **0,951**, precision 0,768, F1 **0,850**. Fue el mejor.
- En test: recall **0,629**, precision 0,611, F1 **0,620**.
- Se eligió porque prioriza **detectar los casos críticos** (recall alto), que es lo que importa cuando el FN cuesta plata.

**Ventajas:** muy rápido, funciona con pocos datos, maneja muchas variables, da probabilidades, es fácil de explicar.

**Desventajas:** el supuesto de independencia es falso; las probabilidades pueden estar mal calibradas; si hay variables redundantes, puede exagerar su influencia. Igual, para clasificar, suele ser sorprendentemente bueno.

### A.15 Árbol de decisión (para comparar)

Un **árbol de decisión** hace preguntas en cadena:

```text
¿active_24 > 28 kWh?
├── sí → ¿hace frío?
│        ├── sí → predecir “te pasás”
│        └── no → predecir “no te pasás”
└── no → ¿es fin de semana?
         ├── sí → ...
         └── no → ...
```

Cada pregunta divide los casos; cada hoja final da una predicción.

**La profundidad** (`max_depth`) controla cuántas preguntas encadena:

- Poca profundidad → modelo simple, puede quedarse corto.
- Mucha profundidad → modelo complejo, puede **memorizar** el entrenamiento y fallar con datos nuevos (**overfitting**).

**Ejemplo real de este trabajo:** el árbol sin límite de profundidad tuvo MAE 7,936 en validación, mucho peor que el de profundidad 3 (5,838). Memorizó el entrenamiento y generalizó peor. Eso es overfitting en estado puro.

### A.16 Dummy: el baseline

Un **baseline** es un modelo tonto que sirve de piso. Si tu modelo no le gana, no aporta nada.

- `DummyRegressor`: siempre predice el promedio del entrenamiento.
- `DummyClassifier`: predice clases respetando la proporción observada.

**En este trabajo:**

- Dummy regresión: MAE 6,386 (validación).
- Dummy clasificación: accuracy 0,501, F1 0,586 (validación).
- KNN: MAE 5,831 (validación, el mejor regresor).
- GaussianNB: F1 0,850 (validación, el mejor clasificador).

### A.17 Cómo se leen los resultados finales de un vistazo

| Métrica | Pregunta que responde | Valor en test | Lectura |
|---|---|---|---|
| **MAE** | ¿Cuánto me equivoco en promedio? | 4,57 kWh | ±4,57 kWh/día ≈ ±685 $/día |
| **RMSE** | ¿Cuánto me equivoco castigando errores grandes? | 6,06 kWh | Hay algunos errores grandes |
| **R²** | ¿Cuánta variabilidad explico? | 0,308 | Explica el 30,8 % |
| **Accuracy** | ¿Qué porcentaje acierto? | 0,740 | 74 % de aciertos |
| **Precision** | Cuando alerto, ¿cuánto acierto? | 0,611 | 61,1 % de las alertas son correctas |
| **Recall** | De los casos críticos, ¿cuántos detecto? | 0,629 | Detecta el 62,9 % |
| **F1** | ¿Cómo equilibro precision y recall? | 0,620 | Equilibrio razonable |
| **FP** | Falsas alarmas | 680 | Cuesta comodidad |
| **FN** | Casos críticos escapados | 630 | Cuesta plata (peso 3) |

### A.18 Las tres cosas que no hay que confundir

```text
1) MODELO DE REGRESIÓN
   16 variables → KNN → 27,4 kWh

2) REGRESIÓN + UMBRAL
   16 variables → KNN → 27,4 kWh → comparar con 25,92 → “te pasás”

3) MODELO DE CLASIFICACIÓN
   16 variables → GaussianNB → “te pasás” (directamente)
```

- La **regresión** produce un número.
- El **umbral** es una regla que convierte el número en clase.
- La **clasificación** produce la clase directamente, sin pasar por el número.

La comparación obligatoria del TP es entre **(2)** y **(3)**. La **(1)** es la regresión pura, que también se evalúa con MAE, RMSE y R².

---

## 2. El problema, contado desde el usuario

### 2.1 La situación

Una persona consume electricidad a ciegas. Se entera de cuánto gastó cuando llega la factura, uno o dos meses después, cuando ya no puede corregir nada.

Eso le importa por cuatro razones:

1. **Plata:** la tarifa eléctrica pesa cada vez más en el presupuesto familiar.
2. **Bloque subsidiado:** el subsidio cubre una cantidad limitada de kWh por mes; lo que se pasa se paga a precio pleno.
3. **Recargos por bajo factor de potencia (coseno φ):** casi nadie los conoce y pueden aparecer en la factura.
4. **Hábitos invisibles:** no sabe qué artefacto le consume más ni cuál empeora su factor de potencia.

### 2.2 Qué querría tener el usuario

Una app que, con lo que su medidor inteligente ya registró, le diga:

- cuánta energía va a consumir en las **próximas 24 horas**;
- si con ese ritmo **se pasa de su meta**;
- cómo está su **coseno φ** y si corre riesgo de recargo;
- cuánta **plata** representa todo eso.

Así puede actuar **antes**: postergar el lavarropas, bajar la calefacción o el aire, apagar el termotanque, o revisar si necesita corregir el factor de potencia.

### 2.3 Por qué “próximas 24 horas” y no “la próxima hora”

Porque el usuario razona por día: su meta es diaria, la factura es mensual y las decisiones domésticas (“hoy no pongo el lavarropas”) son diarias. Predecir la próxima hora sería más fácil, pero menos útil para decidir.

### 2.4 El momento exacto de la predicción

Este es un concepto central de la consigna:

> **La predicción se hace en cualquier momento del día, usando solamente lo que el medidor ya midió hasta ese instante. Se estiman las 24 horas siguientes.**

Ejemplo: si el usuario abre la app un martes a las 19:00, el modelo puede usar todo lo medido hasta las 19:00 (última hora, últimas 24 h, semana anterior, etc.) y debe predecir el consumo de las 24 horas que van de las 19:00 de hoy a las 19:00 de mañana.

Esto define qué variables se pueden usar y cuáles son **fuga de información** (ver sección 7).

---

## 3. Qué pide la consigna y cómo se cumple

La consigna pide, sobre un mismo dataset:

| Requisito | Cómo se cumple |
|---|---|
| Una variable numérica | Energía activa de las próximas 24 h (kWh) |
| Una clase derivada de esa variable | `me_paso = 1` si esa energía supera la meta diaria |
| Al menos 2.000 registros | 33.936 filas horarias |
| Al menos 5 predictores disponibles al predecir | 16 predictores |
| Umbral justificable | Meta diaria = promedio del entrenamiento = 25,92 kWh |
| Fuente documentada | UCI + Open-Meteo, con diccionario en `datos/README.md` |
| Preparación de datos | Limpieza, agregación horaria, ingeniería de variables, control de fugas |
| FP y FN con significado | FN cuesta plata (peso 3); FP cuesta comodidad (peso 1) |
| Privacidad | Un hogar anónimo, sin datos personales |
| Originalidad | No es un tutorial copiado: el diseño, el umbral, los costos y la app son propios |

Y pide comparar **obligatoriamente**:

- **Clasificador directo:** predice la clase 0/1.
- **Regresión + umbral:** predice el valor numérico y luego aplica el umbral.

También pide **baselines** (`DummyRegressor` y `DummyClassifier`) y ciertos **modelos obligatorios**:

- Regresión: `DecisionTreeRegressor` y `KNeighborsRegressor` con `StandardScaler` dentro de un `Pipeline`.
- Clasificación: `DecisionTreeClassifier`, `KNeighborsClassifier` con `StandardScaler` dentro de un `Pipeline` y `GaussianNB`.

Todo eso está implementado en el notebook y en la app.

---

## 4. Los datos

### 4.1 Dataset principal

- **Nombre:** *Individual Household Electric Power Consumption*.
- **Autores:** Hébrail & Bérard.
- **Fuente:** UCI Machine Learning Repository.
- **Licencia:** CC BY 4.0.
- **Contenido:** mediciones **por minuto** de un único hogar en Sceaux, Francia.
- **Período:** 16/12/2006 17:24 → 26/11/2010 21:02.
- **Filas:** 2.075.259.
- **Faltantes:** codificados como `?`, aproximadamente **1,25 %**.

### 4.2 Variables originales

| Variable | Unidad | Qué es |
|---|---|---|
| `Date` | — | Fecha (dd/mm/aaaa) |
| `Time` | — | Hora (hh:mm:ss) |
| `Global_active_power` | kW | Potencia activa promedio del minuto |
| `Global_reactive_power` | kVAr | Potencia reactiva promedio del minuto |
| `Voltage` | V | Voltaje promedio del minuto |
| `Global_intensity` | A | Intensidad promedio del minuto |
| `Sub_metering_1` | Wh | Cocina: lavavajillas, horno, microondas |
| `Sub_metering_2` | Wh | Lavadero: lavadora, secarropas, heladera, luz |
| `Sub_metering_3` | Wh | Termotanque eléctrico y aire acondicionado |

### 4.3 Dataset de clima

- **Fuente:** Open-Meteo Historical Weather API.
- **Punto:** latitud 48,78; longitud 2,29 (Sceaux, Francia).
- **Período:** 01/12/2006 → 31/03/2011 (incluye enero 2011, que se usa como referencia).
- **Variables:** `temp_max`, `temp_min`, `temp_mean` (temperatura diaria en °C).
- **Cómo se obtuvo:** ejecutando `descargar_clima.py`; el CSV quedó guardado para que el notebook sea reproducible sin internet.

**Simplificación declarada:** se usa la temperatura **real** del día como si fuera un pronóstico. En producción se reemplazaría por el pronóstico meteorológico disponible en el momento de la consulta.

### 4.4 Privacidad

El dataset no contiene datos personales identificables: es un hogar anónimo. Por eso cumple el requisito de privacidad de la consigna.

---

## 5. De 2 millones de filas a una tabla de 33.936

Esta es la parte de **preparación de datos**. El notebook la hace en varias etapas.

### 5.1 Lectura y control de calidad

1. Se lee el archivo separado por `;`, tratando `?` como valor faltante.
2. Se construye un `datetime` combinando `Date` + `Time`.
3. Se convierten las columnas numéricas a números.
4. Se controla:
   - filas crudas: **2.075.259**;
   - fechas inválidas: **0**;
   - timestamps duplicados: **0**;
   - faltantes: **1,25 %** en todas las columnas numéricas.
5. Se revisan valores imposibles:
   - voltaje fuera de [180, 260]: **0**;
   - potencias activas negativas: **0**;
   - potencias reactivas negativas: **0**;
   - intensidad negativa: **0**.

**En criollo:** los datos vienen bastante limpios, pero hay que demostrar que se revisaron. La consigna valora ese control.

### 5.2 Agregación horaria: de minutos a horas

El modelo no trabaja por minuto: trabaja por **hora**. ¿Por qué?

- Porque el objetivo es diario (24 h) y una fila por minuto sería redundante.
- Porque así cada fila representa un **momento de consulta** (“martes 19:00”).
- Porque se reduce el ruido de las mediciones instantáneas.

La conversión es la clave:

- `Global_active_power` está en **kW** (potencia media del minuto). Si se promedia durante una hora, se obtiene la **potencia media de esa hora**. Multiplicada por 1 hora, da **kWh** de esa hora.
  - Entonces: **potencia media en kW ≈ energía en kWh de esa hora**.
- `Global_reactive_power` está en **kVAr**. Su promedio horario da **kVArh** de esa hora.
- Los submedidores vienen en **Wh por minuto**. Se **suman** los 60 minutos y se dividen por 1000 para pasar a **kWh**.

> **Cuidado con la intuición:** no es que “se promedia la energía”; se promedia la potencia y, como el intervalo es de 1 hora, el número coincide con la energía de esa hora.

### 5.3 Filtro de calidad

No todas las horas tienen los 60 minutos medidos. Se calcula una **cobertura**:

```text
cobertura = cantidad de minutos con dato / 60
```

Se conservan solamente las horas con **cobertura ≥ 75 %** (al menos 45 minutos medidos).

Resultado:

- horas totales: **34.589**;
- horas conservadas: **34.151**;
- horas descartadas: **438**.

### 5.4 Ingeniería de variables

Ahora se construyen las variables que el modelo va a usar. Todas se calculan con una **ventana hacia atrás**, es decir, con información que ya pasó.

| Variable | Cómo se calcula | Qué representa |
|---|---|---|
| `kwh_h` | energía de la hora actual | consumo de la última hora |
| `active_24` | suma móvil de las últimas 24 h | energía de las últimas 24 h |
| `active_prevweek` | la misma suma, desplazada 168 h (7 días) | energía de las mismas 24 h de la semana anterior |
| `reactive_24` | suma móvil de reactiva de 24 h | energía reactiva de las últimas 24 h |
| `sub1_24`, `sub2_24`, `sub3_24` | suma móvil de 24 h de cada submedidor | cuánto consumió cada grupo de artefactos |
| `volt_24` | promedio móvil de 24 h del voltaje | voltaje típico |
| `cosphi_24` | `active_24 / sqrt(active_24² + reactive_24²)` | factor de potencia de las últimas 24 h |
| `hour` | hora del día (0–23) | hábito horario |
| `dayofweek` | día de la semana (0 = lunes) | hábito semanal |
| `month` | mes (1–12) | estacionalidad |
| `is_weekend` | 1 si sábado o domingo | diferencia fin de semana |
| `is_feriado` | 1 si es feriado fijo | día atípico |
| `temp_actual` | temperatura media del día de la consulta | clima actual |
| `temp_next24` | temperatura media del día siguiente | clima esperado |

La variable objetivo se construye así:

```python
y_reg = kwh_h.rolling(24).sum().shift(-24)
```

**Traducción:** en la fila de la hora `t`, se suma el consumo de las horas `t+1` a `t+24`. Es decir, **la energía de las próximas 24 horas**.

- La suma móvil normal (sin `shift`) mira hacia atrás: `t-23` a `t`.
- El `shift(-24)` mueve el valor 24 posiciones hacia atrás, para que en `t` quede la suma de `t+1` a `t+24`.

### 5.5 La fila del dataset final

Cada fila del dataset final representa:

> **Un momento de consulta (una hora) con todo lo medido hasta ese instante y el consumo de las 24 horas siguientes.**

Ejemplo conceptual:

| Fila | Hora de consulta | Variables de entrada | Objetivo |
|---|---|---|---|
| 1 | 2010-04-21 02:00 | todo lo medido hasta las 02:00 | kWh de 03:00 a 02:00 del día siguiente |
| 2 | 2010-04-21 03:00 | todo lo medido hasta las 03:00 | kWh de 04:00 a 03:00 del día siguiente |

Las filas se superponen: la consulta de las 19:00 y la de las 20:00 comparten 23 de las 24 horas que intentan predecir. Eso es importantísimo para el split (sección 9).

### 5.6 Números finales de la preparación

| Etapa | Cantidad |
|---|---|
| Filas crudas (por minuto) | 2.075.259 |
| Horas totales | 34.589 |
| Horas con cobertura ≥ 75 % | 34.151 |
| Filas con objetivo calculable | 34.127 |
| Filas útiles (sin NaN en features) | **33.936** |
| Predictores | **16** |

---

## 6. Las 16 variables predictoras

El modelo usa exactamente estas 16 variables, en este orden:

```text
kwh_h, active_24, active_prevweek, reactive_24, cosphi_24,
sub1_24, sub2_24, sub3_24, volt_24,
hour, dayofweek, month, is_weekend, is_feriado,
temp_actual, temp_next24
```

### 6.1 Por qué cada una

| Variable | Para qué sirve |
|---|---|
| `kwh_h` | ritmo inmediato: si la última hora fue alta, es probable que siga alta |
| `active_24` | nivel de consumo reciente; es el predictor más fuerte |
| `active_prevweek` | captura el patrón semanal: los martes se parecen a los martes |
| `reactive_24` | indica uso de motores y compresores |
| `cosphi_24` | resume la “calidad” del consumo y el tipo de cargas |
| `sub1_24`, `sub2_24`, `sub3_24` | permiten distinguir si el consumo viene de cocina, lavadero o termotanque/aire |
| `volt_24` | contexto eléctrico; también puede detectar anomalías |
| `hour` | hábitos por hora |
| `dayofweek` | hábitos por día |
| `month` | estacionalidad anual |
| `is_weekend` | diferencia sábado/domingo |
| `is_feriado` | días atípicos |
| `temp_actual` | el clima influye en calefacción y aire |
| `temp_next24` | el clima esperado influye en el consumo futuro |

### 6.2 La lógica de las features

La idea es que el consumo de las próximas 24 h depende de:

1. **Lo que pasó recientemente** (`kwh_h`, `active_24`).
2. **Lo que pasó la semana pasada a la misma hora** (`active_prevweek`), porque los hábitos son semanales.
3. **Qué artefactos se están usando** (submedidores y reactiva).
4. **El calendario** (hora, día, mes, fin de semana, feriado).
5. **El clima** (temperatura actual y prevista).

Es una combinación de **memoria corta**, **memoria semanal**, **contexto** y **estacionalidad**.

---

## 7. Fuga de información: el error que hay que evitar

### 7.1 Qué es

Hay **fuga de información** (data leakage) cuando el modelo usa, en el momento de predecir, algo que en la realidad **todavía no se conoce**. Es el equivalente a hacer trampa en un examen: los resultados parecen buenísimos, pero no sirven en producción.

### 7.2 Las fugas que se detectaron y evitaron

| Fuga | Por qué es fuga | Qué se hizo |
|---|---|---|
| Potencia, reactiva, intensidad y submedidores de horas futuras | Son parte de lo que se quiere predecir | Se usan solo ventanas hacia atrás |
| `Global_intensity` | Es potencia dividida por voltaje: el objetivo disfrazado | Se descartó |
| Fecha como número continuo | No generaliza a fechas futuras | Se usan variables de calendario (`hour`, `month`, etc.) |
| Ventanas superpuestas con split aleatorio | Filas vecinas comparten 23 de 24 horas; el test se filtra en el entrenamiento | Split cronológico con hueco |
| Umbral calculado con todos los datos | El test influiría en la definición de la clase | El umbral se calcula solo con entrenamiento |
| Escalado fuera del Pipeline | El `StandardScaler` aprendería de datos de test | El escalado va dentro del `Pipeline` |
| Elegir el modelo mirando el test | El test deja de ser una prueba honesta | Se elige con validación y el test se usa una sola vez |

### 7.3 La fuga más sutil: las ventanas superpuestas

Pensalo así:

- La fila de las 19:00 predice de 19:00 a 19:00 del día siguiente.
- La fila de las 20:00 predice de 20:00 a 20:00 del día siguiente.
- Esas dos filas comparten **23 de 24 horas**.

Si se separan las filas al azar, es casi seguro que una fila del test tenga una “hermana” casi idéntica en el entrenamiento. El modelo parecería adivinar el futuro, pero solo está reconociendo un caso casi igual.

**Solución:** separar por tiempo, no al azar, y dejar un hueco entre bloques.

---

## 8. La variable objetivo y el umbral

### 8.1 Variable numérica

```text
y_reg = energía activa consumida en las próximas 24 horas (kWh)
```

### 8.2 Variable binaria

```text
me_paso = 1  si y_reg > meta diaria
me_paso = 0  si y_reg <= meta diaria
```

### 8.3 ¿Cuál es la meta diaria?

La meta es el **consumo diario promedio del conjunto de entrenamiento**:

```text
meta = 25,918 kWh
```

Se calcula **solo con entrenamiento** y después queda fija. Nunca se recalcula con validación ni con test.

**Interpretación para el usuario:** “en las próximas 24 h vas a consumir más que en tu día típico”.

### 8.4 ¿Por qué esa meta y no el bloque subsidiado?

Porque este hogar consume mucho: alrededor de 1 kW de potencia media, unos 25 kWh por día. Un tope subsidiado de unos cientos de kWh al mes haría que casi todos los días cayeran en “me pasé”, y la clase quedaría desbalanceada.

La consigna acepta un “límite, objetivo o criterio justificable”. La meta de ahorro es justificable desde el usuario:

- “no quiero superar mi consumo habitual”;
- “no quiero pasarme de lo que cubre el subsidio”;
- “no quiero gastar más de X pesos”.

El método es el mismo; solo cambia el número. En un hogar argentino, la meta podría ser el bloque subsidiado o un presupuesto en pesos convertido a kWh.

### 8.5 El balance de clases (importante)

| Conjunto | Porcentaje con `me_paso = 1` |
|---|---|
| Entrenamiento | **48,3 %** |
| Validación | **72,4 %** |
| Test | **33,7 %** |

Esto muestra un **cambio estacional fuerte**:

- El entrenamiento es de diciembre 2006 a septiembre 2009 (mezcla de estaciones).
- La validación es de septiembre 2009 a abril 2010 (incluye el invierno del hemisferio norte, con más calefacción).
- El test es de abril a noviembre 2010 (primavera/verano, menos calefacción).

**Consecuencia:** las métricas de validación del clasificador son **optimistas**, porque hay muchos positivos. En test, con menos positivos, el recall baja. Esto no significa que el modelo se haya roto: cambió la proporción de casos. Es una de las cosas más importantes para explicar en la defensa.

---

## 9. División temporal: train, validación y test

### 9.1 Cómo se divide

Se usa un **split cronológico 70 / 15 / 15** con un **hueco de 48 horas** entre bloques:

| Bloque | Período | Filas | Para qué |
|---|---|---|---|
| Entrenamiento | 2006-12-24 → 2009-09-15 | **23.755** | entrenar los modelos |
| Validación | 2009-09-17 → 2010-04-19 | **5.042** | comparar y elegir el modelo |
| Test | 2010-04-21 → 2010-11-25 | **5.043** | evaluación final, una sola vez |

### 9.2 Por qué no un split aleatorio

Porque las filas vecinas comparten casi todo el futuro. Un split aleatorio mezclaría casos casi idénticos entre train y test, y las métricas serían falsas.

### 9.3 Por qué un hueco de 48 horas

Porque las ventanas de 24 h se superponen. El hueco corta la continuidad:

- la última fila de train predice las 24 h siguientes;
- la primera fila de validación está 48 h después;
- no hay solapamiento entre lo que una fila de train intenta predecir y lo que ve una fila de validación.

### 9.4 Cómo se usan los bloques

1. Se entrena con **train**.
2. Se comparan los modelos con **validación**.
3. Se elige el mejor.
4. Se **reentrena** con **train + validación**.
5. Se evalúa **una sola vez** en **test**.

Esto cumple las reglas 3 y 7 de la consigna: el test se reserva para el final y no se usa para elegir hiperparámetros.

---

## 10. Baselines: el “modelo tonto” de comparación

### 10.1 Qué es un baseline

Es un modelo deliberadamente simple que sirve como **piso mínimo**. Si tu modelo no le gana, no aporta nada.

La consigna exige dos:

- `DummyRegressor`: siempre predice el promedio del entrenamiento.
- `DummyClassifier`: predice clases siguiendo la proporción observada (estratificado).

### 10.2 Resultados en validación

| Baseline | Resultado |
|---|---|
| `DummyRegressor` (media) | MAE **6,386** · RMSE 8,241 · R² **−0,337** |
| `DummyClassifier` (estratificado) | accuracy **0,501** · precision 0,732 · recall 0,489 · F1 0,586 |

**En criollo:** el regresor tonto se equivoca, en promedio, 6,39 kWh por día. Cualquier modelo útil tiene que bajar ese número.

---

## 11. Regresión: ¿cuánto voy a consumir?

> **Repaso:** qué es un modelo de regresión y qué significan MAE, RMSE y R² está explicado desde cero en **Conceptos básicos A.3 a A.7**.

### 11.1 Los modelos que se comparan

| Modelo | Cómo funciona, en simple |
|---|---|
| `DummyRegressor` | siempre dice el promedio |
| `DecisionTreeRegressor` | hace preguntas del tipo “¿`active_24` > 28?” y divide los casos en grupos; la predicción es el promedio de cada grupo |
| `KNeighborsRegressor` | busca los `k` casos históricos más parecidos y promedia sus consumos |

Se prueban varias profundidades del árbol (`3, 5, 8, 12, sin límite`) y varios `k` del KNN (`5, 15, 25`).

### 11.2 Por qué el KNN lleva `StandardScaler` dentro de un `Pipeline`

El KNN mide “parecido” con distancias. Si una variable está en kWh (valores de 0 a 40) y otra es la hora (0 a 23), o el mes (1 a 12), la distancia quedaría dominada por la variable de mayor escala. El `StandardScaler` lleva todas las variables a una escala comparable (media 0, desvío 1).

El `Pipeline` empaqueta escalador + modelo en un solo objeto. Eso garantiza que el escalador se ajuste **solo con entrenamiento** y no vea los datos de test. Es la regla 6 de la consigna.

### 11.3 Resultados en validación

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| **KNN k=25** | **5,831** | 7,727 | −0,175 |
| DecisionTree depth=3 | 5,838 | 7,530 | −0,116 |
| DecisionTree depth=5 | 5,973 | 7,920 | −0,235 |
| KNN k=15 | 6,116 | 8,143 | −0,305 |
| DecisionTree depth=8 | 6,283 | 8,843 | −0,539 |
| `DummyRegressor` | 6,386 | 8,241 | −0,337 |
| DecisionTree depth=12 | 6,746 | 9,618 | −0,821 |
| KNN k=5 | 6,946 | 9,383 | −0,733 |
| DecisionTree sin límite | 7,936 | 10,846 | −1,315 |

Se elige el de **menor MAE en validación: KNN k=25**.

### 11.4 Resultado final en test

| Métrica | Valor |
|---|---|
| MAE | **4,570 kWh** |
| RMSE | **6,060 kWh** |
| R² | **0,308** |

Residuos (real − predicho):

- media: **−0,653** (leve subestimación);
- desvío: **6,025**;
- percentil 5: **−10,06**;
- percentil 95: **+8,72**.

### 11.5 Qué significa cada métrica

**MAE (Error Absoluto Medio):**

```text
MAE = promedio(|real − predicho|)
```

Es el error promedio en kWh. Si el MAE es 4,57, la app se equivoca, en promedio, **±4,57 kWh por día**. Con una tarifa de 150 $/kWh, eso equivale a **±685 $ por día**.

**RMSE (Raíz del Error Cuadrático Medio):**

```text
RMSE = sqrt(promedio((real − predicho)²))
```

También está en kWh, pero **castiga más los errores grandes** porque los eleva al cuadrado. Que el RMSE (6,06) sea mayor que el MAE (4,57) indica que hay algunos errores grandes, no solo errores chicos.

**R² (coeficiente de determinación):**

- 1 = predicción perfecta;
- 0 = tan bueno como predecir siempre el promedio;
- negativo = **peor** que predecir siempre el promedio.

En test, R² = 0,308 significa que el modelo explica el **30,8 %** de la variabilidad del consumo. No es altísimo, pero es razonable para un fenómeno con tanta variabilidad humana.

### 11.6 ¿Por qué el R² es negativo en validación y positivo en test?

Esta es una pregunta fina y probable en la defensa.

El R² se calcula contra el promedio **del conjunto que se evalúa**. En validación (septiembre 2009 – abril 2010), el consumo medio fue más alto que en entrenamiento, por el invierno. El modelo, entrenado con niveles más bajos, predice de menos; entonces es **peor que predecir el promedio de validación**. De ahí el R² negativo.

En test (abril – noviembre 2010), el nivel medio se parece más al de entrenamiento y el modelo sí captura parte de la variación: R² = 0,308.

**En criollo:** el R² negativo en validación no significa que el modelo sea un desastre; significa que en ese período el nivel de consumo cambió y el modelo quedó “descalibrado” en nivel. El MAE, que es más robusto para comparar, igual mejora al baseline. Y en test, que es la evaluación final, el modelo sí supera al promedio.

> **Para la defensa:** reconocé este punto. Decir “el R² negativo en validación se explica por el cambio estacional y por eso elegimos por MAE, no por R²” demuestra que entendés el problema.

### 11.7 ¿El modelo supera al baseline?

Sí:

- En validación: KNN 5,831 vs Dummy 6,386 (mejora de 0,555 kWh).
- En test: KNN 4,570. El baseline no se evaluó en test en el notebook, pero se puede calcular: sería el MAE de predecir siempre el promedio de entrenamiento (25,92 kWh). Para una defensa perfecta conviene reportar ese número también. La comparación válida ya está hecha en validación, que es donde se elige el modelo.

### 11.8 ¿Por qué KNN k=25 y no un árbol?

Porque tuvo el menor MAE de validación. Además, el KNN con `k=25` **suaviza**: promedia 25 vecinos, así que no reacciona de más a un caso raro. Un `k=5` es más sensible al ruido; un árbol muy profundo se memoriza el entrenamiento y empeora.

---

## 12. Clasificación: ¿me paso o no?

> **Repaso:** qué es un modelo de clasificación y qué significan accuracy, precision, recall, F1, FP y FN está explicado desde cero en **Conceptos básicos A.4 y A.8 a A.12**.

### 12.1 Los modelos que se comparan

| Modelo | Cómo funciona, en simple |
|---|---|
| `DummyClassifier` | predice clases al azar respetando la proporción del entrenamiento |
| `DecisionTreeClassifier` | árbol de preguntas que termina en una clase |
| `KNeighborsClassifier` | busca los `k` casos históricos más parecidos y vota la clase mayoritaria |
| `GaussianNB` | modelo probabilístico basado en el teorema de Bayes; asume que las variables siguen una distribución normal y que son independientes entre sí dada la clase |

Se prueban profundidades `3, 5, 8, 12, sin límite` y `k = 5, 15, 25`.

### 12.2 Cómo se leen las métricas de clasificación

Con la matriz de confusión:

|  | Predicho 0 | Predicho 1 |
|---|---|---|
| **Real 0** | TN (verdadero negativo) | FP (falso positivo) |
| **Real 1** | FN (falso negativo) | TP (verdadero positivo) |

- **Accuracy:** porcentaje de aciertos totales.
- **Precision:** de todos los casos en los que dijo “te pasás”, ¿qué porcentaje realmente se pasó?
  - `precision = TP / (TP + FP)`
- **Recall (sensibilidad):** de todos los casos que realmente se pasaron, ¿qué porcentaje detectó?
  - `recall = TP / (TP + FN)`
- **F1:** media armónica entre precision y recall; resume el equilibrio.

**En criollo:**

- Precision alta = cuando alerta, no molesta de más.
- Recall alto = no se le escapan los casos críticos.
- Para este problema, **importa más el recall**, porque un FN cuesta plata.

### 12.3 Resultados en validación

| Modelo | Accuracy | Precision | Recall | F1 |
|---|---|---|---|---|
| **GaussianNB** | 0,757 | 0,768 | **0,951** | **0,850** |
| DecisionTree depth=5 | 0,758 | 0,778 | 0,932 | 0,848 |
| DecisionTree depth=3 | 0,765 | 0,798 | 0,904 | 0,847 |
| DecisionTree depth=8 | 0,733 | 0,771 | 0,897 | 0,829 |
| KNN k=25 | 0,739 | 0,799 | 0,855 | 0,826 |
| KNN k=15 | 0,726 | 0,793 | 0,842 | 0,816 |
| KNN k=5 | 0,699 | 0,786 | 0,803 | 0,794 |
| DecisionTree depth=12 | 0,690 | 0,775 | 0,806 | 0,790 |
| DecisionTree sin límite | 0,638 | 0,771 | 0,710 | 0,739 |
| `DummyClassifier` | 0,501 | 0,732 | 0,489 | 0,586 |

Se elige por **mayor F1 en validación: GaussianNB** (F1 0,850), que además tiene el recall más alto (0,951).

### 12.4 Resultado final en test

| Métrica | Valor |
|---|---|
| Accuracy | **0,740** |
| Precision | **0,611** |
| Recall | **0,629** |
| F1 | **0,620** |

Matriz de confusión:

|  | Predicho 0 | Predicho 1 |
|---|---|---|
| **Real 0** | **TN = 2.666** | **FP = 680** |
| **Real 1** | **FN = 630** | **TP = 1.067** |

Lectura:

- De 5.043 casos de test, acierta 3.733 (74,0 %).
- Cuando dice “te pasás”, acierta el 61,1 % de las veces.
- Detecta el 62,9 % de los casos en que realmente se pasa.
- Se le escapan **630** casos críticos (FN).
- Molesta de más en **680** casos (FP).

### 12.5 ¿Por qué GaussianNB?

Porque en validación tuvo el mejor F1 y el mejor recall. Es un modelo simple, rápido y probabilistico. Su supuesto fuerte es que las variables son independientes dada la clase; en este problema no es cierto (las variables están correlacionadas), pero igual funcionó bien. Es una lección: un supuesto violado no siempre arruina un modelo.

### 12.6 ¿Por qué las métricas bajan de validación a test?

Por el **cambio en el balance de clases**:

- validación: 72,4 % de positivos → es fácil tener recall alto;
- test: 33,7 % de positivos → hay menos positivos y el modelo falla más.

La accuracy se mantiene parecida (0,757 → 0,740), pero precision y recall bajan. Es esperable y hay que explicarlo, no esconderlo.

---

## 13. Comparación integrada y costos

> **Repaso:** la diferencia entre “modelo de regresión”, “regresión + umbral” y “modelo de clasificación” está resumida en **Conceptos básicos A.18**.

### 13.1 Los dos sistemas

Se evalúan sobre **los mismos casos de test**:

| Sistema | Procedimiento |
|---|---|
| **Clasificador directo** | `GaussianNB` predice 0/1 directamente |
| **Regresión + umbral** | `KNN k=25` predice kWh y luego se aplica `> meta` |

### 13.2 Resultados

| Sistema | Accuracy | Precision | Recall | F1 | FP | FN |
|---|---|---|---|---|---|---|
| **Clasificador directo** | 0,740 | 0,611 | **0,629** | **0,620** | 680 | 630 |
| **Regresión + umbral** | **0,741** | **0,614** | 0,621 | 0,617 | 662 | 644 |

### 13.3 El esquema de costos 3:1

Se define que **un falso negativo cuesta 3 veces más que un falso positivo**:

| Error | Qué le pasa al usuario | Peso |
|---|---|---|
| **FN:** la app dijo “no te pasás” y se pasó | No cambió nada. Paga el exceso a precio pleno y, si el cos φ es bajo, el recargo se calcula sobre una factura más grande | **3** |
| **FP:** la app dijo “te pasás” y no se pasó | Postergó tareas o pasó frío/calor sin necesidad. Pierde comodidad, no plata | **1** |

**Fundamento:** el FN cuesta **plata real**; el FP cuesta **comodidad**. Por eso el usuario prefiere que la app avise de más antes que dejar pasar un día crítico.

Costo total:

```text
costo = 3 × FN + FP
```

| Sistema | Cálculo | Costo |
|---|---|---|
| Clasificador directo | 3 × 630 + 680 | **2.570** |
| Regresión + umbral | 3 × 644 + 662 | **2.594** |

La diferencia es de **24 unidades (0,9 %)**: prácticamente un empate. El clasificador directo gana por muy poco, con mejor recall y menor costo; la regresión gana por muy poco en accuracy y precision.

### 13.4 ¿Qué se recomienda?

- Si hay que elegir uno: **el clasificador directo**, por menor costo y mayor recall.
- Pero la recomendación real es **usar los dos y mostrar si coinciden**. La app hace exactamente eso.
- La regresión aporta algo que el clasificador no da: **cuántos kWh** y, por lo tanto, **cuánta plata**.
- El clasificador aporta la alerta directa, optimizada para no perder casos críticos.

### 13.5 La zona gris

Se define:

```text
zona gris = |kWh predichos − meta| <= MAE
```

Con MAE = 4,57 kWh, la zona gris es el entorno de la meta entre aproximadamente **21,35 y 30,49 kWh**.

Resultados en test:

- **53,3 %** de los casos cae en la zona gris.
- Los dos sistemas **no coinciden** en **828 casos (16,4 %)**.
- De esos desacuerdos, **84 %** cae en la zona gris.

**En criollo:** cuando los dos sistemas discrepan, casi siempre es porque el consumo está tan cerca de la meta que un error chico cambia la respuesta. Por eso la app avisa “estás cerca de tu límite” en lugar de dar una falsa sensación de certeza.

### 13.6 El ejemplo clásico de “buen MAE, mala clasificación”

Meta = 25 kWh.
Predicción = 24,6 kWh → “no te pasás”.
Consumo real = 25,1 kWh → sí se pasó.

El error numérico es de solo **0,5 kWh** (excelente MAE), pero la **alerta es incorrecta**. Eso explica por qué no alcanza con mirar el MAE: cerca del umbral, errores chicos cambian la clase.

---

## 14. El coseno φ (factor de potencia)

### 14.1 Qué es, explicado simple

La energía que entra a la casa tiene dos componentes:

- **Energía activa (kWh):** la que hace trabajo útil: calentar, iluminar, mover.
- **Energía reactiva (kVArh):** la que necesitan motores, compresores y transformadores (heladera, lavarropas, aire, bombas) para crear sus campos magnéticos. No hace trabajo útil, pero circula por la red y la carga.

Se representa con un **triángulo de potencias**:

- cateto 1: potencia activa **P**;
- cateto 2: potencia reactiva **Q**;
- hipotenusa: potencia aparente **S** (lo que la red realmente transporta).

```text
S = sqrt(P² + Q²)
cos φ = P / S = P / sqrt(P² + Q²)
```

- **cos φ = 1:** toda la energía es útil, caso ideal.
- **cos φ bajo:** mucha energía reactiva; la red transporta energía que no se aprovecha. Por eso la distribuidora penaliza.

### 14.2 Cómo se calcula con este dataset

El dataset trae `Global_active_power` y `Global_reactive_power` minuto a minuto. Para cualquier período:

1. Se suma la energía activa del período.
2. Se suma la energía reactiva del período.
3. Se calcula:

```text
cos φ = activa / sqrt(activa² + reactiva²)
```

**Importante:** se calcula con las **energías sumadas**, no promediando los cosenos minuto a minuto. Así lo miden las distribuidoras para facturar.

### 14.3 Las franjas de recargo

Según la **Resolución ENRE 85/2024** (área de Edenor y Edesur):

| Coseno φ | Situación |
|---|---|
| **0,95 o más** | Sin recargo |
| **0,85 – 0,95** | Recargo (aprox. 10 %) |
| **0,75 – 0,85** | Recargo mayor (aprox. 20 %) |
| **Menos de 0,75** | Recargo máximo (aprox. 30 %) |

Detalles:

- **Aplicación gradual:** 30 % del recargo desde octubre 2024, 60 % desde mayo 2025, 100 % desde diciembre 2025.
- **Tope:** el recargo no puede superar el **40 % del subtotal** de la factura.
- **Requisito de medición:** no se puede cobrar a hogares cuyo medidor no separe energía activa de reactiva.
- **Jurisdicción:** la 85/2024 rige en el AMBA (ENRE). En el interior de la provincia de Buenos Aires regula el OCEBA y el régimen puede ser distinto.

### 14.4 Qué lugar ocupa en el TP

El cos φ **no es el objetivo** del trabajo. La consigna pide una variable numérica y una clase derivada; el cos φ entra de tres maneras:

1. **Predictor:** `cosphi_24` y `reactive_24` ayudan a predecir porque reflejan qué artefactos se están usando.
2. **Indicador en la app:** muestra el cos φ **medido** en las últimas 24 h y su franja de recargo. No es una predicción.
3. **Esquema de costos:** el recargo se suma al costo del error en pesos.

### 14.5 Cómo lo calcula la app

La app **no pide** el cos φ. Lo calcula a partir de:

```text
kwh_24h  (energía activa de las últimas 24 h)
kvarh_24h (energía reactiva de las últimas 24 h)

cosphi = kwh_24h / sqrt(kwh_24h² + kvarh_24h²)
```

Eso es correcto y evita que el usuario ingrese un valor inconsistente.

### 14.6 Limitaciones del indicador

- Es **medido**, no predicho.
- Las franjas son aproximadas y dependen de la distribuidora.
- La app aplica el recargo al **costo de energía estimado**, no al subtotal completo de la factura. Es una simplificación.
- No sirve para reclamar formalmente un recargo: vale la medición de la distribuidora.

---

## 15. Comparador estacional de enero

### 15.1 Qué es y por qué está

Es una **tarea complementaria**, agregada por el grupo, que no reemplaza las dos tareas obligatorias. Compara el gasto del mes de **enero** de los últimos años y estima el **enero siguiente (2011)**, que queda fuera del dataset (el dataset termina el 26/11/2010).

### 15.2 Cómo se prepara

Se trabaja a nivel **diario**:

- se suma el consumo de cada día, exigiendo al menos **20 horas válidas**;
- se une la temperatura media diaria;
- se construyen variables de calendario: `month`, `doy` (día del año), `dayofweek`, `is_weekend`;
- se agrega un **rezago largo**: `kwh_year_ago`, el consumo del **mismo día del año anterior**.

**¿Por qué no se usan rezagos cortos (ayer, semana pasada)?** Porque para predecir enero 2011 no existe diciembre 2010 medido. El único dato histórico disponible es enero 2010 y anteriores.

Días útiles: **1.051**, desde 2007-12-17 (cuando ya hay un año de historia para el rezago) hasta 2010-11-26.

### 15.3 Cómo se valida

- Entrenamiento: todo lo anterior a enero 2010 → **739 días**.
- Validación: **enero 2010** → **28 días** (faltan 3 días por datos insuficientes).
- Se compara contra:
  - `DummyRegressor` (media);
  - **estacional ingenuo**: repetir el mismo día del año anterior;
  - regresión lineal;
  - árbol de decisión depth=5;
  - KNN k=5 con `StandardScaler`.

### 15.4 Resultados en validación (enero 2010)

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| **KNN k=5** | **5,216** | 7,592 | −0,377 |
| DecisionTree depth=5 | 6,478 | 7,877 | −0,482 |
| Regresión lineal | 7,412 | 9,068 | −0,964 |
| `DummyRegressor` | 8,853 | 10,351 | −1,559 |
| Estacional ingenuo (año anterior) | 10,336 | 12,190 | −2,550 |

Gana **KNN k=5**: reduce el error a la mitad respecto del estacional ingenuo.

### 15.5 La estimación de enero 2011

Se reentrena con todo el histórico y se predice día por día enero 2011. Para los días en que falta el valor del año anterior (porque enero 2010 tiene 28 días), se usa el **promedio diario de enero**.

Resultado:

```text
Enero 2011 estimado: 1.074,5 kWh  (± 42,3 kWh)
```

El rango de error se calcula como:

```text
RMSE de validación × sqrt(31 días) = 7,592 × 5,568 ≈ 42,3 kWh
```

### 15.6 Tabla comparativa

| Año | Días | kWh | kWh/día | Costo (150 $/kWh) | Variación |
|---|---|---|---|---|---|
| 2007 | 31 | 1.150,3 | 37,11 | $172.545 | — |
| 2008 | 31 | 1.086,2 | 35,04 | $162.933 | −5,6 % |
| 2009 | 31 | 1.049,2 | 33,85 | $157.383 | −3,4 % |
| 2010 | 28 | 958,1 | 34,22 | $143.712 | +1,1 % |
| **2011 (estimado)** | 31 | **1.074,5** | 34,66 | **$161.173** | +1,3 % |

**Detalle importante:** 2010 tiene **28 días**, no 31, porque faltaban datos. Por eso la comparación de variación se hace sobre **kWh/día**, no sobre el total. Si se comparara el total, 2010 parecería más bajo solo por tener menos días.

### 15.7 Limitaciones del comparador

- Solo hay **4 eneros completos** en el dataset: muy poca historia.
- El rango de ±42,3 kWh supone que los errores diarios son independientes; en la realidad están correlacionados, así que el rango podría ser optimista.
- Es un pronóstico de **un mes entero**, no de un día: la incertidumbre se acumula.
- No usa clima en el modelo estacional; solo calendario y año anterior.
- 2011 está fuera del dataset: no se puede verificar el acierto.

---

## 16. La aplicación web

### 16.1 Arquitectura general

```text
notebook  →  entrena y guarda  →  modelos/*.pkl
                                      │
                                      ▼
usuario  →  formulario HTML  →  Flask (app.py)  →  carga el .pkl  →  predict
                                      │
                                      ▼
                         resultados + alertas + costos
```

La app **no entrena**. Solo carga los modelos ya entrenados con `joblib` y ejecuta `predict`. Eso cumple el requisito de la consigna: “sin entrenamiento en cada solicitud”.

### 16.2 Archivos de la app

| Archivo | Rol |
|---|---|
| `app.py` | servidor Flask, validaciones, predicción, costos |
| `templates/index.html` | formulario y presentación de resultados |
| `public/style.css` | estilos (Flask los sirve en `/static/style.css`) |
| `modelos/reg_24h.pkl` | pipeline de regresión + features + meta + MAE |
| `modelos/clf_me_paso.pkl` | pipeline de clasificación + features + meta |
| `modelos/enero_resumen.csv` | tabla del comparador estacional |
| `modelos/enero2011_diario.csv` | predicción diaria de enero 2011 |

### 16.3 Qué ingresa el usuario

El formulario pide lo que en una app real vendría automáticamente del medidor:

| Campo | Unidad | Ejemplo |
|---|---|---|
| Fecha | — | 2026-10-20 |
| Hora (0–23) | h | 19 |
| Energía última hora | kWh | 1,2 |
| Energía últimas 24 h | kWh | 26,0 |
| Energía mismas 24 h, semana pasada | kWh | 27,0 |
| Energía reactiva últimas 24 h | kVArh | 7,0 |
| Submedidor cocina | kWh | 3,0 |
| Submedidor lavadero | kWh | 4,0 |
| Submedidor termotanque/aire | kWh | 10,0 |
| Voltaje promedio 24 h | V | 235 |
| Temperatura actual | °C | 18 |
| Temperatura prevista | °C | 20 |
| Tarifa | $/kWh | 150 |
| ¿Mañana es feriado? | sí/no | — |

### 16.4 Qué hace la app, paso a paso

1. **Lee el formulario.**
2. **Convierte los números.** Acepta coma o punto decimal.
3. **Calcula el cos φ** a partir de `kwh_24h` y `kvarh_24h`.
4. **Valida.**
5. **Si hay errores, los muestra y no predice.**
6. **Si está todo bien:**
   - arma una fila con las 16 features en el orden exacto que espera el modelo;
   - ejecuta `reg["modelo"].predict(X)`;
   - ejecuta `clf["modelo"].predict(X)`;
   - compara la predicción con `META`;
   - calcula la zona gris;
   - calcula el costo y el recargo;
   - identifica el submedidor de mayor consumo;
   - renderiza la plantilla con los resultados.

### 16.5 Validaciones

| Regla | Mensaje |
|---|---|
| Campos numéricos parseables | “El campo ‘X’ debe ser un número.” |
| No negativos (salvo temperatura) | “El campo ‘X’ no puede ser negativo.” |
| Energía de 24 h > 0 | “La energía de las últimas 24 h debe ser mayor que 0.” |
| Última hora ≤ 24 h | “La energía de la última hora no puede superar la de las últimas 24 h.” |
| Suma de submedidores ≤ total | “La suma de los submedidores no puede superar la energía total de 24 h.” |
| Temperaturas entre −30 y 50 °C | “Las temperaturas deben estar entre −30 y 50 grados C.” |
| Hora entre 0 y 23 | “La hora debe estar entre 0 y 23.” |

**Detalle:** si un campo numérico queda vacío, la app usa un valor por defecto (hora 12, 25 kWh, etc.) en lugar de rechazarlo. Es cómodo para probar, pero para una versión final convendría exigir todos los campos.

### 16.6 Qué muestra el resultado

| Bloque | Ejemplo |
|---|---|
| Consumo estimado (próximas 24 h) | 27,4 kWh (± 4,6 kWh) |
| Tu meta diaria | 25,9 kWh |
| Diferencia | Te pasás por 1,5 kWh / Estás 1,5 kWh por debajo |
| Alerta por regresión + umbral | Te pasás / No te pasás |
| Alerta del clasificador directo | Te pasás / No te pasás |
| Coincidencia | Coinciden / No coinciden: zona gris |
| Coseno φ de las últimas 24 h | 0,93 · franja de recargo |
| Costo estimado | $ total = energía + recargo |
| Dónde podés ahorrar | Submedidor de mayor consumo y su porcentaje |
| Zona gris | “Estás dentro de la zona gris: la alerta puede fallar” |
| Lectura | Recomendación concreta: postergar artefactos, revisar motores, etc. |
| Limitaciones | Advertencia permanente |

### 16.7 Cómo calcula el costo

```text
costo_energía = kWh estimados × tarifa
recargo       = costo_energía × porcentaje de la franja de cos φ
costo_total   = costo_energía + recargo
```

La tarifa por defecto es **150 $/kWh**, editable por el usuario. El dataset no trae tarifas, así que es un supuesto declarado.

### 16.8 “Dónde podés ahorrar”

La app toma los tres submedidores, calcula cuál es el mayor y muestra qué porcentaje representa **sobre la suma de los tres** (no sobre el total de la casa). Es una guía, no una medición exacta: hay consumos que no están en ningún submedidor.

### 16.9 Seguridad y buenas prácticas

- No hay base de datos.
- No se suben archivos.
- No se aceptan `.pkl` externos.
- No hay credenciales en el repositorio.
- Los modelos se cargan desde rutas fijas del proyecto.
- Flask usa Jinja, que escapa el HTML por defecto.

### 16.10 Cómo se ejecuta localmente

```bash
pip install -r requirements.txt
python app.py
```

Abrir `http://127.0.0.1:5000`.

En Windows también está `levantar.bat`, que verifica que existan los modelos, que Python esté instalado y que Flask esté disponible.

---

## 17. Despliegue en Vercel

### 17.1 Cómo está configurado

`vercel.json`:

```json
{
  "version": 2,
  "builds": [
    { "src": "app.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "app.py" }
  ]
}
```

- Vercel usa el runtime de Python.
- Todas las rutas van a `app.py`.
- Vercel instala las dependencias de `requirements.txt`.
- La app queda en una URL `proyecto.vercel.app`.

### 17.2 Pasos

1. Subir el repositorio a GitHub.
2. En Vercel: **New Project → Import Git Repository**.
3. Framework preset: **Other**.
4. Deploy.
5. Probar desde otro dispositivo.

### 17.3 Qué se sube y qué no

- **Se sube:** código, modelos `.pkl`, CSVs de resultados, plantillas, estilos.
- **No se sube:** el `.txt` grande de 133 MB (GitHub no lo acepta). No hace falta para la app, solo para entrenar.
- Los `.pkl` están versionados aunque el `.gitignore` ignore `*.pkl`, porque ya fueron agregados antes de la regla. Si se regeneran, hay que volver a commitearlos.

### 17.4 Advertencia

En el informe final la URL de Vercel figura como “completar tras el despliegue”. Antes de entregar hay que publicarla y probarla desde otro dispositivo.

---

## 18. Reproducibilidad

### 18.1 Qué garantiza que se pueda repetir

- **Semilla fija:** `RANDOM_STATE = 42` en todos los modelos que la usan.
- **Versiones fijas:** `requirements.txt` con versiones exactas.
- **Notebook ejecutable desde cero:** carga datos, entrena, evalúa y guarda los modelos.
- **Artefactos guardados:** los `.pkl` contienen el modelo, las features, la meta y las métricas.
- **La app solo consume los artefactos:** no reentrena.

### 18.2 Contenido de los `.pkl`

`reg_24h.pkl`:

```python
{
  "modelo": Pipeline(StandardScaler + KNeighborsRegressor(k=25)),
  "features": [...16 nombres...],
  "meta": 25.917658045475125,
  "nombre": "KNN k=25",
  "mae": 4.570313361485965,
  "rmse": 6.059912518982312
}
```

`clf_me_paso.pkl`:

```python
{
  "modelo": GaussianNB(),
  "features": [...],
  "meta": 25.917658045475125,
  "nombre": "GaussianNB"
}
```

`reg_estacional.pkl`:

```python
{
  "modelo": Pipeline(StandardScaler + KNeighborsRegressor(k=5)),
  "features": ["month", "doy", "dayofweek", "is_weekend", "kwh_year_ago"],
  "nombre": "KNN k=5",
  "tarifa_default": 150.0,
  "rmse_mes": 42.3
}
```

También se guardan `dummy_reg.pkl` y `dummy_clf.pkl` para compatibilidad con la Entrega 2.

### 18.3 Orden de ejecución

1. `pip install -r requirements.txt`
2. (Opcional) `python descargar_clima.py`
3. Tener `household_power_consumption.txt` en `datos/`.
4. Ejecutar el notebook de punta a punta.
5. Verificar que se generaron los `.pkl` en `modelos/`.
6. `python app.py`.

---

## 19. Qué hace cada archivo del repositorio

| Archivo / carpeta | Qué contiene |
|---|---|
| `README.md` | presentación, estructura, cómo ejecutar, resultados y limitaciones |
| `requirements.txt` | versiones exactas de pandas, numpy, scikit-learn, joblib, matplotlib, requests y Flask |
| `app.py` | aplicación Flask completa |
| `templates/index.html` | formulario y bloques de resultado |
| `public/style.css` | estilos de la app |
| `notebooks/entrenamiento.ipynb` | todo el pipeline: datos, features, baselines, modelos, comparación, estacional y guardado |
| `datos/README.md` | fuente, diccionario y transformaciones |
| `datos/clima_sceaux.csv` | clima diario de Sceaux |
| `datasets/household_power_consumption.txt` | dataset grande (no versionado) |
| `datasets/clima_sceaux.csv` | copia del clima |
| `modelos/reg_24h.pkl` | regresor final |
| `modelos/clf_me_paso.pkl` | clasificador final |
| `modelos/reg_estacional.pkl` | modelo estacional |
| `modelos/dummy_reg.pkl`, `modelos/dummy_clf.pkl` | baselines guardados |
| `modelos/enero_resumen.csv` | tabla de eneros 2007–2011 |
| `modelos/enero2011_diario.csv` | predicción diaria de enero 2011 |
| `informe/informe_final.md` | informe final |
| `informe/bitacora.md` | bitácora de decisiones |
| `informe/distribucion_tareas.md` | reparto de tareas por integrante |
| `descargar_clima.py` | descarga el clima de Open-Meteo |
| `crear_nb.py` | genera el notebook desde código Python |
| `levantar.bat` | lanzador local para Windows (está en la carpeta pero no se versiona) |
| `vercel.json` | configuración de despliegue |
| `consignas.md` | enunciado del TP |
| `Trabajo.md` | documento de diseño narrativo del proyecto |
| `propuestas.md` | alternativas iniciales |
| `Entrega_1_Propuesta_Clase1.md` | propuesta de la Clase 1 |
| `Trabajo.pdf`, `Consigna_TP_Integrador_Aprendizaje_Automatico.docx`, `Opciones para el trabajo...docx` | documentos del enunciado |

**Nota:** hay dos carpetas de datos (`datos/` y `datasets/`). El notebook lee de `datos/`, pero el `.txt` grande está en `datasets/`. Para reproducir el notebook hay que copiarlo o moverlo a `datos/`. Es un detalle a corregir.

---

## 20. Limitaciones y riesgos

### 20.1 Limitaciones de los datos

1. **Un solo hogar.** El modelo aprende los hábitos de una familia de Sceaux. Para otra casa hay que reentrenar con sus datos.
2. **Francia, 2006–2010.** Otro clima, otros artefactos y otras tarifas. El **método** se traslada a Argentina; los **números** no.
3. **Faltantes.** Alrededor del 1,25 %, con días enteros sin medir. Se descartan horas con cobertura < 75 %.
4. **Clima real usado como pronóstico.** Es una simplificación declarada. En producción se usaría el pronóstico disponible.
5. **Feriados franceses.** La lista de feriados fijos es la de Francia (1/1, 1/5, 8/5, 14/7, 15/8, 1/11, 11/11, 25/12). Para una app argentina habría que usar feriados argentinos y reentrenar.
6. **Un solo medidor.** No hay información de otros hogares ni de la red.

### 20.2 Limitaciones del modelo

7. **Cambios de hábito (concept drift).** Un artefacto nuevo, uno que se rompe o un integrante más cambian el patrón. El modelo se adapta en pocos días porque usa las últimas 24 h y la semana anterior, no el año pasado. Durante la transición, la zona gris se agranda.
8. **Vacaciones o ausencias.** El modelo no sabe que el usuario se fue; genera FP, que son errores baratos.
9. **No hay incertidumbre por caso.** Se muestra ± MAE, que es un error promedio global, no un intervalo de confianza individual.
10. **KNN guarda todos los datos de entrenamiento.** Con 28.000 filas es manejable, pero no escala a millones sin otra estrategia.
11. **El modelo no entiende causalidad.** Aprende correlaciones; no sabe que “prender el aire” causa consumo.

### 20.3 Limitaciones de la app y del negocio

12. **Tarifa asumida.** 150 $/kWh es un supuesto; el dataset no trae tarifas.
13. **Cos φ medido, no predicho.** Es un indicador, no un pronóstico.
14. **Recargo simplificado.** Se aplica al costo de energía, no al subtotal completo de la factura.
15. **Régimen no universal.** ENRE 85/2024 rige en AMBA; OCEBA puede tener otro régimen.
16. **No sirve para reclamar formalmente.** Vale la medición de la distribuidora.
17. **Pronóstico estacional de baja confianza.** Solo 4 eneros; el rango ±42,3 kWh es optimista.
18. **La app no reemplaza al medidor.** Es un prototipo educativo.

---

## 21. Las 8 preguntas del informe, respondidas

### 1. ¿El modelo de regresión supera al baseline?

**Sí.** En validación, KNN k=25 tiene MAE 5,831 vs 6,386 del `DummyRegressor`. En test, el MAE final es 4,570. La comparación formal se hace en validación, que es donde se elige el modelo; para la defensa conviene tener también el baseline calculado en test.

### 2. ¿Qué significa el MAE en el contexto elegido?

Que la app se equivoca, en promedio, **±4,57 kWh por día**. Con 150 $/kWh, eso es **±685 $ por día**. Respecto de la meta de 25,92 kWh, es un error de aproximadamente **17,6 %**.

### 3. ¿Qué modelo detecta mejor los casos críticos?

El **clasificador directo GaussianNB**, que prioriza el **recall**: 0,629 en test y 0,951 en validación. La regresión + umbral tiene recall 0,621 en test. La diferencia es chica, pero el clasificador está optimizado para no perder casos críticos.

### 4. ¿Qué errores son más costosos?

Los **falsos negativos**: la app dijo “no te pasás” y el usuario se pasó. Cuestan plata real y el recargo por cos φ los agrava. Por eso el esquema 3:1.

### 5. ¿Qué sucede con los casos cercanos al umbral?

Se concentran los desacuerdos entre los dos sistemas. El **53,3 %** de los casos de test está en la zona gris (± MAE), y el **84 %** de los desacuerdos cae ahí. Por eso la app muestra una advertencia en lugar de una certeza.

### 6. ¿Es posible obtener un buen MAE y una mala clasificación?

**Sí.** Cerca del umbral, un error de 0,5 kWh cambia la alerta. El MAE puede ser bueno y la clasificación mala al mismo tiempo. Es exactamente el argumento de la zona gris.

### 7. ¿Qué sistema recomendarían y por qué?

El **clasificador directo**, por menor costo total (2.570 vs 2.594) y mayor recall, aunque la diferencia es mínima. La recomendación completa es **usar los dos y mostrar coincidencia/desacuerdo**: la regresión aporta los kWh y el costo; el clasificador aporta la alerta directa.

### 8. ¿En qué situaciones no debería utilizarse la solución?

- En otro hogar sin reentrenar.
- Con artefactos nuevos, durante los primeros días de adaptación.
- Sin los datos de las últimas 24 h.
- En vacaciones o ausencias prolongadas.
- Para reclamar formalmente un recargo.
- En una jurisdicción o tarifa distintas sin ajustar el esquema.
- Si el medidor no registra energía reactiva (para la parte de cos φ).

---

## 22. Números clave para memorizar

| Dato | Valor |
|---|---|
| Filas crudas | 2.075.259 |
| Horas conservadas | 34.151 |
| Filas útiles | 33.936 |
| Predictores | 16 |
| Split | 70 / 15 / 15 con hueco de 48 h |
| Train / val / test | 23.755 / 5.042 / 5.043 |
| Meta diaria | **25,918 kWh** |
| Positivos en train / val / test | 48,3 % / 72,4 % / 33,7 % |
| Regresor elegido | **KNN k=25** (Pipeline + StandardScaler) |
| MAE test | **4,570 kWh** |
| RMSE test | **6,060 kWh** |
| R² test | **0,308** |
| Clasificador elegido | **GaussianNB** |
| Accuracy test | **0,740** |
| Precision test | **0,611** |
| Recall test | **0,629** |
| F1 test | **0,620** |
| Matriz de confusión | TN 2.666 · FP 680 · FN 630 · TP 1.067 |
| Costo clasificador | **2.570** |
| Costo regresión + umbral | **2.594** |
| Coincidencia entre sistemas | **83,6 %** |
| Desacuerdos | **16,4 %** (828 casos) |
| Desacuerdos en zona gris | **84 %** |
| Zona gris en test | **53,3 %** |
| Enero 2011 estimado | **1.074,5 kWh ± 42,3** |
| Costo enero 2011 | **$161.173** |
| Tarifa asumida | **150 $/kWh** |
| Semilla | **42** |

---

## 23. Preguntas probables de defensa

### ¿Por qué eligieron el consumo eléctrico?

Porque tiene una variable numérica clara (kWh), un umbral justificable desde el usuario (su meta diaria), datos públicos y abundantes, y permite que FP y FN tengan significados distintos y realistas.

### ¿Por qué 24 horas y no 1 hora?

Porque la decisión del usuario es diaria: su meta, su factura y sus hábitos se piensan por día. Predecir una hora sería más fácil pero menos útil.

### ¿Por qué la meta es el promedio y no el percentil 75?

Porque el usuario no piensa en percentiles; piensa en “no pasarme de mi consumo habitual”. Además, el promedio deja clases razonablemente balanceadas en entrenamiento (48,3 %). El percentil 75 fue la idea inicial para una distribuidora, pero se descartó al reenfocar el proyecto en el titular del hogar.

### ¿Por qué no usaron el bloque subsidiado como umbral?

Porque este hogar consume mucho (unos 25 kWh/día) y casi todos los días superarían un tope subsidiado típico; la clase quedaría casi toda en 1. Se explica que el método es el mismo y solo cambia el número.

### ¿Por qué el split es cronológico y no aleatorio?

Porque las ventanas de 24 h se superponen: dos filas consecutivas comparten 23 de 24 horas. Un split aleatorio filtraría el test en el entrenamiento.

### ¿Por qué 48 horas de hueco?

Porque las ventanas se superponen 24 h; el hueco corta la continuidad y evita que el modelo vea en validación casi lo mismo que vio en entrenamiento. 48 h da margen.

### ¿Por qué el test no se usó para elegir el modelo?

Porque se elige con validación. El test se reserva para la evaluación final y se usa una sola vez. Si se usara para elegir, dejaría de ser una prueba honesta.

### ¿Por qué el R² de validación es negativo?

Porque en validación el consumo medio fue más alto (invierno) que en entrenamiento; el modelo predice de menos y queda peor que el promedio de validación. En test, el nivel se parece más al de entrenamiento y el R² es 0,308. Por eso se elige por MAE, que es más robusto al cambio de nivel.

### ¿Por qué no eligieron el árbol si tenía mejor R² en validación?

Porque el criterio de selección fue el **MAE**, que es el error promedio en kWh y se traduce directamente a pesos. El árbol depth=3 tenía MAE 5,838 vs 5,831 del KNN: prácticamente empatados, y el KNN fue levemente mejor. Además, el KNN suaviza con 25 vecinos.

### ¿Por qué GaussianNB si las variables están correlacionadas?

Porque funcionó mejor en validación (mejor F1 y mejor recall) y es simple y rápido. El supuesto de independencia no se cumple, pero el modelo es robusto en este caso. Es una decisión empírica, no teórica.

### ¿Por qué el recall baja tanto de validación a test?

Por el cambio en el balance de clases: validación tiene 72,4 % de positivos (invierno) y test 33,7 % (primavera/verano). Con menos positivos, es más difícil detectarlos. La accuracy se mantiene, pero precision y recall bajan.

### ¿Por qué 3:1 y no 1:1?

Porque un FN cuesta plata real (exceso a precio pleno + recargo sobre una factura más grande) y un FP cuesta comodidad. 3:1 refleja esa asimetría. Se probaron 1:1, 2:1 y 3:1 en la bitácora.

### ¿Cómo se calcula el cos φ?

Con las energías sumadas del período: `P / sqrt(P² + Q²)`. No se promedian cosenos minuto a minuto, porque la distribuidora factura sobre energías agregadas.

### ¿El cos φ es una predicción?

No. Es un indicador **medido** de las últimas 24 h. Se muestra como medición, no como pronóstico. Sí se usa como predictor del modelo.

### ¿Cómo se traduce el MAE a pesos?

`MAE × tarifa = 4,57 × 150 ≈ 685 $/día`. Es un orden de magnitud, porque la tarifa es asumida.

### ¿Qué pasa si el usuario está cerca de la meta?

La app muestra la zona gris: `|predicción − meta| ≤ MAE`. Ahí la alerta puede fallar y se avisa.

### ¿Qué sistema recomiendan?

El clasificador directo por muy poco (costo 2.570 vs 2.594). Pero lo más honesto es usar los dos y mostrar coincidencia/desacuerdo. La regresión aporta el “cuánto” y el costo; el clasificador, la alerta.

### ¿Qué pasa si se rompe un artefacto o compran uno nuevo?

El modelo usa las últimas 24 h y la semana anterior, así que se adapta en pocos días. Durante la transición, la zona gris se agranda.

### ¿Qué pasa en vacaciones?

El modelo no sabe que el usuario se fue; probablemente genere FP (dice “te pasás” y no). Son errores baratos.

### ¿Por qué no usaron una red neuronal?

No era necesario: los modelos obligatorios son árbol, KNN y GaussianNB. Con 33.936 filas y 16 features, un modelo simple y interpretable es preferable. Además, la consigna valora la comparación y la explicación, no la complejidad.

### ¿Qué mejorarían?

- Reportar el baseline también en test.
- Usar feriados argentinos y reentrenar.
- Usar pronóstico real de temperatura.
- Agregar intervalo de confianza por caso.
- Corregir rutas hardcodeadas en los scripts auxiliares.
- Unificar `datos/` y `datasets/`.
- Agregar validación cruzada temporal.
- Probar Gradient Boosting o Random Forest como comparación extra.

---

## 24. Glosario

| Término | Significado simple |
|---|---|
| **Modelo** | Función entrenada que transforma entradas en una salida. |
| **Algoritmo** | El método o la “receta” con la que se entrena un modelo (KNN, árbol, GaussianNB). |
| **Entrenamiento** | Proceso de ajustar el modelo con ejemplos históricos. |
| **Predicción** | Aplicar el modelo ya entrenado a un caso nuevo. |
| **Regresión** | Predecir un número (kWh). |
| **Clasificación** | Predecir una categoría (me paso / no me paso). |
| **Clase** | Categoría que se predice: 0 o 1. |
| **Clase positiva** | La clase que interesa detectar; acá, `me_paso = 1`. |
| **Feature / predictor** | Variable de entrada. |
| **Target / objetivo** | Variable que se quiere predecir. |
| **Umbral del problema** | Valor de corte que separa las clases (meta = 25,92 kWh). |
| **Umbral de decisión** | Punto donde el clasificador cambia de clase (en binario, probabilidad 0,5). |
| **Probabilidad** | Número entre 0 y 1 que indica qué tan probable es una clase. |
| **Distancia** | Medida de parecido entre dos casos; la usa KNN. |
| **Estandarización** | Llevar las variables a la misma escala para que ninguna domine. |
| **Baseline** | Modelo simple de comparación. |
| **Train** | Datos para entrenar. |
| **Validación** | Datos para comparar y elegir modelos. |
| **Test** | Datos para la evaluación final. |
| **Fuga de información** | Usar datos que no estarían disponibles al predecir. |
| **Overfitting** | Memorizar el entrenamiento y fallar con datos nuevos. |
| **Pipeline** | Objeto que encadena transformaciones y modelo. |
| **StandardScaler** | Escala las variables a media 0 y desvío 1. |
| **KNN** | *K-Nearest Neighbors*: busca los K casos históricos más parecidos y promedia (regresión) o vota (clasificación). |
| **Vecino** | Caso histórico parecido a uno nuevo, según una distancia. |
| **Árbol de decisión** | Serie de preguntas que divide los casos; la profundidad controla su complejidad. |
| **GaussianNB** | Clasificador probabilístico basado en Bayes; supone independencia entre variables y distribución normal. |
| **Naive Bayes** | Familia de clasificadores que aplican Bayes con el supuesto “ingenuo” de independencia. |
| **Matriz de confusión** | Tabla que cruza clase real con clase predicha: TP, TN, FP y FN. |
| **MAE** | Error absoluto promedio, en las unidades del target. |
| **RMSE** | Raíz del error cuadrático medio; castiga errores grandes. |
| **R²** | Proporción de variabilidad explicada; negativo = peor que el promedio. |
| **Accuracy** | Porcentaje de aciertos. |
| **Precision** | De lo que alertó, cuánto era correcto. |
| **Recall** | De lo que realmente pasó, cuánto detectó. |
| **F1** | Equilibrio entre precision y recall. |
| **TP / TN / FP / FN** | Verdadero positivo, verdadero negativo, falso positivo, falso negativo. |
| **FN** | Dijo “no te pasás” y sí se pasó. Cuesta plata. |
| **FP** | Dijo “te pasás” y no se pasó. Cuesta comodidad. |
| **Zona gris** | Rango alrededor de la meta donde la alerta es poco confiable. |
| **Concept drift** | Cambio en el comportamiento que invalida patrones viejos. |
| **cos φ** | Factor de potencia: proporción de energía útil. |
| **Energía activa** | La que hace trabajo útil (kWh). |
| **Energía reactiva** | La que usan motores y compresores (kVArh). |
| **Potencia aparente** | Combinación de activa y reactiva (kVA). |
| **Joblib** | Librería para guardar modelos entrenados. |
| **Flask** | Framework web de Python. |
| **Vercel** | Servicio de despliegue en la nube. |

---

## 25. Cómo ejecutar el trabajo paso a paso

### 25.1 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 25.2 Preparar los datos

1. Descargar `household_power_consumption.txt` desde UCI.
2. Guardarlo en `datos/` (el notebook lee de ahí).
3. Verificar que `datos/clima_sceaux.csv` exista (ya está en el repo).

### 25.3 Ejecutar el notebook

Opción A: abrir `notebooks/entrenamiento.ipynb` y usar **Kernel → Restart & Run All**.

Opción B:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/entrenamiento.ipynb
```

Esto entrena, evalúa y guarda los modelos en `modelos/`.

### 25.4 Ejecutar la app

```bash
python app.py
```

Abrir `http://127.0.0.1:5000`.

En Windows: doble clic en `levantar.bat`.

### 25.5 Probar un caso

Se puede usar el formulario con valores de ejemplo. La app valida, predice y muestra:

- kWh estimados;
- alerta por regresión;
- alerta por clasificador;
- coincidencia;
- cos φ;
- costo;
- zona gris;
- comparador de enero.

---

## 26. Checklist contra la consigna

| Requisito | Estado |
|---|---|
| Problema y usuario definidos | ✅ |
| Variable numérica | ✅ kWh/24 h |
| Clase derivada | ✅ `me_paso` |
| ≥ 2.000 registros | ✅ 33.936 |
| ≥ 5 predictores | ✅ 16 |
| Umbral justificado | ✅ meta diaria |
| Fuente documentada | ✅ UCI + Open-Meteo |
| Limpieza y transformación | ✅ |
| FP y FN con significado | ✅ |
| Privacidad | ✅ |
| Originalidad | ✅ |
| `DummyRegressor` | ✅ |
| `DummyClassifier` | ✅ |
| `DecisionTreeRegressor` | ✅ |
| `KNeighborsRegressor` + Pipeline | ✅ |
| `DecisionTreeClassifier` | ✅ |
| `KNeighborsClassifier` + Pipeline | ✅ |
| `GaussianNB` | ✅ |
| MAE, RMSE, R² | ✅ |
| Accuracy, precision, recall, F1 | ✅ |
| Matriz de confusión | ✅ |
| Comparación directo vs regresión+umbral | ✅ |
| Esquema de costos | ✅ 3:1 |
| Zona gris / casos cerca del umbral | ✅ |
| Notebook ejecutable | ✅ (ver detalle de ruta de datos) |
| Modelos guardados con joblib | ✅ |
| App Flask con validaciones | ✅ |
| Sin entrenamiento por solicitud | ✅ |
| Sin base de datos | ✅ |
| Sin credenciales | ✅ |
| `requirements.txt` con versiones | ✅ |
| `vercel.json` | ✅ |
| URL de Vercel | ⚠️ falta publicar/completar |
| Informe final en PDF | ⚠️ está en `.md` |
| Presentación | ⚠️ no está en el repo |
| Bitácora | ✅ |
| Distribución de tareas | ✅ |
| Etiquetas/commits por entrega | ⚠️ verificar en Git |

---

## 27. Detalles a corregir o mejorar antes de la entrega

Estos puntos no invalidan el trabajo, pero conviene tenerlos claros para la defensa y, si hay tiempo, corregirlos:

1. **El baseline no está evaluado en test.** En el notebook, el `DummyRegressor` se evalúa solo en validación. El informe dice “reduce el MAE de 6,39 a 4,57 en test”, pero son conjuntos distintos. Para que la comparación sea impecable, calculá el baseline también en test. La conclusión (el modelo supera al baseline) igual se sostiene con validación.

2. **El R² negativo en validación.** No es un error, pero llama la atención. Tené preparada la explicación estacional. Si querés, podés agregar una nota al informe.

3. **Cambio de balance de clases.** Validación 72,4 % vs test 33,7 %. Las métricas de validación del clasificador son optimistas. Conviene decirlo explícitamente en el informe.

4. **Feriados franceses en una app argentina.** La lista de feriados fijos es la de Francia. Para producción en Argentina hay que usar feriados argentinos y reentrenar.

5. **El checkbox dice “¿Mañana es feriado?” pero el código lo usa como feriado de la fecha de consulta.** Es una inconsistencia menor de semántica. Se puede alinear el texto o la lógica.

6. **Campos vacíos usan valores por defecto.** La app no obliga a completar todo. Para una versión final, conviene exigir los campos o marcar claramente los valores de ejemplo.

7. **La temperatura es real, no pronóstico.** Está declarado, pero conviene repetirlo en la defensa.

8. **El rango ±42,3 kWh del estacional es optimista.** Supone errores diarios independientes. Con 4 eneros, la incertidumbre real es mayor.

9. **Rutas hardcodeadas en scripts auxiliares.** `descargar_clima.py` escribe en `C:\Users\romin\Desktop\tpintegrador\datos\...` y `crear_nb.py` genera el notebook en la misma ruta. En otra máquina fallan. Conviene usar `Path(__file__).parent`.

10. **Dos carpetas de datos.** `datos/` y `datasets/`. El notebook lee de `datos/`, pero el `.txt` está en `datasets/`. Unificar o documentar claramente.

11. **`reg_estacional.pkl` no lo usa la app.** La app lee `enero_resumen.csv`. El `.pkl` queda como artefacto del notebook. No es un error, pero puede confundir.

12. **El informe final está en `.md`.** La consigna pide PDF. Exportarlo antes de entregar.

13. **Falta la presentación y la URL de Vercel.** Completar antes de la entrega final.

14. **`app.run(debug=True)`.** Para producción conviene `debug=False`; en Vercel no se usa ese bloque, pero es buena práctica.

15. **El costo del recargo es una simplificación.** Se aplica al costo de energía, no al subtotal de la factura. Aclararlo si preguntan.

---

## 28. Pitch final de 60 segundos

> “El usuario residencial consume a ciegas: se entera de lo que gastó cuando llega la factura. Nosotros usamos las mediciones minuto a minuto de un hogar real para anticipar las próximas 24 horas y avisar si se va a pasar de su meta diaria.
>
> Sobre el mismo dataset resolvemos dos tareas: una **regresión** que estima los kWh de las próximas 24 horas, y una **clasificación** que dice si esos kWh superan la meta. Además comparamos dos formas de generar la alerta: un clasificador directo y la regresión con umbral. Los dos coinciden en el 84 % de los casos y, cuando no coinciden, casi siempre es porque el consumo está cerca de la meta: por eso mostramos una **zona gris**.
>
> El mejor regresor es un KNN con k=25, con un MAE de 4,57 kWh por día; el mejor clasificador es GaussianNB, con un recall de 0,63 en test. Definimos un esquema de costos 3 a 1 porque un falso negativo cuesta plata y un falso positivo solo cuesta comodidad.
>
> La app en Flask carga los modelos ya entrenados, valida los datos, muestra las dos alertas, el coseno φ medido, el costo estimado y el comparador de enero. Es un prototipo: un solo hogar, Francia 2006–2010, y no sirve para reclamar formalmente un recargo. Pero el método se traslada a cualquier hogar con medidor inteligente.”

---

## Cierre

Si entendiste estas ideas, podés defender el trabajo:

1. **Qué se predice:** kWh de las próximas 24 h y si superan la meta.
2. **Con qué:** 16 variables disponibles al momento de la consulta, sin fuga.
3. **Cómo se evalúa:** split cronológico con hueco, baseline, validación para elegir, test para el final.
4. **Qué modelos:** KNN k=25 para regresión, GaussianNB para clasificación.
5. **Cómo se comparan:** clasificador directo vs regresión + umbral, con costo 3:1 y zona gris.
6. **Qué significa el error:** MAE 4,57 kWh/día ≈ $685/día.
7. **Qué limitaciones tiene:** un hogar, Francia 2006–2010, clima real como pronóstico, tarifa asumida, cos φ medido.
8. **Qué valor tiene:** convierte datos del medidor en una decisión concreta antes de que llegue la factura.
