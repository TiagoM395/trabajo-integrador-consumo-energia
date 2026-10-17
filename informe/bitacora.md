# Bitácora de decisiones

| Fecha | Decisión | Alternativas | Justificación | Resultado |
|---|---|---|---|---|
| 15/10/2026 | Seleccionar el proyecto de consumo eléctrico | Alt.1 (consumo), Alt.2 (aire), Alt.3 (agro) | Mejor ajuste a requisitos, dataset sólido y umbral justificable con datos. | Aprobado. |
| 16/10/2026 | Reenfocar el proyecto desde el usuario final | Distribuidora vs titular del hogar | El titular es quien decide y a quien le sirve la alerta; habilita costos en pesos. | Se adopta usuario = titular. |
| 16/10/2026 | Definir el objetivo como energía de las próximas 24 h | Consumo de la hora vs de 24 h | "Próximas 24 h" coincide con el día de consumo y con la meta diaria del usuario. | Adoptado kWh/24 h. |
| 16/10/2026 | Umbral = meta diaria (promedio de entrenamiento) | Percentil 75, meta del usuario | Para el usuario el criterio natural es su propia meta; se calcula solo con entrenamiento. | Meta = 25,92 kWh. |
| 16/10/2026 | Separación cronológica con hueco de 48 h | Split aleatorio vs cronológico | Las ventanas de 24 h se superponen y filtrarían el test en el entrenamiento. | Adoptado split cronológico. |
| 16/10/2026 | No usar `Global_intensity` ni variables futuras | Incluirlas vs descartarlas | `Global_intensity` = potencia/voltaje es el objetivo disfrazado; las futuras son fuga directa. | Descartadas. |
| 16/10/2026 | Escalado dentro del Pipeline | Scaler global vs Pipeline | Regla 6 de la consigna; evita fuga del escalado. | Adoptado Pipeline. |
| 16/10/2026 | Esquema de costos 3:1 (FN pesa 3× FP) | 1:1, 2:1, 3:1 | El FN cuesta plata real y el recargo por cos φ lo agrava; el FP cuesta comodidad. | Adoptado 3:1. |
| 16/10/2026 | Agregar comparador estacional de enero | Incluir vs dejar fuera | Pedido del grupo: comparar el gasto de enero por año y estimar el siguiente. | Se agrega como tarea complementaria. |
| 16/10/2026 | Tarifa configurable con valor por defecto | Fija vs configurable | El dataset no trae tarifas; una tarifa editable permite mostrar pesos sin inventar al usuario. | Tarifa default 150 $/kWh. |
| 16/10/2026 | Coseno φ como indicador medido, no como objetivo | Objetivo vs indicador | La consigna pide una variable numérica y una clase derivada; el cos φ es predictor e indicador. | Adoptado indicador. |
