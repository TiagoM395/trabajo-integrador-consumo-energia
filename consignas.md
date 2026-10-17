Trabajo Práctico Integrador de Aprendizaje Automático
Regresión, clasificación aplicación web y despliegue
Datos del trabajo	Completar
Integrantes	
Curso	
Fecha de inicio	
Fecha de entrega final	

Propósito
En este trabajo deberán diseñar una solución completa de aprendizaje automático. El proyecto comenzará con la búsqueda de un problema y terminará con una aplicación web publicada que permita realizar predicciones con datos nuevos.
Sobre el mismo conjunto de datos resolverán dos tareas relacionadas: estimar un valor numérico mediante regresión y anticipar si ese valor superará un umbral mediante clasificación.
Modalidad
•	Trabajo grupal de 4 integrantes.
•	Duración de cinco clases.
•	Cinco entregas progresivas.
•	Repositorio Git por grupo.
•	Aplicación final publicada en Vercel.
•	Presentación grupal.
 
1 Desafío general
Cada grupo deberá seleccionar un problema que tenga una variable objetivo numérica y construir dos sistemas relacionados.
Tarea	Pregunta	Resultado
Regresión	¿Qué valor se espera obtener?	Predicción numérica
Clasificación	¿El valor superará un umbral relevante?	Categoría o alerta

1.1 Ejemplo orientativo
Un proyecto sobre eventos podría predecir la cantidad de asistentes y determinar si se espera una concurrencia superior a 500 personas.
Salida	Ejemplo
Regresión	Asistencia estimada: 627 personas
Clasificación	Alta concurrencia: sí

El ejemplo solamente muestra la relación entre las dos tareas. Cada grupo deberá investigar y proponer su propio proyecto.
1.2 Comparación obligatoria
La alerta deberá generarse de dos maneras:
Sistema	Procedimiento
Clasificador directo	Predice directamente la clase 0 o 1
Regresión más umbral	Predice el valor y luego aplica el umbral

Deberán comparar ambos resultados y explicar cuál conviene utilizar. Un modelo puede cometer un error numérico pequeño y, aun así, producir una alerta incorrecta cuando el caso está cerca del umbral.
1.2.3 Costos
Deberán definir según algún criterio explicado, un esquema de costos para la toma de decisiones. 
1.3 Áreas posibles
Área	Valor numérico	Alerta posible
Eventos	Cantidad de asistentes	Alta concurrencia
Turismo	Porcentaje de ocupación	Ocupación crítica
Energía	Consumo	Consumo pico
Comercio	Monto de ventas	Cumplimiento del objetivo
Transporte	Cantidad de pasajeros	Alta demanda
Ambiente	Índice ambiental	Nivel de alerta
Agricultura	Rendimiento	Rendimiento insuficiente
Alquileres	Precio	Precio superior al límite

2 Condiciones para aprobar el proyecto
El proyecto deberá cumplir todas las condiciones siguientes:
Criterio	Condición
Problema	Debe existir una necesidad y una decisión concreta
Objetivo	Debe existir una variable numérica y una clase derivada
Tamaño	Al menos 2000 registros. 
Variables	Al menos cinco predictores disponibles al momento de predecir
Umbral	Debe representar un límite, objetivo o criterio justificable
Fuente	El origen de los datos debe estar documentado
Preparación	Los datos deben requerir comprensión, limpieza o transformación
Errores	Falsos positivos y falsos negativos deben tener significado
Privacidad	No se admiten datos personales identificables
Originalidad	No se admite copiar completamente un tutorial resuelto

2.1 Proyectos no permitidos
No podrán utilizar Iris, Titanic ni repetir los casos ya trabajados sobre spam, fugas, entregas, máquinas o clasificación de residuos. Tampoco se aprobarán datasets demasiado pequeños, objetivos ambiguos o proyectos donde la respuesta aparezca directa o indirectamente entre las entradas.
3 Organización de las cinco clases
Clase	Trabajo principal	Entrega
1	Investigar y formular el proyecto	Propuesta con tres alternativas
2	Preparar datos y construir baselines	Dataset, diccionario y baselines
3	Entrenar y evaluar regresores	Informe parcial de regresión
4	Entrenar clasificadores e integrar	Comparación y aplicación local
5	Publicar, presentar y defender	Entrega completa y URL pública

