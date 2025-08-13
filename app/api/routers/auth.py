import random
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, EmailStr
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
from supabase import create_client, Client
from datetime import datetime, timedelta
import bcrypt
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class ValidateEmailRequest(BaseModel):
    code: str

class LoginRequest(BaseModel):
    username: str
    password: str

def generate_code():
    return str(random.randint(100000, 999999))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")  # Pon una clave segura en tu .env
JWT_ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@router.post("/register")
async def register_user(data: RegisterRequest):
    # Verificar si el username ya existe
    username_check = supabase.table("users").select("id").eq("username", data.username).execute()
    if username_check.data:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    # Verificar si el email ya existe
    email_check = supabase.table("users").select("id").eq("email", data.email).execute()
    if email_check.data:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    code = generate_code()
    now = datetime.now().isoformat()
    # Hashear la contraseña antes de guardar
    hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    result = supabase.table("users").insert({
        "username": data.username,
        "email": data.email,
        "password": hashed_password,
        "verification_code": code,
        "is_verified": False,
        "created_at": now,
        "updated_at": now
    }).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al registrar usuario")
    return {"message": "Usuario registrado correctamente"}

@router.get("/getVerificationCode")
async def get_verification_code(current_user: dict = Depends(get_current_user)):
    # Solo usa el email del usuario autenticado
    if not current_user or "email" not in current_user:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    email = current_user["email"]

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
async def validate_email(
    data: ValidateEmailRequest,
    current_user: dict = Depends(get_current_user)
):
    if not current_user or "email" not in current_user:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
    email = current_user["email"]

    # Buscar el usuario por email en Supabase
    result = supabase.table("users").select("verification_code", "is_verified").eq("email", email).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="No se encontró usuario para este correo")
    user = result.data[0]
    if user["is_verified"]:
        return {"message": "El correo ya está verificado"}
    if data.code != user["verification_code"]:
        raise HTTPException(status_code=400, detail="Código incorrecto")
    # Marcar usuario como verificado
    supabase.table("users").update({"is_verified": True}).eq("email", email).execute()
    return {"message": "Correo verificado correctamente"}

@router.post("/login")
async def login_user(data: LoginRequest):
    result = supabase.table("users").select("*").eq("username", data.username).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user = result.data[0]
    if not bcrypt.checkpw(data.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    token = create_access_token({"sub": user["username"], "email": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
