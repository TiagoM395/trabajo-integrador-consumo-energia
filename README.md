# TP Integrador - Aprendizaje Automático

**"¿Me paso o no me paso?" - Asistente de consumo eléctrico para el hogar**

Integrantes: Bulggiani · Campos · Guzman · Maidana — 2do año

Sobre un mismo conjunto de datos se resuelven dos tareas y una comparación obligatoria:

| Tarea | Pregunta | Resultado |
|---|---|---|
| Regresión | ¿Cuánta energía voy a consumir en las próximas 24 h? | kWh estimados |
| Clasificación | ¿Me paso de mi meta diaria? | sí / no |
| Integración | Comparar el clasificador directo con la regresión + umbral | tabla + costos |

Además, una **tarea complementaria**: un comparador estacional que compara el gasto del mes de enero de los
últimos años y estima el enero siguiente.

## Estructura del repositorio

```
tpintegrador/
├── README.md
├── requirements.txt
├── vercel.json                     # despliegue en Vercel
├── app.py                          # aplicación Flask (solo hace predict)
├── templates/
│   └── index.html
├── public/
│   └── style.css                   # estáticos (Flask los sirve desde /static)
├── notebooks/
│   └── entrenamiento.ipynb         # notebook completo (se ejecuta desde cero)
├── datos/
│   ├── README.md                   # fuente y diccionario de datos
│   ├── household_power_consumption.txt   (no se versiona: ver datos/README.md)
│   └── clima_sceaux.csv
├── modelos/                        # Pipelines entrenados (.pkl) + tablas del comparador
├── informe/
│   ├── informe_final.md
│   ├── bitacora.md
│   └── distribucion_tareas.md
├── descargar_clima.py              # reproduce datos/clima_sceaux.csv
└── crear_nb.py                     # regenera notebooks/entrenamiento.ipynb
```

> `household_power_consumption.txt` (~133 MB) no se versiona por tamaño. Descargarlo desde
> [UCI](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption)
> y guardarlo en `datos/`. Las instrucciones están en [datos/README.md](datos/README.md).

## Datos

- **Individual Household Electric Power Consumption** (UCI, CC BY 4.0): mediciones por minuto de un hogar
  en Sceaux, Francia, dic. 2006 – nov. 2010.
- **Open-Meteo Historical Weather API**: temperatura diaria de la misma ubicación.

Detalle completo en [datos/README.md](datos/README.md).

## Cómo ejecutar el notebook

```bash
pip install -r requirements.txt
python descargar_clima.py            # (opcional) reproduce el clima
jupyter nbconvert --to notebook --execute --inplace notebooks/entrenamiento.ipynb
```

O abrir `notebooks/entrenamiento.ipynb` y usar *Kernel > Restart & Run All*.
El notebook entrena, evalúa y guarda los modelos en `modelos/`.

## Cómo ejecutar la aplicación local

```bash
python app.py
```

Abrir http://127.0.0.1:5000. La app **carga los Pipelines ya entrenados** (`modelos/*.pkl`) y ejecuta `predict`;
no reentrena en cada solicitud ni necesita base de datos.

### Funciones de la app
- Formulario con las variables que en un caso real vendrían del medidor.
- Validación de campos y rangos (no negativos, última hora ≤ 24 h, submedidores ≤ total, temperaturas razonables).
- Predicción numérica (kWh de las próximas 24 h) con ± MAE.
- Alerta desde la regresión (kWh > meta) y alerta del clasificador directo.
- Indicación de coincidencia o desacuerdo y aviso de **zona gris**.
- Coseno φ medido de las últimas 24 h y su franja de recargo.
- Costo estimado en pesos según una tarifa configurable.
- Comparador del gasto de enero por año.

## Despliegue en Vercel

1. Subir el repositorio a GitHub (recordar que el `.txt` grande no se versiona).
2. En Vercel: **New Project > Import Git Repository**.
3. Framework preset: *Other*. El archivo `vercel.json` ya indica el runtime Python y enruta todo a `app.py`.
4. Deploy. Vercel instala `requirements.txt` y publica una URL `proyecto.vercel.app`.
5. Probar desde otro dispositivo.

## Metodología (puntos clave de la consigna)

- **Momento de la predicción:** cualquier hora del día; solo variables medidas hasta ese instante.
- **Sin fuga:** se descarta `Global_intensity` (objetivo disfrazado) y toda medición de horas futuras.
- **Split cronológico** con hueco de 48 h (las ventanas de 24 h se superponen).
- **Umbral** (meta diaria) calculado solo con entrenamiento y luego fijo.
- **Baselines** obligatorios: `DummyRegressor` y `DummyClassifier`.
- **Modelos obligatorios:** Decision Tree, KNN con `StandardScaler` dentro de un `Pipeline` y GaussianNB.
- **Comparación integrada** en los mismos casos de test, con esquema de costos 3:1 (FN 3× más costoso que FP).

## Resultados principales (test)

| Regresión | MAE (kWh/24h) | RMSE | R² |
|---|---|---|---|
| KNN k=25 (con scaler en Pipeline) | 4,57 | 6,06 | 0,31 |

| Sistema de alerta | Accuracy | Precision | Recall | F1 | FP | FN |
|---|---|---|---|---|---|---|
| Clasificador directo (GaussianNB) | 0,740 | 0,611 | 0,629 | 0,620 | 680 | 630 |
| Regresión + umbral | 0,741 | 0,614 | 0,621 | 0,617 | 662 | 644 |

Los dos sistemas coinciden casi siempre; los desacuerdos (16%) caen en un 84% cerca del umbral (zona gris).

## Comparador estacional (enero)

| Año | Días | kWh | kWh/día | Var.% |
|---|---|---|---|---|
| 2007 | 31 | 1150,3 | 37,11 | — |
| 2008 | 31 | 1086,2 | 35,04 | −5,6% |
| 2009 | 31 | 1049,2 | 33,85 | −3,4% |
| 2010 | 28 | 958,1 | 34,22 | +1,1% |
| **2011 (estimado)** | 31 | **1074,5** | 34,66 | +1,3% |

El pronóstico de un mes entero es de baja confianza (solo 4 eneros de historia); se reporta con su rango de error (±42 kWh).

## Limitaciones

- Un solo hogar: no generaliza a otras viviendas sin reentrenar.
- Datos de Francia 2006–2010: otro clima, artefactos y tarifas.
- La temperatura se usa como valor real (simplificación declarada).
- El costo en pesos usa una **tarifa asumida**; el dataset no la incluye.
- No sirve para reclamar formalmente un recargo (vale la medición de la distribuidora).

## Reproducibilidad

- Semilla fija `RANDOM_STATE = 42` en todos los modelos.
- Versiones en `requirements.txt`.
- El notebook se ejecuta desde cero y guarda los modelos; la app solo consume esos artefactos.