3.1 Clase 1 Investigación y propuesta
Deberán investigar tres proyectos posibles. Para cada alternativa indicarán:
•	problema que se intenta resolver;
•	usuario de la predicción;
•	decisión que se tomaría;
•	variable numérica;
•	umbral posible;
•	fuente y tamaño del dataset;
•	variables disponibles;
•	riesgos y limitaciones.
Entrega 1. Documento de propuesta con las tres alternativas. El trabajo continuará solamente con el proyecto aprobado.
3.2 Clase 2 Preparación y baselines
•	identificar qué representa cada fila;
•	definir las variables predictoras;
•	definir la variable numérica;
•	construir la variable binaria;
•	justificar el umbral;
•	revisar tipos, faltantes, duplicados y valores imposibles;
•	identificar fuga de información;
•	analizar distribuciones y balance de clases;
•	separar entrenamiento, validación y prueba;
•	construir DummyRegressor y DummyClassifier.
Entrega 2. Dataset preparado, diccionario de variables, definición de los objetivos, protocolo de evaluación y resultados de los dos baselines.
3.3 Clase 3 Regresión
Deberán comparar como mínimo:
•	DummyRegressor;
•	DecisionTreeRegressor;
•	KNeighborsRegressor con StandardScaler dentro de un Pipeline.
Evaluarán los modelos con MAE, RMSE y R². Deberán comparar profundidades, valores de k, resultados de validación y test, además de analizar residuos y errores importantes.
Entrega 3. Informe parcial de regresión, tabla comparativa, gráficos, análisis de errores y regresor seleccionado.
3.4 Clase 4 Clasificación e integración
Deberán comparar como mínimo:
•	DummyClassifier;
•	DecisionTreeClassifier;
•	KNeighborsClassifier con StandardScaler dentro de un Pipeline;
•	GaussianNB.
Evaluarán accuracy, precision, recall, F1 y matriz de confusión. Luego compararán el clasificador directo con la alerta obtenida al aplicar el umbral sobre la regresión.
Entrega 4. Tabla comparativa de los dos sistemas, análisis de falsos positivos y falsos negativos, modelos guardados y primera aplicación Flask funcionando localmente.
3.5 Clase 5 Despliegue y defensa
•	completar y probar la aplicación;
•	subir el proyecto al repositorio;
•	conectar el repositorio con Vercel;
•	obtener una URL pública;
•	probar desde otro dispositivo;
•	presentar y defender el trabajo.
Entrega 5. Repositorio final, notebook, modelos, aplicación publicada, informe, presentación, bitácora y distribución de tareas.
4 Reglas metodológicas
1. Definir el momento exacto en que se realiza la predicción.
2. Utilizar solamente variables disponibles en ese momento.
3. Separar el test antes de seleccionar modelos o hiperparámetros.
4. Utilizar los mismos casos para evaluar regresión y clasificación.
5. Ajustar las transformaciones solamente con entrenamiento.
6. Incluir el escalado dentro del Pipeline cuando sea necesario.
7. Seleccionar modelos con validación y reservar el test para el final.
8. Comparar todos los modelos contra su baseline.
9. Guardar semillas y versiones para reproducir resultados.
10. Acompañar tablas y gráficos con interpretaciones escritas.
4.1 Evidencias obligatorias
Parte	Evidencia
Datos	Diccionario, controles de calidad y variables descartadas
Regresión	MAE, RMSE, R², residuos y comparación con baseline
Clasificación	Matriz, accuracy, precision, recall, F1 y baseline
Integración	Clasificador directo frente a regresión más umbral
Errores	Casos concretos, consecuencias y cercanía al umbral
Reproducibilidad	Notebook ejecutable, README y requirements

4.2 Tabla integradora
Sistema	Accuracy	Precision	Recall	F1	FP	FN
Clasificador directo						
Regresión más umbral						

