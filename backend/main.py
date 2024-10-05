import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from dotenv import load_dotenv
import jwt
from jwt import PyJWTError
import requests
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from databases import Database

# load environment variables from .env file
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# dummy credentials from .env file
DUMMY_USERNAME = os.getenv("DUMMY_USERNAME")
DUMMY_PASSWORD = os.getenv("DUMMY_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# token settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# JWT token expiration time
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Set up SQLite database
DATABASE_URL = "sqlite:///./funds.db"
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define the PurchaseRecord model
class PurchaseRecordModel(Base):
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    scheme_name = Column(String, index=True)
    units = Column(Integer)
    purchase_time = Column(DateTime)
    value = Column(Float)

# Create the database tables
Base.metadata.create_all(bind=engine)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str
    password: str

class PurchaseRequest(BaseModel):
    scheme_code: str
    units: int

class FundScheme(BaseModel):
    Scheme_Code: int
    ISIN_Div_Payout_ISIN_Growth: str
    ISIN_Div_Reinvestment: str
    Scheme_Name: str
    Net_Asset_Value: float
    Date: str
    Scheme_Type: str
    Scheme_Category: str
    Mutual_Fund_Family: str

# global variable to store fund families
fund_families = []

def authenticate_user(username: str, password: str):
    if username == DUMMY_USERNAME and password == DUMMY_PASSWORD:
        return True
    return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

# fetch fund families at startup
@app.on_event("startup")
async def startup_event():
    await database.connect()
    global fund_families
    url = "https://latest-mutual-fund-nav.p.rapidapi.com/latest?Scheme_Type=Open"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "latest-mutual-fund-nav.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        funds = response.json()
        fund_families = list(set(fund["Mutual_Fund_Family"] for fund in funds))
    else:
        print(f"Failed to fetch fund families: {response.status_code}")

# close the database connection on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()

# endpoint to get fund families
@app.get("/fund_families")
def get_fund_families():
    return {"families": fund_families}

# login endpoint to get token
@app.post("/login", response_model=Token)
def login(user: User):
    if not authenticate_user(user.username, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# dependency to extract and verify JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
    return decode_access_token(token)

# fetch open-ended schemes for selected fund family (using RapidAPI)
@app.get("/funds/{family}", response_model=list[FundScheme])
def fetch_fund_schemes(family: str, token: str = Depends(get_current_user)):
    url = f"https://latest-mutual-fund-nav.p.rapidapi.com/fetch_schemes?Mutual_Fund_Family={family}"

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "latest-mutual-fund-nav.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch schemes")

    return response.json()

# endpoint to purchase mutual fund units
@app.post("/funds/purchase")
async def purchase_fund_units(purchase: PurchaseRequest, token: str = Depends(get_current_user)):
    # fetch the current value of the mutual fund scheme from the API
    url = f"https://latest-mutual-fund-nav.p.rapidapi.com/fetch_scheme_value?Scheme_Code={purchase.scheme_code}"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "latest-mutual-fund-nav.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch scheme value")

    current_value = response.json().get('Net_Asset_Value')  
    scheme_info = response.json()
    scheme_name = scheme_info.get('Scheme_Name', 'Unknown Scheme')

    # create a new purchase record and store it in the database
    purchase_record = PurchaseRecordModel(
        scheme_name=scheme_name,
        units=purchase.units,
        purchase_time=datetime.now(),
        value=current_value
    )

    # insert into the database
    async with database.transaction():
        query = PurchaseRecordModel.__table__.insert().values(
            scheme_name=purchase_record.scheme_name,
            units=purchase_record.units,
            purchase_time=purchase_record.purchase_time,
            value=purchase_record.value
        )
        await database.execute(query)

    return {"message": f"Purchased {purchase.units} units of {scheme_name}", "current_value": current_value}

# endpoint to get all purchased mutual funds with their latest values
@app.get("/funds/purchases")
async def get_purchased_funds(token: str = Depends(get_current_user)):
    # fetch records from the database
    query = select(PurchaseRecordModel)
    records = await database.fetch_all(query)
    purchases = [
        {
            "scheme_name": record.scheme_name,
            "units": record.units,
            "purchase_time": record.purchase_time,
            "value": record.value,
        }
        for record in records
    ]
    return purchases

# simple home route for testing
@app.get("/")
def read_root():
    return {"message": "Welcome to the Mutual Fund API!"}
