# Cómo abrir ¿Me paso o no me paso? (en tu PC)

Ya tenés todo instalado. No hace falta instalar nada más.

---

## Opción 1: la más fácil (doble clic)

1. Abrí la carpeta del proyecto en el Explorador de archivos.
2. Hacé **doble clic** en **`abrir_simulador.bat`**.
3. Se abre una ventana negra y, a los pocos segundos, la app en el navegador.
4. **No cierres la ventana negra** mientras lo usás. Para apagarlo, cerrá esa ventana.

---

## Opción 2: desde VS Code

1. En VS Code, arriba: **Terminal → New Terminal** (Terminal → Nueva terminal).
2. Abajo aparece la terminal. Copiá y pegá esto, y apretá **Enter**:

   ```
   python -m streamlit run streamlit_app.py
   ```

3. Se abre solo en el navegador. Si no se abre, entrá a: **http://localhost:8501**
4. Para apagarlo: hacé clic en la terminal y apretá **Ctrl + C**.

---

## Para verlo en el celular

1. El celular tiene que estar en **el mismo Wi-Fi** que la PC.
2. En la terminal de VS Code pegá esto (en vez del comando de arriba):

   ```
   python -m streamlit run streamlit_app.py --server.address 0.0.0.0
   ```

3. En la terminal aparece una línea **Network URL**, por ejemplo `http://192.168.0.15:8501`.
4. Escribí **esa dirección** en el navegador del celular.
5. Para escanear la factura desde el celular: pestaña **Factura → Escanear tu factura →
   Subir PDF o foto**, y elegí **"Tomar foto"**. (La opción **Sacar foto** solo anda cuando la
   app está publicada en internet, con `https://`.)

> Si el celular no carga la página, Windows puede estar bloqueando la conexión: cuando aparezca el
> aviso del Firewall, tocá **Permitir acceso**.

---

## Qué funciona en tu PC

| Cosa | ¿Funciona? |
|---|---|
| Todas las pestañas (Mi casa, Ambiente 3D, Factura, Análisis) | ✅ Sí |
| La predicción del paso 4 de Mi casa | ✅ Sí (usa los modelos de la carpeta `modelos/`) |
| Leer la factura en **PDF** | ✅ Sí |
| Leer la factura en **foto** | ✅ Sí: Tesseract con español ya está instalado en esta PC |
| **Sacar foto** desde el celular | ❌ Solo cuando la app está publicada (`https://`). Por Wi-Fi usá **Subir PDF o foto** |

Después de cambiar algo en los archivos, **cerrá la app y volvé a abrirla** para ver los cambios.

---

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| `Port 8501 is already in use` | Ya lo tenés abierto en otra ventana. Cerrá la otra, o usá `python -m streamlit run streamlit_app.py --server.port 8502` |
| `No module named streamlit` | Pegá `python -m pip install -r requirements.txt` y después volvé a probar. |
| La página quedó en blanco | Apretá **F5** en el navegador. |
