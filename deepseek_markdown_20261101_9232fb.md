# 📄 README: Anatomía y Cálculo de la Factura Eléctrica de EDEA

Este documento explica de manera detallada la estructura, el origen y la metodología de cálculo de cada uno de los conceptos que aparecen en una factura de la Empresa Distribuidora de Energía Atlántica (EDEA S.A.), correspondiente a la categoría tarifaria **T1RE (Residencial Estacional)** en la zona de Chascomús.

---

## 📌 1. Estructura General de la Boleta

La factura de EDEA se compone de varios bloques visuales que agrupan información distinta[reference:6]:

- **Encabezado**: Contiene el logo de EDEA, el número de factura (con código de barras), la fecha de emisión y los datos del titular (nombre y zona comercial).
- **Recuadro de Cuenta Nº**: Es el resumen central. Incluye el número de cuenta, el período facturado (ej. 05/2026), la fecha de vencimiento y el **Total a Pagar**.
- **Domicilio y Tarifa**: Muestra el domicilio de consumo, la tarifa aplicada (T1RE), la categoría de IVA (CFI - Consumidor Final) y los datos fiscales.
- **Consumos Registrados**: Detalla las lecturas del medidor (estado anterior y actual), el consumo del período en kWh y la energía reactiva.
- **Gráfico de Períodos**: Barras que comparan el consumo de los últimos períodos (kWh) para detectar variaciones anómalas.
- **Detalle de Facturación**: La sección más importante, donde se desglosan los cargos por energía, los impuestos y las tasas.

> **Nota sobre la periodicidad**: EDEA realiza la lectura del medidor cada dos meses, pero emite una boleta todos los meses. El consumo registrado en la lectura bimestral se divide en dos liquidaciones mensuales (cuotas). Por eso el período de facturación puede abarcar rangos de fechas que no coinciden exactamente con el mes calendario[reference:7].

---

## 🔢 2. Sección "Consumos Registrados" (Medición)

Esta sección explica de dónde salen los kWh que se van a facturar.

| Campo | Significado | ¿De dónde sale? |
| :--- | :--- | :--- |
| **Medidor N°** | Número de serie del medidor físico instalado en el domicilio. | Dato fijo del suministro. |
| **Estado anterior** | Lectura del medidor al inicio del período. | Registro de la última lectura (debe coincidir con el "Estado actual" de la boleta previa). |
| **Estado actual** | Lectura del medidor al cierre del período. | Lectura tomada por el operario de EDEA o estimada. |
| **Consumo** | Diferencia entre el estado actual y el anterior. | **Cálculo**: `Estado actual - Estado anterior` (se expresa en kWh). |
| **Energía Reactiva** | Consumo de potencia reactiva (kVarh). | Se mide con el mismo medidor. Solo genera recargos si el factor de potencia (coseno fi) es bajo (generalmente menor a 0,85). En la boleta de ejemplo es 0, por lo que no hay recargo[reference:8]. |
| **Total a Facturar** | Consumo total en kWh sobre el cual se aplicará el cargo variable. | Generalmente coincide con el "Consumo" medido. |
| **Gasto diario de electricidad** | Costo promedio diario del servicio. | **Cálculo**: `Total a Pagar / Días del período facturado` (incluye todos los conceptos e impuestos). |

---

## 💰 3. Sección "Tarifas Aplicadas" y "Conceptos" (Cargos y Cálculos)

Esta sección es el corazón de la factura. El total se compone de la suma de **Energía** (cargos regulados) más los **Impuestos**.

### 3.1. Cargo Fijo (CF)
Es un monto mensual que pagás **haya o no consumo**, porque representa el costo de tener el medidor conectado a la red y disponible[reference:9].
- **En la boleta**: `CARGO FIJO RESID.ESTAL: $ 13.700,70`
- **Origen**: Sale del **Cuadro Tarifario oficial** de EDEA para la categoría T1RE. Es un valor fijado por el Estado provincial (OCEBA) y se actualiza periódicamente[reference:10].

### 3.2. Cargo Variable (CV)
Es el costo por la energía efectivamente consumida. Se calcula multiplicando los **kWh consumidos** por un **precio unitario ($/kWh)** que varía según el nivel de consumo (escalas)[reference:11].

**Fórmula**: `Cargo Variable = Consumo (kWh) × Precio Unitario del Tramo ($/kWh)`

- **En la boleta**: `TARIFA RES.EST.VAR: $ 47.086,07` y `C.T.VAR: $ 2.541,29`
- **Origen**: El Cuadro Tarifario de EDEA establece distintos precios por kWh según el consumo mensual:
    - **Tramo 1**: Hasta 100 kWh/mes → Precio más bajo.
    - **Tramo 2**: Entre 100 y 200 kWh/mes → Precio intermedio.
    - **Tramo 3**: Entre 200 y 400 kWh/mes → Precio más alto.
    - (Y así sucesivamente hasta el Tramo 7 para consumos mayores a 1400 kWh)[reference:12].
