# Amazon Scraper FastAPI

Servicio backend para scrapear productos de Amazon, procesar los datos y realizar preguntas sobre ellos usando IA.  
Incluye autenticación de usuarios, verificación de correo y endpoints protegidos con JWT.

---

## Estructura del proyecto

```
app/
  main.py
  api/
    routers/
      auth.py
      health.py
      prompt.py
      scrape.py
  core/
    auth.py
    config.py
  schemas/
    auth.py
    prompt.py
    scrape.py
  services/
    gemini.py
    purify.py
    scraper.py
```

---

## Instalación

1. Clona el repositorio.
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Configura tu archivo `.env` con las variables necesarias:
   ```
   SUPABASE_URL=...
   SUPABASE_KEY=...
   JWT_SECRET=tu_clave_secreta_segura
   GOOGLE_API_KEY=...
   BREVO_API_KEY=...
   ```

---

## Uso

### 1. Ejecuta el servidor

```bash
python start.py
```

### 2. Endpoints principales

- **Autenticación**
  - `POST /register` — Registra un usuario nuevo.
  - `POST /login` — Inicia sesión y recibe un token JWT.
  - `GET /getVerificationCode` — Envía el código de verificación al correo (requiere estar autenticado).
  - `POST /validateEmail` — Verifica el correo con el código (requiere estar autenticado).
  - `GET /me` — Consulta los datos del usuario autenticado.

- **Scraping**
  - `POST /scrape` — Scrapea una URL de Amazon, normaliza los datos y los guarda en `data.json`.  
    **Protegido:** Solo usuarios autenticados y con correo verificado.

- **Preguntas IA**
  - `POST /prompt` — Realiza preguntas sobre los datos guardados en `data.json`.  
    **Protegido:** Solo usuarios autenticados y con correo verificado.

---

## Ejemplo de flujo

1. **Registro y login:**  
   Regístrate y obtén tu token JWT.
2. **Verificación de correo:**  
   Solicita el código y verifica tu correo.
3. **Scraping:**  
   Envía la URL de Amazon al endpoint `/scrape` (con tu token en el header).
4. **Preguntas:**  
   Usa `/prompt` para consultar sobre los datos guardados.

---

## Notas técnicas

- Los endpoints protegidos requieren el header:
  ```
  Authorization: Bearer <access_token>
  ```
- Los datos normalizados se guardan en `data.json` en la carpeta `data/`.
- El scraping usa Playwright en modo asíncrono.

---

## Requisitos

- Python 3.10+
- Playwright (`pip install playwright` y ejecuta `playwright install`)
- Supabase para gestión de usuarios
- Brevo (Sendinblue) para envío de correos

---

## Licencia

MIT

