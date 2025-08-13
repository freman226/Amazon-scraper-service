import random
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
from supabase import create_client, Client
from datetime import datetime

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

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.post("/register")
async def register_user(data: RegisterRequest):
    code = generate_code()
    now = datetime.now().isoformat()
    result = supabase.table("users").insert({
        "username": data.username,
        "email": data.email,
        "password": data.password,
        "verification_code": code,
        "is_verified": False,
        "created_at": now,
        "updated_at": now
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al registrar usuario")
    return {"message": "Usuario registrado correctamente"}

@router.get("/getVerificationCode")
async def get_verification_code(email: EmailStr = Query(...)):
    # Buscar el usuario por email en Supabase
    result = supabase.table("users").select("verification_code").eq("email", email).execute()
    if not result.data or not result.data[0]["verification_code"]:
        raise HTTPException(status_code=404, detail="No se encontró código para este correo")

    code = result.data[0]["verification_code"]

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
    # Buscar el usuario por email en Supabase
    result = supabase.table("users").select("verification_code", "is_verified").eq("email", data.email).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="No se encontró usuario para este correo")
    user = result.data[0]
    if user["is_verified"]:
        return {"message": "El correo ya está verificado"}
    if data.code != user["verification_code"]:
        raise HTTPException(status_code=400, detail="Código incorrecto")
    # Marcar usuario como verificado
    supabase.table("users").update({"is_verified": True}).eq("email", data.email).execute()
    return {"message": "Correo verificado correctamente"}

@router.post("/login")
async def login_user(data: LoginRequest):
    # Buscar usuario en Supabase
    result = supabase.table("users").select("*").eq("username", data.username).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user = result.data[0]
    if data.password != user["password"]:
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    if not user["is_verified"]:
        raise HTTPException(status_code=403, detail="Correo no verificado")
    return {"message": "Login exitoso"}