- **Ejemplo práctico**: Si consumiste 644 kWh en el período (dividido en dos cuotas de 322 kWh), una parte se factura al precio del Tramo 1 y otra al del Tramo 2 o 3, según corresponda.

### 3.3. "CF - ENERGÍA SIN SUBSIDIO"
- **Monto en boleta**: `$ 100.392,56`
- **Significado**: Es el subtotal de la energía calculada a precio pleno (sin ningún tipo de subsidio estatal). En la categoría T1RE, el usuario paga la energía sin subsidio, y este concepto refleja el costo real de la generación y transporte mayorista.

### 3.4. Subtotales de Energía
- **Subtotal Energía**: Es la suma del Cargo Fijo + Cargo Variable (sin impuestos). En la boleta: `$ 39.685,10`. *Nota: El valor puede variar según la escala de consumo y la actualización tarifaria.*

---

## 🏛️ 4. Sección "Subtotal Estado Nacional" e Impuestos

Aquí se detallan las cargas impositivas que se aplican sobre el subtotal de energía. Para la categoría **T1RE (Residencial)**, la alícuota total de impuestos ronda el **36,5%** sobre el subtotal[reference:13].

| Concepto | ¿Qué es? | Cálculo / Alícuota |
| :--- | :--- | :--- |
| **IVA (21%)** | Impuesto al Valor Agregado. | **Cálculo**: `Subtotal Energía × 0,21` (21% para Consumidor Final). |
| **Ley 10.474** | Fondo Especial de Grandes Obras Eléctricas Provinciales. | Alícuota fija del **6%** sobre el subtotal de energía[reference:14]. |
| **Ley 11.769 Art. 75** | Fondo Provincial de Compensaciones Tarifarias. | Alícuota fija del **6%** (conforme Art. 71 Ley 15.310)[reference:15]. |
| **Ley 11.769 Art. 75 (DCOM)** | Componente de descentralización (comercialización). | Alícuota del **0,001%** (muy baja, solo para redondeo)[reference:16]. |
| **Subtotal Impuestos** | Suma de todos los conceptos impositivos. | **Cálculo**: `IVA + Ley 10.474 + Ley 11.769 + DCOM`. |
| **TOTAL FACTURA** | Monto final a pagar. | **Cálculo**: `Subtotal Energía + Subtotal Impuestos`. |

> **Importante**: El monto de IVA discriminado **no puede computarse como crédito fiscal** para usuarios residenciales (así lo indica la propia boleta en "Información para el Usuario").

---

## 📅 5. Sección "Información para el Usuario"

Esta sección contiene datos operativos y de contacto.

- **Código de Pago Electrónico**: Un número único que identifica tu factura para pagos online o en home banking.
- **Código para Débito Automático**: Se utiliza para adherir el pago automático a una tarjeta o cuenta bancaria.
- **Segmentación N2SEB**: Indica el nivel de subsidio asignado (en este caso, Nivel 2 - Tarifa Social, aunque la boleta muestra "Subsidiado Estado Nacional: 0" porque el usuario no recibe subsidio directo en esta categoría).
- **Vencimiento estimado de la próxima factura**: Fecha probable de emisión de la siguiente boleta.
- **Liquidación de Servicios Públicos / C.E.S.P.**: Números de registro interno de la factura y del código de suministro.
- **Último plazo para pago en bancos**: Fecha límite para abonar en entidades bancarias (suele ser unos días después del vencimiento principal).

---

## 💵 6. Sección "Total a Pagar" y "Gasto Diario"

- **Total a Pagar**: Es el monto final que figura en el recuadro superior derecho y en el pie de la boleta. Incluye **Energía + Impuestos**.
- **Gasto Diario de Electricidad**: Es un indicador que te ayuda a dimensionar el costo diario. Se calcula dividiendo el **Total a Pagar** por la cantidad de días del período facturado.
    - **Fórmula**: `Gasto Diario = Total a Pagar / Días del período`.

---

## 🧾 7. Glosario de Términos Clave

- **kWh (Kilovatio-hora)**: Unidad de medida de la energía consumida.
- **kVarh (Kilovatio-amperio-hora reactivo)**: Unidad de medida de la energía reactiva.
- **T1RE**: Tarifa Residencial Estacional, la categoría para la mayoría de los hogares.
- **CFI**: Consumidor Final Inscripto (categoría de IVA).
- **OCEBA**: Organismo de Control de Energía de la Provincia de Buenos Aires, ente que regula las tarifas de EDEA.
- **Cuadro Tarifario**: Documento oficial donde se publican los precios de los cargos fijo y variable.

---

## 📚 Referencias

1. **EDEA - ¿Cómo leer la factura eléctrica?** (Guía oficial)[reference:17].
2. **EDEA - Cuadro Tarifario Vigente** (Precios de Cargo Fijo y Variable por tramo de consumo)[reference:18].
3. **OCEBA - Impuestos y FPCT** (Alícuotas de Ley 10.474, Ley 11.769, IVA, etc.)[reference:19].
4. **Factura.uno - Cómo leer la factura de EDEA** (Explicación de la periodicidad bimestral y secciones)[reference:20].