4.3 Preguntas que debe responder el informe
•	¿El modelo de regresión supera al baseline?
•	¿Qué significa el MAE en el contexto elegido?
•	¿Qué modelo detecta mejor los casos críticos?
•	¿Qué errores son más costosos?
•	¿Qué sucede con los casos cercanos al umbral?
•	¿Es posible obtener un buen MAE y una mala clasificación?
•	¿Qué sistema recomendarían y por qué?
•	¿En qué situaciones no debería utilizarse la solución?
5 Aplicación web
La aplicación deberá permitir que una persona ingrese un caso y reciba las dos predicciones. El entrenamiento se realiza en el notebook. La aplicación solamente carga los Pipelines ya entrenados y ejecuta predict.
5.1 Funciones mínimas
•	formulario con las variables necesarias;
•	validación de campos y rangos;
•	predicción numérica;
•	alerta obtenida desde la regresión;
•	alerta producida por el clasificador directo;
•	indicación de coincidencia o desacuerdo;
•	interpretación comprensible;
•	advertencia sobre limitaciones.
5.2 Requisitos técnicos
•	Flask para la aplicación;
•	Pipelines guardados con joblib;
•	requirements.txt con versiones;
•	sin credenciales dentro del repositorio;
•	sin entrenamiento en cada solicitud;
•	sin permitir la carga de archivos joblib o pickle externos;
•	sin necesidad de base de datos.
5.3 Despliegue
1. Crear una cuenta gratuita en Vercel.
2. Crear o vincular el repositorio del grupo.
3. Importar el proyecto desde Vercel.
4. Revisar el proceso de construcción.
5. Corregir errores de dependencias o rutas.
6. Obtener la URL del tipo proyecto.vercel.app.
7. Probar la aplicación desde otro equipo o teléfono.
No deberán comprar un dominio ni contratar servicios pagos. Para este trabajo se utilizará la dirección gratuita asignada por Vercel.
6 Organización de archivos y entregas
6.1 Repositorio
Cada grupo deberá crear un repositorio y permitir el acceso del docente. La estructura mínima será:
proyecto/
├── README.md
├── requirements.txt
├── app.py
├── modelos/
├── templates/
├── public/
├── notebooks/entrenamiento.ipynb
├── datos/README.md
└── informe/informe_final.pdf
6.2 Versiones de entrega
Cada entrega deberá asociarse con un commit o etiqueta del repositorio:
•	entrega-1-propuesta;
•	entrega-2-datos;
•	entrega-3-regresion;
•	entrega-4-clasificacion;
•	entrega-5-final.
6.3 Drive
El docente comunicará la carpeta de Drive asignada a cada grupo. En cada entrega deberán subir el documento correspondiente e incluir:
•	número y nombre del grupo;
•	integrantes;
•	archivo solicitado;
•	enlace al repositorio;
•	identificador del commit o etiqueta;
•	en la entrega final, enlace a Vercel.
7 Entrega final
La entrega final deberá contener:
•	notebook ejecutado desde cero;
•	dataset o instrucciones para obtenerlo;
•	diccionario de datos;
•	modelos y Pipelines guardados;
•	código de la aplicación;
•	requirements.txt;
•	README con instalación y ejecución;
•	informe final en PDF;
•	presentación;
•	bitácora de decisiones;
•	distribución de tareas;
•	URL del repositorio;
•	URL de Vercel.
7.1 Presentación
Cada grupo contará con aproximadamente diez minutos. La exposición deberá incluir problema, datos, umbral, baselines, modelos, métricas, comparación integrada, errores, limitaciones y demostración de la aplicación.
7.2 Defensa individual
Todos los integrantes deberán poder explicar cualquier parte del trabajo. El docente podrá realizar preguntas individuales sobre datos, validación, métricas, modelos, errores, aplicación y despliegue.
8 Evaluación
Criterio	Puntos
Formulación y comprensión de los datos	15
Baselines y protocolo de evaluación	10
Desarrollo de regresión	15
Desarrollo de clasificación	15
Comparación integrada	15
Aplicación y despliegue	15
Informe y reproducibilidad	5
Presentación grupal	5
Defensa individual	5
Total	100

8.1 Causas de devolución
El trabajo podrá devolverse para corrección cuando:
•	no se pueda ejecutar el notebook;
•	se utilice el test para elegir el modelo;
•	exista fuga de información;
•	no se compare contra baselines;
•	las métricas aparezcan sin interpretación;
•	la aplicación no utilice los modelos presentados;
•	falten integrantes en la defensa;
•	el proyecto reproduzca una solución externa sin análisis propio.
Anexo Plantilla de propuesta
Campo	Respuesta del grupo
Integrantes	
Nombre del proyecto	
Problema	
Usuario de la predicción	
Decisión que permitirá tomar	
Variable numérica	
Umbral y justificación	
Variable binaria	
Fuente de datos	
Cantidad de observaciones	
Variables disponibles	
Posibles fugas	
Riesgos y limitaciones	

Bitácora de decisiones
Fecha	Decisión	Alternativas	Justificación	Resultado
				
				
				
				
				

Lista de comprobación final
☐ El problema y el usuario de la predicción están definidos.
☐ Las variables están disponibles al momento de predecir.
☐ El umbral está justificado.
☐ El test no se utilizó para seleccionar modelos.
☐ Se incluyeron los dos baselines.
☐ Se compararon los modelos obligatorios.
☐ Las métricas están interpretadas.
☐ Se analizaron errores y casos cercanos al umbral.
☐ El notebook se ejecuta desde cero.
☐ La aplicación valida las entradas.
☐ La URL de Vercel funciona desde otro dispositivo.
☐ El repositorio contiene instrucciones.
☐ El informe reconoce limitaciones.
☐ Todos los integrantes pueden defender el trabajo.
