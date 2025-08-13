# Amazon Scrapper FastAPI

Este proyecto es una API backend desarrollada con FastAPI para el análisis y scraping de productos de Amazon. Incluye autenticación de usuarios, verificación por correo electrónico y envío de códigos de confirmación usando Brevo (Sendinblue).

## Características

- Registro de usuarios con nombre de usuario, correo y contraseña.
- Envío de código de verificación por correo electrónico.
- Validación de correo electrónico mediante código.
- Inicio de sesión con nombre de usuario y contraseña.
- Integración con Brevo para envío de emails.
- Estructura modular y escalable.

## Requisitos

- Python 3.10+
- FastAPI
- Uvicorn
- sib-api-v3-sdk (Brevo)
- email-validator
- (Opcional) Supabase para almacenamiento

## Instalación

1. Clona el repositorio:
   ```
   git clone <URL_DEL_REPOSITORIO>
   cd Amazon-scrapper-fastApi/Amazon-scrapper
   ```

2. Crea y activa un entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configura tus variables de entorno en un archivo `.env`:
   ```
   GOOGLE_API_KEY="Your gemini api key"
   ACCESS_TOKEN="Your token access"
   BREVO_API_KEY="Your Brevo API key"
   ```

## Uso

1. Inicia el servidor:
   ```
   uvicorn app.main:app --reload
   ```

2. Accede a la documentación interactiva en [http://localhost:8000/docs](http://localhost:8000/docs).

## Endpoints principales

- `POST /register` — Registro de usuario.
- `GET /getVerificationCode` — Envío de código de verificación por correo.
- `POST /validateEmail` — Validación de correo con código.
- `POST /login` — Inicio de sesión.

## Estructura del proyecto

```
app/
  ├── main.py
  ├── api/
  │   └── routers/
  │       ├── auth.py
  │       └── ...
  ├── core/
  ├── schemas/
  ├── services/
  └── ...
```

