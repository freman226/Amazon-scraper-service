import random
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os

router = APIRouter()

# Diccionario temporal para pruebas: {email: code}
codes = {}
# Diccionario temporal para pruebas: {username: password}
users = {}
emails_to_usernames = {}

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class ValidateEmailRequest(BaseModel):
    email: EmailStr
    code: str

class LoginRequest(BaseModel):
    username: str
    password: str

def generate_code():
    return str(random.randint(100000, 999999))

@router.post("/register")
async def register_user(data: RegisterRequest):
    code = generate_code()
    codes[data.email] = code  # Guardar el código temporalmente
    users[data.username] = data.password  # Guardar usuario por username
    emails_to_usernames[data.email] = data.username  # Relacionar email con username
    return {"message": "Usuario registrado correctamente"}

@router.get("/getVerificationCode")
async def get_verification_code(email: EmailStr = Query(...)):
    code = codes.get(email)
    if not code:
        raise HTTPException(status_code=404, detail="No se encontró código para este correo")

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = "Tu código de verificación"
    sender = {"name": "Amazon Scraper Service", "email": "freman226@gmail.com"}
    to = [{"email": email}]
    html_content = (
        f"<html><body>"
        f"<h1>Código de verificación</h1>"
        f"<p>Tu código de verificación es: <b>{code}</b></p>"
        f"</body></html>"
    )

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        subject=subject,
        sender=sender
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        return {"message": "Código de verificación enviado al correo"}
    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Error enviando correo: {e}")

@router.post("/validateEmail")
async def validate_email(data: ValidateEmailRequest):
    saved_code = codes.get(data.email)
    if not saved_code:
        raise HTTPException(status_code=404, detail="No se encontró código para este correo")
    if data.code != saved_code:
        raise HTTPException(status_code=400, detail="Código incorrecto")
    # Aquí podrías marcar el usuario como verificado en la base de datos
    return {"message": "Correo verificado correctamente"}

@router.post("/login")
async def login_user(data: LoginRequest):
    saved_password = users.get(data.username)
    if not saved_password:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if data.password != saved_password:
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    return {"message": "Login exitoso"}
