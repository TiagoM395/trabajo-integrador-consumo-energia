# ¿Me paso o no me paso?

Asistente de consumo eléctrico para el hogar — Trabajo Integrador de Aprendizaje Automático.

El usuario residencial consume a ciegas: se entera de cuánto consumió cuando llega la factura, uno o dos meses después, cuando ya no puede corregir nada. Este proyecto responde, con lo que el medidor inteligente ya registró:

- **¿Cuánta energía voy a consumir en las próximas 24 h?** → Regresión
- **¿Me paso de mi meta diaria?** → Clasificación binaria
- **¿Cómo está mi coseno φ y me pueden multar?** → Indicador complementario
- **¿Cuánto me cuesta, incluido un posible recargo?** → Costo estimado

Si el clasificador y la regresión + umbral no coinciden, la app lo dice: *"Los modelos no coinciden. Estás cerca de tu límite"*.

---

## Contenido del repositorio

| Archivo | Descripción |
| --- | --- |
| `Trabajo.md` | Documento del trabajo: problemática, ficha del proyecto, methodology, riesgos y limitaciones. |
| `Trabajo.pdf` | Versión para entregar. |
| `Consigna_TP_Integrador_Aprendizaje_Automatico.docx` | Consigna de la cátedra. |

El código de los modelos se irá agregando a medida que se desarrolle.

---

## Cómo obtener el dataset

El dataset **no está en el repositorio** (pesa ~127 MB y GitHub no admite archivos mayores a 100 MB). Descargalo manualmente:

**UCI Machine Learning Repository — *Individual Household Electric Power Consumption***
Hébrail & Bérard · Licencia CC BY 4.0

1. Entrá a <https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption>
2. Descargá el archivo y descomprimilo.
3. Colocá el contenido en la carpeta `datasets/` de este proyecto (queda ignorada por git).

El dataset trae mediciones por minuto de un hogar entre diciembre de 2006 y noviembre de 2010: potencia activa y reactiva, voltaje, intensidad y 3 submedidores (cocina, lavadero, termotanque/aire).

Como fuente complementaria se usa **Open-Meteo Historical API** para la temperatura horaria del lugar.

---

## Dataset esperado

```
datasets/
└── household_power_consumption.txt   # ~127 MB, no versionado
```

---

## Licencia

El código de este repositorio es de uso académico. El dataset conserva su licencia original CC BY 4.0 (UCI).