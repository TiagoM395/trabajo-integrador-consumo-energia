¿Me paso o no me paso? — Asistentede consumo eléctrico para mi hogar
Oct 13, 2026 · @Francisco Elias Campos
1. La problemática, desde el usuario
El usuario residencial consume a ciegas: se entera de cuánto consumió cuando llegala factura, uno o dos meses después, cuando ya no puede corregir nada.
Por qué le importa anticiparse:
1.
Plata.
La tarifa eléctrica pesa cada vez más en el presupuesto del hogar.
2.
Bloque subsidiado.
El subsidio cubre una cantidad limitada de kWh por mes; loque se pasa se paga a precio pleno. Los topes cambian seguido: verificar elesquema vigente al citarlos.
3.
Recargos por bajo factor de potencia (coseno φ).
Casi ningún usuario loconoce y ahora le puede llegar en la factura (sección 4).
4.
Hábitos invisibles.
El usuario no sabe qué artefacto le come el consumo ni cuálempeora su factor de potencia.
Lo que el usuario querría tener:
Una app que, con lo que su medidor inteligente ya registró, le diga:
cuánta energía va a consumir en las próximas 24 horas;
si con ese ritmo se pasa de su meta;
cómo está su coseno φ y si corre riesgo de recargo;
cuánta plata representa todo eso.
Así puede actuar antes: postergar el lavarropas, bajar la calefacción o el aire, apagarel termotanque, o revisar si necesita corregir el factor de potencia.
2. Las preguntas del usuario y las tareasdel TP
La app responde dos preguntas con modelos (regresión y clasificación) y suma dosdatos calculados que no son modelos.
Tarea
Pregunta delusuario
Salida de la app
Regresión
¿Cuánta energíavoy a consumir enlas próximas 24h?
"Vas a consumir unos 27,4 kWh"
Clasificación
¿Me paso de mimeta diaria?
"Te pasás: sí / no"
Indicadorcomplementario (noes modelo)
¿Cómo está micoseno φ? ¿Mepueden multar?
"Tu cos φ de las últimas 24 h: 0,93.Zona de recargo"
Costo estimado
¿Cuánto mecuesta?
"Estimado:
Y"
Comparación obligatoria, contada desde el usuario.
La alerta "te pasás" sale dedos maneras:
Clasificador directo:
responde sí o no.
Regresión + umbral:
estima los kWh y los compara con la meta.
Si los dos no coinciden, la app lo dice: "Los modelos no coinciden. Estás cerca de tulímite".
3. Ficha del proyecto (plantilla delAnexo)
X, incluidounposiblerecargode
Campo
Respuesta
Nombre delproyecto
"¿Me paso o no me paso?": asistente para anticipar elconsumo eléctrico y el riesgo de recargo en un hogar conmedidor inteligente
Problema
El usuario residencial no conoce su consumo ni su factor depotencia hasta que llega la factura. Pasarse de la meta (o delbloque subsidiado) y tener un coseno φ bajo encarecen lafactura
Usuario de lapredicción
El titular del hogar, a través de una aplicación web
Momento de lapredicción
Cualquier hora del día, cuando el usuario abre la app. Usatodo lo medido hasta ese instante y estima las 24 horassiguientes
Decisión quepermitirá tomar
Si la alerta da "te pasás": reducir o postergar lavarropas,secarropas, lavavajillas, termotanque, calefacción y aire. Si elcos φ está en zona de recargo: revisar los artefactos conmotores o compresores y evaluar un capacitor
Variablesdisponibles almomento depredecir
Lo que el medidor ya registró:
energía activa de la últimahora y de las últimas 24 h; energía activa de las mismas 24 hde la semana anterior; energía de las últimas 24 h porsubmedidor (cocina, lavadero, termotanque/aire); energíareactiva de las últimas 24 h; coseno φ de las últimas 24 h;voltaje promedio de las últimas 24 h.
Calendario:
hora actual, día de la semana, mes, fin desemana o feriado, período de vacaciones.
Clima:
temperatura actual y temperatura prevista para laspróximas 24 h.
Variablesdescartadas
Potencia activa, reactiva, intensidad y submedidores de horasfuturas: son el objetivo o partes de él.
Intensidad como atajo: es potencia dividida por voltaje.
Fecha como número continuo: no generaliza a fechas futuras.
Unidad de análisis
Un momento de consulta, por ejemplo "martes 14/03/2009,19:00". Una fila por cada hora del período
Variable numérica
Energía activa consumida en las 24 horas siguientes (kWh)
Campo
Respuesta
Umbral
La meta diaria de consumo del usuario (sección 5)
Variable binaria
me_paso = 1 si el consumo de las próximas 24 h supera lameta diaria
Fuente de datos
UCI Machine Learning Repository, "Individual HouseholdElectric Power Consumption" (Hébrail & Bérard), CC BY 4.0:mediciones por minuto de un hogar, dic. 2006 a nov. 2010(potencia activa y reactiva, voltaje, intensidad, 3submedidores).
Open-Meteo Historical API: temperatura horaria del lugar
Cantidad deobservaciones
Unas 2.075.000 mediciones por minuto; por momento deconsulta horario, unas 34.500 filas (más de 2000)
Posibles fugas
Sección 6
Riesgos ylimitaciones
Sección 9
4. Coseno φ y multas
El coseno φ entra al proyecto como predictor, como indicador medido en la app ycomo parte del costo del error. No es el objetivo principal.
4.1 Qué es, explicado para el usuario
La energía que entra a la casa tiene dos componentes:
Energía activa (kWh):
la que hace trabajo útil (calentar, iluminar, mover). Es laque el usuario "usa".
Energía reactiva (kVArh):
la que necesitan motores, compresores ytransformadores (heladera, lavarropas, aire, bombas, fuentes de equipos) paracrear sus campos magnéticos. No hace trabajo útil, pero circula por la red y lacarga.
Se representan como un triángulo de potencias: un cateto es la potencia activa (P), elotro la reactiva (Q) y la hipotenusa la aparente (S), lo que la red realmente transporta.
Cos φ = 1:
toda la energía es útil, el caso ideal.
Cos φ bajo:
mucha energía reactiva; la red transporta energía que no seaprovecha. Por eso la distribuidora penaliza.
4.2 Las multas (recargos)
La Resolución ENRE 85/2024 (área de Edenor y Edesur) incorporó un régimen demejora del factor de potencia que alcanza también a usuarios residenciales. Según lopublicado:
Aplicación gradual:
30% del recargo desde octubre 2024, 60% desde mayo2025, 100% desde diciembre 2025.
Tope:
el recargo no puede superar el 40% del subtotal de la factura.
Requisito de medición:
no se puede cobrar a hogares cuyo medidor no separeenergía activa de reactiva. Por eso el caso tiene sentido en un hogar con medidorinteligente, que es lo que representa el dataset.
Coseno φ
Situación
0,95 o más
Sin recargo
Entre 0,85 y 0,95
Recargo (informado alrededor del 10%)
Entre 0,75 y 0,85
Recargo mayor (alrededor del 20%)
Menos de 0,75
Recargo máximo (alrededor del 30%)
Para el informe:
los porcentajes vienen de notas periodísticas; citarlos desde el textooficial de la resolución. La 85/2024 rige en el área del ENRE (AMBA); en el interior dela provincia de Buenos Aires regula el OCEBA y el régimen puede ser distinto.
4.3 Cómo se calcula con el dataset
El dataset trae
Global_active_power
y
Global_reactive_power
minuto a minuto.Para cualquier período:
1.
Se suma la energía activa del período.
2.
Se suma la energía reactiva del período.
3.
Cos φ del período = activa / √(activa² + reactiva²).
cos φ = =
S
P
P2 + Q2
P
Se calcula con energías sumadas,
no promediando cosenos minuto a minuto
,porque así lo miden las distribuidoras para facturar.
4.4 Qué lugar ocupa en el TP
La consigna pide una variable numérica y una clase derivada de ella; por eso elcoseno φ no es el objetivo. Entra de tres maneras:
1.
Predictor:
el cos φ y la energía reactiva de las últimas 24 h reflejan quéartefactos se están usando (motores y compresores) y ayudan a predecir elconsumo.
2.
Indicador en la app:
muestra el cos φ medido en las últimas 24 h y en qué franjade recargo cae. Es una medición calculada, no una predicción, y así se presenta.
3.
Esquema de costos:
el recargo se suma al costo del error en pesos (sección 7).
A revisar en la exploración (Clase 2):
en un hogar típico el cos φ promedio suele seralto, porque predominan cargas resistivas (termotanque, horno), y baja en horas depoco consumo. Mirar la distribución real del cos φ diario de este hogar y contar en quéporcentaje de días cae debajo de 0,95. Ese dato va en el informe y justifica que el cosφ sea indicador y no objetivo.
5. El umbral: la meta del usuario
El umbral es la meta diaria del usuario: su consumo diario promedio del período deentrenamiento. La consigna pide un "límite, objetivo o criterio justificable", y desde elusuario el criterio natural es su propia meta.
Meta diaria = meta mensual ÷ 30.
En la vida real, la meta mensual puede salir de:
el bloque subsidiado ("no quiero pasarme de lo que cubre el subsidio");
un presupuesto en pesos, pasado a kWh con la tarifa;
una meta de ahorro ("no quiero superar mi consumo habitual").
Para este proyecto se usa la meta de ahorro:
Meta diaria = consumo diario promedio del período de entrenamiento.
La alerta significa: "en las próximas 24 h vas a consumir más que en tu día típico".
Se calcula solo con los datos de entrenamiento (regla 5) y queda fija. Da clasesrazonablemente balanceadas.
Por qué no el bloque subsidiado:
este hogar consume bastante (alrededor de 1 kWde potencia media, unos 25 kWh por día; verificarlo en la exploración). Con un tope deunos cientos de kWh al mes se pasaría casi siempre y la clase quedaría casi toda en1. En el informe se aclara que con un hogar argentino la meta sería el bloquesubsidiado o el presupuesto en pesos: el método es el mismo y solo cambia elnúmero.
6. Fugas de información
Solo entra lo medido antes del momento de consulta; todo lo demás es fuga.
1.
Datos futuros:
ninguna medición posterior al momento de consulta: potencia,reactiva, intensidad, submedidores y también el cos φ de las horas futuras.
2.
Intensidad:
es casi potencia dividida por voltaje, o sea el objetivo disfrazado.
3.
Submedidores del período futuro:
son partes del consumo que se quierepredecir.
4.
Ventanas superpuestas:
la consulta de las 19:00 predice de 19 a 19 y la de las20:00 de 20 a 20; comparten 23 de 24 horas. Si las filas se separan al azar, eltest se filtra en el entrenamiento.
Solución:
separación cronológica enentrenamiento, validación y test, con un día de hueco entre bloques.
5.
Umbral calculado con todos los datos:
la meta sale solo del entrenamiento.
6.
Escalado fuera del Pipeline:
el StandardScaler va dentro del Pipeline (regla 6).
7. Costos de los errores, en pesos
Un falso negativo cuesta tres veces más que un falso positivo, porque cuesta plata yno solo comodidad.
Error
Qué le pasa al usuario
Peso
FN:
la app dijo"no te pasás" yse pasó
No cambió nada. Paga el exceso (a precio pleno sisuperó el bloque subsidiado) y, si su cos φ es bajo, elrecargo se calcula sobre una factura más grande
3
Error
Qué le pasa al usuario
Peso
FP:
la app dijo "tepasás" y no sepasaba
Postergó tareas o pasó algo de frío o calor sinnecesidad. Pierde comodidad, no plata
1
Fundamento:
el FN cuesta plata real y la multa por coseno φ lo agrava, porque elrecargo es un porcentaje de la factura: cuanto más consume, más paga de recargo. ElFP cuesta comodidad. Por eso al usuario le importa más el recall: que la app no sepierda los días en que se pasa.
Costo estimado que muestra la app:
costo de energía = kWh estimados × tarifa;
recargo = costo de energía × porcentaje según la franja de cos φ;
costo total estimado = costo de energía + recargo.
Así el MAE se traduce a pesos: "en promedio la app se equivoca ± X kWh, que con tutarifa son ±$Y".
Casos cerca del umbral:
con una meta de 25 kWh, una predicción de 24,6 kWh da"no te pasás", pero alcanza un error de 0,5 kWh para que el consumo real sea 25,1 yla alerta quede equivocada. Por eso la app marca una
zona gris
de ± el MAEalrededor de la meta: "estás cerca de tu límite".
8. La aplicación
El usuario carga lo que en una app real vendría automáticamente del medidor y recibeconsumo, alertas, cos φ y costo.
Formulario
día y hora actual;
energía activa de la última hora y de las últimas 24 h (kWh);
energía activa de las mismas 24 h de la semana pasada;
energía reactiva de las últimas 24 h (kVArh);
energía de ayer por submedidor: cocina, lavadero, termotanque/aire;
temperatura actual y prevista;
si mañana es feriado o fin de semana;
tarifa por kWh (opcional, para mostrar pesos).
Validaciones
no se aceptan valores negativos;
la energía de la última hora no puede superar la de las últimas 24 h;
la suma de los submedidores no puede superar la energía total;
las temperaturas tienen que estar en rangos razonables.
Resultado que ve el usuario
Bloque
Ejemplo
Consumo estimado(próximas 24 h)
27,4 kWh (± MAE)
Tu meta diaria
25 kWh
Alerta por regresión
Te pasás por 2,4 kWh
Alerta delclasificador directo
Te pasás
Coincidencia
Los dos sistemas coinciden / no coinciden: estás en zonagris
Coseno φ de lasúltimas 24 h
0,93, franja de recargo. "Los motores y compresores(heladera, lavarropas, aire) bajan tu factor de potencia.Consultá con un electricista por un capacitor"
Costo estimado
Y de posible recargo
Interpretación
"Ayer el termotanque y el aire fueron el 45% de tu consumo:ahí podés ahorrar más"
Limitaciones
"Modelo de referencia entrenado con otro hogar. Losrecargos dependen de tu distribuidora y de que tengasmedidor que registre energía reactiva"
9. Riesgos y limitaciones
Xdeenergˊıa+
El proyecto es un prototipo de lo que podría tener cada hogar con medidor inteligente,no una herramienta lista para cualquier casa.
1.
Un solo hogar.
El modelo aprende los hábitos de esa familia; para otra casa hayque reentrenarlo con sus datos.
2.
Francia, 2006-2010.
Otro clima, otros artefactos y otras tarifas. El método setraslada a Argentina; los números no.
3.
El régimen de recargos no es universal.
La Res. ENRE 85/2024 rige en el áreade Edenor y Edesur; en el interior bonaerense regula el OCEBA y las condicionespueden ser otras. Además, no se puede cobrar si el medidor no registra energíareactiva.
4.
El cos φ de la app es el medido, no el predicho.
Es un indicador y no sepresenta como pronóstico.
5.
Cambios de hábitos (Concept Drift).
Un artefacto nuevo, uno que se rompe, oun integrante más modifican el patrón de consumo. Por ejemplo: si el aireacondicionado se rompe y el usuario compra una heladera nueva, el modelopuede equivocarse los primeros días porque se basa en patrones viejos.
Sinembargo, el diseño del modelo mitiga este problema:
como los predictoresprincipales son el consumo de las últimas 24 h y de la semana anterior (no elconsumo del año pasado), el modelo se adapta automáticamente a la nuevaheladera en cuestión de días, sin que el usuario tenga que avisarle nada. Duranteesa transición, la app muestra la zona gris con mayor amplitud para advertir quela predicción tiene más incertidumbre.
6.
Vacaciones o ausencias:
el modelo no sabe que el usuario se va; eso generaFP, que son errores baratos.
7.
Clima real usado como pronóstico:
simplificación declarada.
8.
Faltantes:
alrededor del 1,25%, con días enteros sin medir. La decisión sobrequé hacer va en la bitácora.
10. Las preguntas del informe, desde elusuario
Pregunta de laconsigna
Respuesta desde el usuario
¿La regresiónsupera al baseline?
Se compara con el DummyRegressor y con un baselineingenuo ("mañana consumo lo mismo que en las últimas 24h"). Si no le gana a eso, la app no le aporta nada al usuario
Pregunta de laconsigna
Respuesta desde el usuario
¿Qué significa elMAE?
"La app se equivoca en promedio ± X kWh por día, o sea ±$Y"
¿Qué modelodetecta mejor loscasos críticos?
El de mayor recall en me_paso = 1
¿Qué errores sonmás costosos?
Los FN: son plata y el recargo por cos φ los agrava
¿Qué pasa cerca delumbral?
Ahí se concentran los desacuerdos entre los dos sistemas;por eso existe la zona gris
¿Buen MAE y malaclasificación?
Sí: errores chicos cerca de la meta cambian la alerta
¿Qué sistemarecomiendan?
El de menor costo total con el esquema 3 a 1, sin que laprecision caiga tanto que el usuario ignore las alertas
¿Cuándo no usarlo?
En otro hogar sin reentrenar, con artefactos nuevos (durantelos primeros días de adaptación), sin los datos de las últimas24 h, o para reclamar formalmente un recargo (la mediciónválida es la del medidor de la distribuidora)
Fuentes
Programa para la mejora del factor de potencia (sobre Res. ENRE 85/2024),Editores Quiénes podrían pagar multas en Edenor o Edesur, BAE Negocios
Open-Meteo Historical Weather API
UCI Machine Learning Repository, "Individual Household Electric PowerConsumption" (Hébrail & Bérard)