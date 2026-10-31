# Cómo ejecutar ¿Me paso o no me paso?

## 1. Requisitos

- **Python 3.11 o superior** (probado con 3.13).
- Opcional, para leer **fotos** de facturas en tu PC: **Tesseract OCR** (ver punto 5).
  Sin Tesseract la app funciona igual: lee facturas en **PDF** y permite cargar los datos a mano.

## 2. Instalar (una sola vez)

Abrí una terminal en la carpeta del proyecto:

```bash
# (recomendado) crear un entorno virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# instalar dependencias
pip install -r requirements.txt
```

## 3. Ejecutar

```bash
streamlit run streamlit_app.py
```

Se abre solo en el navegador, en **http://localhost:8501**. Para cortarla: `Ctrl + C` en la terminal.

## 4. Abrirla desde el celular (misma red Wi-Fi)

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```

En la terminal aparece una **Network URL** (por ejemplo `http://192.168.0.15:8501`). Abrila en el
navegador del celular, conectado al mismo Wi-Fi.

**Escanear la factura desde el celular:**
- Pestaña **Factura → Escanear tu factura → Subir PDF o foto**: en el celular, el botón
  ofrece **"Tomar foto"** o elegir un archivo. Funciona siempre.
- La pestaña **Sacar foto** usa la cámara dentro de la página. Los navegadores del celular solo
  permiten la cámara en páginas **HTTPS**: funciona en la versión publicada (punto 6), pero no en
  `http://192.168…` de la red local. En la red local usá "Subir PDF o foto".

Consejos para la foto: factura apoyada en una mesa, bien iluminada, derecha y sin sombras;
encuadrá la parte del **consumo** y el **total a pagar**. El PDF que manda EDEA por mail es lo más
preciso. Siempre se revisan los datos antes de usarlos.

## 5. Instalar Tesseract (para leer fotos de facturas)

Tesseract es un programa del sistema, no un paquete de Python: por eso no está en
`requirements.txt`. En Streamlit Community Cloud se instala solo con `packages.txt`.

- **Windows** (una terminal):
  ```bash
  winget install --id UB-Mannheim.TesseractOCR
  ```
  Después, agregar el idioma español: descargar
  [`spa.traineddata`](https://github.com/tesseract-ocr/tessdata_best/raw/main/spa.traineddata) y copiarlo
  en `C:\Program Files\Tesseract-OCR\tessdata\` (pide permiso de administrador).
  La app encuentra Tesseract en esa carpeta aunque no esté en el `PATH`.
- **macOS:** `brew install tesseract tesseract-lang`
- **Linux (Debian/Ubuntu):** `sudo apt install tesseract-ocr tesseract-ocr-spa`

Los códigos QR y de barras se leen con `zxing-cpp`, que se instala con `requirements.txt`.

## 6. Publicar en internet (gratis) con Streamlit Community Cloud

Streamlit Community Cloud publica desde GitHub y entrega una dirección **HTTPS**, necesaria para
usar la cámara del celular en la pestaña *Factura*. Este proyecto ya tiene como repositorio remoto
público `TiagoM395/trabajo-integrador-consumo-energia`, con `streamlit_app.py` en la raíz.

1. Verificá que la versión que querés publicar ya esté subida a GitHub. Community Cloud despliega
   los commits de GitHub, no los cambios locales sin commit. La rama de trabajo actual es `tiago2`;
   si vas a desplegar esa versión, primero subí los cambios a esa rama. También podés desplegar
   `main` si esa es la versión aprobada.
2. Entrá a <https://share.streamlit.io> con la cuenta de GitHub que tiene acceso al repositorio.
3. Elegí **Create app → Deploy a public app from GitHub**.
4. Seleccioná el repositorio `TiagoM395/trabajo-integrador-consumo-energia`, la rama que contiene
   la versión deseada y el archivo **`streamlit_app.py`**.
5. En *Advanced settings*, seleccioná **Python 3.12**. Las dependencias Python están fijadas en
   `requirements.txt`; Tesseract y español se instalan desde `packages.txt`.
6. Elegí el nombre de la URL pública y presioná **Deploy**. Al terminar, la dirección será del
   tipo `https://NOMBRE.streamlit.app`.

Cada `git push` a la rama seleccionada actualiza la aplicación publicada automáticamente. Los
modelos están versionados en `modelos/` y la app los carga localmente; no hace falta configurar
Secrets para ejecutarla.

**App creada:** <https://me-paso-consumo-energia-tiago.streamlit.app/> (rama `main`, Python 3.12).
La versión subida actualmente muestra un error en **Análisis** porque ese commit no incluye
`explicaciones/README_ANALISIS.md`; sincronizá los archivos de análisis antes de compartirla como
entrega terminada. La visualización en teléfonos ya fue comprobada y funciona correctamente.

**Persistencia:** las casas guardadas se escriben en `sesiones/` en el disco local de la app. En
Community Cloud ese almacenamiento no es persistente ante reinicios o recreaciones del entorno;
compartí la URL de una casa solo como enlace temporal hasta decidir una base de datos persistente.

## 7. Correr las pruebas

```bash
python -m unittest discover -s tests -v
```

Deben pasar las 23 pruebas (cálculo, factura de EDEA, curva horaria, lectura de facturas con
texto, QR y subsidio, y preparación/separación temporal de los datos).

## 8. Actualizar el dataset de eficiencia (opcional)

```bash
python datos/preparar_dataset.py
```

Descarga la versión más reciente desde data.gov.au y regenera
`datos/electrodomesticos_eficiencia.csv`. Fuentes y detalle de columnas: `datos/FUENTES.md`.

## 9. Problemas frecuentes

| Problema | Solución |
|---|---|
| `streamlit: command not found` | Activá el entorno virtual o usá `python -m streamlit run streamlit_app.py`. |
| "El OCR (Tesseract) no está instalado" | Subí el PDF de la factura, cargá los datos a mano o instalá Tesseract (punto 5). |
| La cámara no aparece en el celular | Estás entrando por `http://`. Usá "Subir PDF o foto" o la versión publicada (HTTPS). |
| Se perdieron mis electrodomésticos | El estado vive en la sesión del navegador: al cerrar la pestaña o tocar «Reiniciar todo» la casa vuelve a quedar vacía. |
| El puerto 8501 está ocupado | `streamlit run streamlit_app.py --server.port 8502` |
