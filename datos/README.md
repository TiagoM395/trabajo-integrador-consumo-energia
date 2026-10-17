# Datos

## 1. Consumo electrico del hogar

- **Archivo:** `household_power_consumption.txt`
- **Fuente:** UCI Machine Learning Repository, *Individual Household Electric Power Consumption*
  (Hebrail & Berard). https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
- **Licencia:** CC BY 4.0
- **Contenido:** mediciones por minuto de un unico hogar en Sceaux (Francia).
- **Periodo:** 16/12/2006 17:24 -> 26/11/2010 21:02 (~2.075.259 filas).
- **Faltantes:** los valores ausentes estan codificados como `?` (~1,25%).

### Diccionario de variables originales

| Variable | Unidad | Descripcion |
|---|---|---|
| Date | - | Fecha (dd/mm/aaaa) |
| Time | - | Hora (hh:mm:ss) |
| Global_active_power | kW | Potencia activa promedio del minuto |
| Global_reactive_power | kVAr | Potencia reactiva promedio del minuto |
| Voltage | V | Voltaje promedio del minuto |
| Global_intensity | A | Intensidad promedio del minuto |
| Sub_metering_1 | Wh | Submedidor 1 (cocina: lavavajillas, horno, microondas) |
| Sub_metering_2 | Wh | Submedidor 2 (lavadero: lavadora, secarropas, heladera, luz) |
| Sub_metering_3 | Wh | Submedidor 3 (calefon electrico y aire acondicionado) |

### Transformaciones aplicadas (en el notebook)

- Agregacion **horaria**: la potencia media en kW durante una hora equivale a la **energia kWh** de esa hora.
  La reactiva media en kVAr equivale a **kVArh**. Los submedidores, que vienen en Wh por minuto, se **suman** y se
  dividen por 1000 para obtener kWh.
- Filtro de calidad: se conservan solo las horas con **>= 75%** de minutos medidos (de 34.589 horas quedan 34.151).
- Agregacion **diaria** para la tarea estacional (minimo 20 horas validas por dia).

## 2. Clima (temperatura)

- **Archivo:** `clima_sceaux.csv`
- **Fuente:** Open-Meteo Historical Weather API. https://open-meteo.com/
- **Punto:** lat 48.78, lon 2.29 (Sceaux, Francia), zona horaria Europe/Paris.
- **Periodo:** 01/12/2006 -> 31/03/2011 (incluye enero 2011 para referencia).
- **Como se obtuvo:** ejecutando `descargar_clima.py` (se guardo el CSV para que el notebook sea reproducible sin internet).

### Diccionario de variables

| Variable | Unidad | Descripcion |
|---|---|---|
| date | - | Fecha diaria |
| temp_max | grados C | Temperatura maxima del dia |
| temp_min | grados C | Temperatura minima del dia |
| temp_mean | grados C | Temperatura media del dia |

En el notebook se usan `temp_mean` del dia de la consulta y del dia siguiente. **Simplificacion declarada:**
se usa la temperatura real como sustituto de un pronostico; en produccion se reemplazaria por el pronostico meteorologico.

## 3. Nota sobre privacidad

El dataset no contiene datos personales identificables. Corresponde a un unico hogar anonimo.
