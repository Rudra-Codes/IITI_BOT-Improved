import os
import threading
import random
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException, Depends, BackgroundTasks, Body
import httpx
from pymongo import MongoClient
import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import pathway as pw
# from app.pipeline2 import Retriever
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URI"))

# Send a ping to confirm a successful connection
try:
  mongo_client.admin.command('ping')
  print("Main backend successfully connected to database")
except Exception as e:
  print(e)

database = mongo_client['IITI_BOT']
users_collection = database['users']
pending_users_collection = database['pending_users']

SECRET_KEY = os.getenv["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Using direct bcrypt to avoid passlib compatibility issues with newer bcrypt versions
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

class InputSchema(pw.Schema):
    chat_id: int
    email: str
    queries: str
    # session_id: str = pw.column_definition(primary_key=True)


class UserSignup(BaseModel):
    Name : str
    email : str
    phone : str
    password : str
    member_type : str
    department : Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class OTPVerify(BaseModel):
    email: str
    otp: str


def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        session_id: str = payload.get("session_id")
        if email is None or session_id is None:
            raise credentials_exception
        
        return email, session_id
    except JWTError:
        raise credentials_exception

def send_otp_email(receiver_email, otp):
    # sender_email
    password = os.getenv("app_password")

    message = MIMEMultipart("alternative")
    message["Subject"] = "OTP for IITI BOT"
    message["From"] = f"IITI BOT <{SENDER_EMAIL}>"
    message["To"] = receiver_email

    html_content = f"<strong>Your OTP is {otp}. Enjoy Brother!!!</strong>"
    part = MIMEText(html_content, "html")
    message.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(SENDER_EMAIL, password)
        server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())



# Pathway logic
def run_pathway():
    
    input_, output_writer = pw.io.http.rest_connector(
        webserver=pw.io.http.PathwayWebserver(host="0.0.0.0", port=8003),
        route="/ask",
        schema=InputSchema,
        delete_completed_queries=True
    )
    input2 = input_.with_columns(user_id=pw.this.id)
    retriever = Retriever()
    output = retriever(input2)
    input_.promise_universe_is_equal_to(output)
    output = output.with_universe_of(input_)
    # print(input_.typehints())
    output_writer(output)
    pw.run()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # threading.Thread(target=run_pathway, daemon=True).start()
    app.state.http_client = httpx.AsyncClient(timeout=300.0)
    print("HTTP client opened.")
    yield
    await app.state.http_client.aclose()
    print("HTTP client closed.")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/signup")
async def signup(user: UserSignup, background_tasks: BackgroundTasks):
    if users_collection.find_one({"email": user.email}) or pending_users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists or is pending verification")

    print(user.password)
    hashed_password = get_password_hash(user.password)
    otp = random.randint(100000, 999999)
    otp_expiry = datetime.utcnow() + timedelta(minutes=10)

    user_dict = {
        "email": user.email,
        "name": user.Name,
        "phone": user.phone,
        "password": hashed_password,
        "member_type": user.member_type,
        "department": user.department,
        "otp": str(otp),
        "otp_expiry": otp_expiry
    }
    pending_users_collection.insert_one(user_dict)

    background_tasks.add_task(send_otp_email, user.email, otp)

    return {"message": "OTP sent to your email. Please verify to complete registration."}

@app.post("/verify-email")
async def verify_email(data: OTPVerify):
    user = pending_users_collection.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found or already verified")

    if user["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.utcnow() > user["otp_expiry"]:
        raise HTTPException(status_code=400, detail="OTP expired")

    user.pop("otp")
    user.pop("otp_expiry")
    user["is_verified"] = True
    user["chats"] = []
    users_collection.insert_one(user)
    pending_users_collection.delete_one({"email": data.email})

    return {"message": "Email verified successfully!"}

@app.post("/login")
async def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not db_user.get("is_verified", False):
        raise HTTPException(status_code=403, detail="Email not verified. Please verify OTP.")

    token = create_access_token({"email": user.email,"session_id": db_user.get('phone','')})
    return {"access_token": token, "token_type": "bearer"}


@app.post('/ask')
async def ask_question(
    request: Request, 
    payload: dict = Body(...), 
    token: str = Depends(oauth2_scheme)
):
    email, session_id = get_current_user(token)
    
    payload['email'] = email

    excluded_headers = {'host', 'content-length', 'content-type'}
    headers = {
        k: v for k, v in request.headers.items() 
        if k.lower() not in excluded_headers
    }

    # 4. Use the global client and pass payload to `json=`
    pathway_response = await request.app.state.http_client.request(
        method=request.method,
        url="http://0.0.0.0:8003/ask",
        headers=headers,
        json=payload # httpx automatically handles json parsing.
    )

    response_headers = dict(pathway_response.headers)
    response_headers.pop("transfer-encoding", None)

    return Response(
        content=pathway_response.content,
        status_code=pathway_response.status_code,
        headers=response_headers
    )
@app.get('/history')
async def get_history(request: Request, token: str = Depends(oauth2_scheme)):
    print(token)
    email,_ = get_current_user(token)
    print(email)
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    history = user.get('chats', {})
    print(history)
    return history
