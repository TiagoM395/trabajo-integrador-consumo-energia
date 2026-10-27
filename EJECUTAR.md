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

## 6. Publicar en internet (gratis) con GitHub + Streamlit Community Cloud

> Streamlit Community Cloud publica gratis directo desde GitHub y da una dirección **HTTPS**
> (así la cámara del celular funciona en la pestaña *Factura*).

1. Subí el proyecto a un repositorio de GitHub:
   ```bash
   git init
   git add .
   git commit -m "Me paso o no me paso"
   git branch -M main
   git remote add origin https://github.com/USUARIO/REPOSITORIO.git
   git push -u origin main
   ```
   (`datos/crudos/` no se sube: está en `.gitignore`. El dataset limpio sí.)
2. Entrá a https://share.streamlit.io con tu cuenta de GitHub.
3. **Create app → Deploy a public app from GitHub**.
4. Elegí el repositorio, la rama `main` y el archivo **`streamlit_app.py`**.
5. En *Advanced settings* elegí **Python 3.12** o superior.
6. **Deploy**. En unos minutos tenés una URL del tipo `https://NOMBRE.streamlit.app`.

Cada `git push` actualiza la app publicada automáticamente.

Los modelos (`modelos/*.pkl`) se suben con el proyecto: la app los necesita para la predicción.

## 7. Correr las pruebas

```bash
python -m unittest discover -s tests -v
```

Deben pasar las 19 pruebas (cálculo, factura de EDEA, curva horaria y lectura de facturas con texto, QR y subsidio).

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
