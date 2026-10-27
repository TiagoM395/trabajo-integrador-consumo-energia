# Pendientes de la aplicación

Lo que falta hacer, ordenado por importancia. Estado al **26/10/2026**.

**Menú actual:** Mi casa (pasos 1 a 4, con la predicción al final) · Ambiente 3D · Factura · Análisis.

| Sección | Qué hay |
|---|---|
| [1. El cos φ](#1-el-cos-φ) | El tema más importante que falta: hoy la app casi no lo usa y el valor fijo que usa hace fallar al clasificador |
| [2. Importantes](#2-importantes) | Probar con una factura real, publicar la app, probar en el celular |
| [3. Predicción](#3-predicción-paso-4-de-mi-casa) | Temperatura real, meta, pruebas |
| [4. Mi casa](#4-mi-casa) | Catálogo con estaciones, valores típicos, pruebas |
| [5. Limpieza del proyecto](#5-limpieza-del-proyecto) | Archivos y código que sobran |
| [6. Hecho](#6-hecho) | Lo que ya está terminado |

---

## 1. El cos φ

### 1.1 Qué es

La electricidad que entra a una casa tiene dos partes:

| Parte | Unidad | Qué hace | Ejemplos |
|---|---|---|---|
| **Energía activa** | kWh | Hace el trabajo útil: calienta, ilumina, mueve | Todo lo que se usa |
| **Energía reactiva** | kVArh | La necesitan los **motores, compresores y fuentes** para funcionar; va y viene por la red sin hacer trabajo útil | Heladera, lavarropas, aire, bomba de agua, cargadores |

El **cos φ** (coseno de fi, o factor de potencia) dice qué parte de lo que circula se aprovecha:

```
cos φ = energía activa ÷ √(energía activa² + energía reactiva²)
```

| cos φ | Qué significa |
|---|---|
| **1** | Todo se aprovecha (termotanque, horno, pava, plancha: cargas que solo calientan) |
| **Cerca de 1** (0,95 o más) | Casa normal |
| **Bajo** | Mucha energía reactiva: la red transporta energía que no se usa. Por eso la distribuidora puede cobrar un recargo |

Se calcula con las **energías sumadas** de todo el período, no promediando el cos φ minuto a minuto,
porque así lo mide la distribuidora.

### 1.2 Qué plantea el trabajo

En el trabajo del grupo (`Trabajo.md`, sección 4) el cos φ entra de tres maneras:

| # | Uso | Estado en la app |
|---|---|---|
| 1 | **Dato para el modelo:** el cos φ y la energía reactiva de las últimas 24 h ayudan a predecir el consumo | ⚠️ Se usa, pero con un **valor fijo de 0,95** que hace fallar al clasificador (1.4) |
| 2 | **Indicador en la app:** mostrar el cos φ de la casa y si cae en zona de recargo | ❌ **No está.** La app no muestra el cos φ en ningún lado |
| 3 | **Costo del error:** sumar el recargo al costo de equivocarse | ❌ No está |

### 1.3 Qué dice el cuadro tarifario de EDEA

En el **Anexo 44** (cuadro tarifario oficial de EDEA, Resolución MIySP 682/2026, archivo
`datos/crudos/oceba/IF-2026-27778457-GDEBA-GMOCEBA.pdf`, página 4):

| Concepto | Valor |
|---|---|
| **Recargos por bajo coseno de fi · suministros en baja tensión** | **$ 29,8352 por kVArh** |
| Suministros en media tensión | $ 29,8352 por kVArh |
| Suministros en alta tensión | $ 29,8352 por kVArh |

El Anexo 52 (subsidio SEF) aclara que para este recargo rige el anexo de la demanda residencial.

**Lo que el cuadro NO dice (hay que averiguarlo):**
- **Desde qué cos φ se cobra** (el límite).
- **Qué kVArh se cobran:** todos los del período o solo los que pasan el límite.
- **A qué usuarios se aplica en la práctica.** El precio es por kVArh: solo se puede cobrar si el
  medidor mide la energía reactiva. El medidor común de una casa mide solo energía activa.

Eso está en las **normas de aplicación del cuadro tarifario** del OCEBA (régimen tarifario de la
provincia de Buenos Aires).

**Ojo con lo que dice el trabajo del grupo:** las franjas «0,85 a 0,95 → recargo de alrededor del
10 %, 0,75 a 0,85 → 20 %, menos de 0,75 → 30 %» son de la **Resolución ENRE 85/2024**, que rige
para **Edenor y Edesur** (AMBA) y salen de notas periodísticas. **No se aplican a EDEA**, que regula
el OCEBA. No hay que usarlas en la app.

### 1.4 El problema actual: el valor fijo de 0,95

La app no tiene cómo medir el cos φ de la casa, así que le pasa al modelo **siempre 0,95**
(`COSPHI_TIPICO` en [`simulador/prediccion.py`](simulador/prediccion.py)). En el hogar de Francia
con el que se entrenó:

| Días | cos φ promedio | Desvío |
|---|---:|---:|
| En que no se pasó de la meta | 0,979 | 0,033 |
| En que **sí** se pasó | **0,995** | 0,006 |

Para el clasificador (Naive Bayes), 0,95 es un valor que en un día de exceso casi no existió: por
eso responde **«no te pasás» casi siempre**, haga el frío que haga. Comprobado con la casa Familia
en julio:

| cos φ que recibe el modelo | Probabilidad de «sí» del clasificador |
|---:|---:|
| **0,95** (hoy) | **0 %** |
| 0,98 | 95 % |
| 0,99 | 99,9 % |

Detalle completo en la sección 11 de [`README_MODELO_CLASIFICACION.md`](explicaciones/README_MODELO_CLASIFICACION.md).

### 1.5 Plan propuesto

| Paso | Qué hacer | Qué hace falta | Resultado |
|---|---|---|---|
| **A** | **Arreglo rápido:** usar como cos φ el valor típico del dataset (≈ 0,99) en vez de 0,95 | Cambiar una línea | El clasificador vuelve a funcionar |
| **B** | **Estimar el cos φ de la casa** a partir de sus electrodomésticos: cada uno con su factor de potencia típico (las resistencias ≈ 1; motores y compresores, menos) | Un factor de potencia por equipo del catálogo, **con fuente** (va en `datos/FUENTES.md`) | La app calcula la energía reactiva y el cos φ de la casa, como el medidor del dataset |
| **C** | **Mostrarlo en Mi casa** (paso 3): «⚡ Tu cos φ estimado: 0,96», qué equipos lo bajan (heladera, lavarropas, aire, bomba, cargadores) y qué significa | Paso B | El indicador que pide el trabajo |
| **D** | **Pasarle al modelo el cos φ estimado** (y su energía reactiva) en lugar de un valor fijo | Paso B | Predicción coherente con la casa armada |
| **E** | **Recargo en pesos:** kVArh × $ 29,8352 cuando corresponda | Saber el límite y qué kVArh se cobran (1.3) | Avisar «podrías tener recargo de $ X» |
| **F** | **Explicarlo en la app y en los README** (qué es, por qué baja, que en una casa común el medidor no lo mide) | Pasos B y C | Que nadie lo confunda con una multa segura |

**Recomendación:** hacer **A** ya, porque arregla un error. Después, **B + C + D** juntos, que son el
uso principal del cos φ en la app. **E** queda hasta conseguir la norma del OCEBA.

---

## 2. Importantes

| # | Qué falta | Por qué | Qué hace falta |
|---|---|---|---|
| 1 | **Probar el escaneo con una factura real de EDEA** | La lectura (texto, QR, subsidio) solo se probó con una factura armada para la prueba. Cada distribuidora escribe los datos a su manera | Una foto y un PDF de una factura real de EDEA |
| 2 | **Ver qué trae el código de barras de EDEA** | Hoy se lee el QR de factura electrónica (importe). El código de barras de pago se detecta, pero no se usa | La misma factura real |
| 3 | **Publicar la app en internet** (Streamlit Community Cloud) | Sin publicar, la app solo se abre desde esta PC o por Wi‑Fi. La cámara de *Factura* solo funciona en una página con `https://` | Un repositorio en GitHub y el punto 7 de [`EJECUTAR.md`](EJECUTAR.md) |
| 4 | **Probar todo en el celular** | *Mi casa* cambió mucho: grilla de cards, cantidad con flechas, paso 4 más grande, casa guardada al recargar | Recorrer los 4 pasos, la factura y el 3D en el celular |
| 5 | **Casas guardadas al publicar** | La casa se guarda en la carpeta `sesiones/` del servidor. En Streamlit Community Cloud esa carpeta se borra cuando la app se reinicia | Decidir si alcanza así o si hace falta otro lugar para guardarlas |

## 3. Predicción (paso 4 de Mi casa)

| # | Qué falta | Detalle |
|---|---|---|
| 6 | **El cos φ** | Ver sección 1 |
| 7 | **Temperatura real** | Hoy vienen 20 °C por defecto. Se podría traer la temperatura y el pronóstico del día desde Open‑Meteo, la misma fuente de clima del dataset |
| 8 | **La meta de 25,9 kWh por día** | Es el consumo típico de la casa francesa, alto para un hogar de acá: las casas chicas casi siempre dan «no te pasás». Cambiarla implica reentrenar los modelos |
| 9 | **Casas muy distintas a la de Francia** | El modelo de regresión no puede predecir menos que los días más bajos de esa casa: una casa de 2,9 kWh por día da 18,4 kWh para mañana. Está explicado en [`README_MODELO_REGRESION.md`](explicaciones/README_MODELO_REGRESION.md) (sección 10); falta decidir si se aclara en la app |
| 10 | **Pruebas automáticas de la predicción** | No hay tests de [`simulador/prediccion.py`](simulador/prediccion.py) (armado de las 16 variables, corrimiento del mes, submedidores) |

## 4. Mi casa

| # | Qué falta | Detalle |
|---|---|---|
| 11 | **Consumo típico del catálogo con estaciones** | En el catálogo, los equipos de temporada muestran un promedio del año (aire ≈ 43 kWh) y la card, un mes con uso (aire 106 kWh). Hay que unificar: mostrar en el catálogo lo mismo que va a dar la card |
| 11b | **Precio fijo de las cards** | Para que cada card sea independiente y el total sea su suma, *Mi casa* usa un precio fijo por kWh (casa típica, tramo R3). En casas de otros tramos el total se aleja de la factura real de EDEA, que se muestra debajo como referencia (Familia: $ 284.709 contra $ 341.095). Decidir si alcanza con mostrar los dos números |
| 12 | **Pruebas de las variantes** | No hay tests de [`simulador/variantes.py`](simulador/variantes.py) |
| 13 | **Valores típicos sin dato real** | Termotanque, lavarropas, secarropas, lavavajillas, microondas, horno, calefactor, ventilador, notebook, PC, lámparas y bomba usan valores típicos. Se podrían reemplazar por datos de etiquetas argentinas |
| 14 | **Valores que no se pueden cambiar** | Las horas que queda enchufado, los días de uso, el consumo en espera y la hora de inicio usan siempre los del catálogo |
| 15 | **Barra de horas pegada al 0** | Los usos comunes (1 a 6 h) quedan todos a la izquierda de una barra de 0 a 24 h. Propuesta: pasos de media hora hasta 8 h y de una hora desde ahí |
| 16 | **Recuadro «Resumen de tu casa»** | Aparece arriba en *Mi casa*, *Ambiente 3D* y *Factura*. Falta decidir si queda en las tres o solo en *Mi casa* |

## 5. Limpieza del proyecto

Nada de esto cambia lo que se ve en la app.

| # | Qué | Por qué | Propuesta |
|---|---|---|---|
| 17 | 4 pantallas viejas: `app_pages/dia.py`, `tarifas.py`, `eficiencia.py`, `referencias.py` | No están en el menú | Borrarlas, con los 4 gráficos que solo usan ellas (`curva`, `agenda`, `costo_consumo`, `meta_diaria`) |
| 18 | `clima_sceaux.csv` en la raíz | La app no lo usa: es la temperatura con que se entrenaron los modelos | Pasarlo a `datos/` |
| 19 | Funciones sin uso: `estado.duplicar`, `ui._al_cambiar_conectado`, `ui._horas_txt`, `variantes.POR_DEFECTO` | Quedaron de versiones anteriores | Borrarlas |
| 20 | `Consigna…docx`, `Trabajo.pdf`, `Propuesta_Simulador_Interactivo.md` en la raíz | Son documentos del curso, no de la app | Juntarlos en una carpeta `documentos/` |
| 21 | `EJECUTAR.md` y `EJECUTAR_ELIAS.md` en la raíz | Son instrucciones, como los README | Pasarlos a `explicaciones/` |

---

## 6. Hecho

**Mi casa**
- Grilla de **cards cuadradas** (280 px): nombre grande, kWh y $ al centro, pregunta abajo, franja con el color de la categoría, sin barra para bajar adentro. Entran 2 o 3 por fila según la pantalla.
- **Cantidad con flechas** (1 a 20), sin escribir.
- **Total del mes en pesos** arriba del paso 3, con el desglose de la factura.
- El perfil elegido va en su propio recuadro; más espacio en el paso 2.
- Perfil *Ejemplo de la propuesta* con un **cargador de celular**.
- Resultado de la predicción (paso 4) **más grande y destacado**.
- **La casa no se pierde** al cambiar de pestaña ni al recargar la página (código `?casa=…` en la dirección).

**Factura**
- La **cámara se abre solo con un botón** («Sacar foto con la cámara»), no al entrar a la pestaña.

**Documentación**
- READMEs en la carpeta `explicaciones/`: uno por pestaña y uno por cada modelo
  ([regresión](explicaciones/README_MODELO_REGRESION.md) y [clasificación](explicaciones/README_MODELO_CLASIFICACION.md)).
- README detallado de *Mi casa*: [`README_MI_CASA.md`](explicaciones/README_MI_CASA.md).

**Antes**
- Navbar fijo con el nombre **¿Me paso o no me paso?** y las pestañas siempre visibles.
- Sin barra lateral: subsidio, consumo de base y «Reiniciar todo» en el paso 1 de *Mi casa*.
- *Mi casa* en 4 pasos, con la predicción (regresión y clasificación) al final.
- *Factura*: foto, PDF o cámara; lectura de texto (Tesseract), QR y subsidio.
- *Análisis*: el trabajo con el dataset y los modelos, paso a paso.
