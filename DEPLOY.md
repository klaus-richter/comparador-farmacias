# 🚀 Guía de Despliegue: Comparador de Farmacias

Este proyecto se compone de:
1. **Frontend (HTML/CSS/JS)** 👉 Se publica gratis en **GitHub Pages**.
2. **Backend (FastAPI + Playwright)** 👉 Se despliega gratis/bajo costo en **Render**, **Railway** o **Fly.io** (usando el `Dockerfile` incluido).

---

## 1️⃣ Paso 1: Desplegar el Backend (Render / Railway)

Dado que el backend usa navegadores reales (Playwright) para farmacias como Cruz Verde y Ahumada, se empaqueta con Docker.

### Opción A: Render.com (Recomendado - Fácil y Gratis)
1. Crea una cuenta en [render.com](https://render.com).
2. Haz clic en **New +** -> **Web Service**.
3. Conecta tu repositorio de GitHub.
4. Render detectará automáticamente el archivo `Dockerfile`.
5. En **Instance Type**, selecciona **Free**.
6. Haz clic en **Create Web Service**.
7. Una vez desplegado, copia tu URL pública (ejemplo: `https://comparador-farmacias.onrender.com`).

---

## 2️⃣ Paso 2: Conectar el Frontend a tu Backend

En `frontend/app.js`, edita la línea 4 con tu URL de Render:

```javascript
const API = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:8000"
  : "https://TU-BACKEND-EN-RENDER.onrender.com";
```

---

## 3️⃣ Paso 3: Publicar el Frontend en GitHub Pages

1. Sube tu proyecto a GitHub:
   ```bash
   git init
   git add .
   git commit -m "Comparador de farmacias completo"
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```
2. En tu repositorio de GitHub:
   - Ve a **Settings** -> **Pages**.
   - En **Build and deployment** > **Source**, selecciona `Deploy from a branch`.
   - En **Branch**, selecciona `main` y en carpeta selecciona `/frontend` (o `/root` si mueves los archivos).
   - Guarda los cambios.
3. ¡Tu comparador estará online para todo el mundo! 🎉
