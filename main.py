from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Database connection URL for PostgreSQL
DATABASE_URL = "postgresql://postgres:n1m010@localhost:5432/akp"

# Create the engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define your models
class PersonalInformation(Base):
    __tablename__ = 'personal_information'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    marital_status = Column(String)
    number_of_dependents = Column(Integer)
    father_name = Column(String)
    military_status = Column(String)
    exemption_type = Column(String)
    place_of_birth = Column(String)
    place_of_issue = Column(String)
    insurance_history = Column(Boolean)
    insurance_duration = Column(String)
    residence_address = Column(String)
    birth_type = Column(String)
    fixed_number = Column(String)
    mobile_number = Column(String)
    how_you_knew_us = Column(String)
    resume_file_path = Column(String)  # Path to the uploaded resume file

    # Relationships
    job_applications = relationship("JobApplication", back_populates="personal_information")
    educations = relationship("Education", back_populates="personal_information")
    work_experiences = relationship("WorkExperience", back_populates="personal_information")
    language_skills = relationship("LanguageSkill", back_populates="personal_information")
    technology_skills = relationship("TechnologySkill", back_populates="personal_information")


class JobApplication(Base):
    __tablename__ = 'job_application'

    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_information_id = Column(Integer, ForeignKey('personal_information.id'))
    job_title = Column(String)
    cooperation_type = Column(String)
    personal_information = relationship("PersonalInformation", back_populates="job_applications")


class Education(Base):
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_information_id = Column(Integer, ForeignKey('personal_information.id'))
    year = Column(Integer)
    institution_name = Column(String)
    field_of_study = Column(String)
    degree = Column(String)
    personal_information = relationship("PersonalInformation", back_populates="educations")


class WorkExperience(Base):
    __tablename__ = 'work_experience'

    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_information_id = Column(Integer, ForeignKey('personal_information.id'))
    organization = Column(String)
    position = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    last_salary = Column(String)
    reason_for_leaving = Column(String)
    personal_information = relationship("PersonalInformation", back_populates="work_experiences")


class LanguageSkill(Base):
    __tablename__ = 'language_skill'

    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_information_id = Column(Integer, ForeignKey('personal_information.id'))
    language = Column(String)
    proficiency = Column(String)
    personal_information = relationship("PersonalInformation", back_populates="language_skills")


class TechnologySkill(Base):
    __tablename__ = 'technology_skill'

    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_information_id = Column(Integer, ForeignKey('personal_information.id'))
    technology = Column(String)
    proficiency = Column(String)
    personal_information = relationship("PersonalInformation", back_populates="technology_skills")


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)


# Create all tables in the database
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (replace with specific origins in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Serve static files (e.g., resumes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for request and response
class PersonalInformationCreate(BaseModel):
    first_name: str
    last_name: str
    marital_status: Optional[str] = None
    number_of_dependents: Optional[int] = None
    father_name: Optional[str] = None
    military_status: Optional[str] = None
    exemption_type: Optional[str] = None
    place_of_birth: Optional[str] = None
    place_of_issue: Optional[str] = None
    insurance_history: Optional[bool] = None
    insurance_duration: Optional[str] = None
    residence_address: Optional[str] = None
    birth_type: Optional[str] = None
    fixed_number: Optional[str] = None
    mobile_number: Optional[str] = None
    how_you_knew_us: Optional[str] = None


class TechnologySkillCreate(BaseModel):
    technology: str
    proficiency: str


class LanguageSkillCreate(BaseModel):
    language: str
    proficiency: str


class JobApplicationCreate(BaseModel):
    job_title: str
    cooperation_type: str


class EducationCreate(BaseModel):
    year: int
    institution_name: str
    field_of_study: str
    degree: str


class WorkExperienceCreate(BaseModel):
    organization: str
    position: str
    start_date: date
    end_date: date
    last_salary: str
    reason_for_leaving: str


class AdminRegister(BaseModel):
    username: str
    password: str


class AdminLogin(BaseModel):
    username: str
    password: str


# JWT utilities
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# Admin authentication dependency
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


async def get_current_admin(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


# Ensure the static folder exists
os.makedirs("static", exist_ok=True)


# API to save personal information and return user ID
@app.post("/save-personal-info", response_model=int)
async def save_personal_info(
    personal_info: PersonalInformationCreate,
    db: Session = Depends(get_db)
):
    try:
        # Create a new PersonalInformation object
        db_personal_info = PersonalInformation(**personal_info.dict())

        # Add to the database
        db.add(db_personal_info)
        db.commit()
        db.refresh(db_personal_info)

        # Return the generated user ID
        return db_personal_info.id
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# API to save resume file for a user
@app.post("/save-resume/{user_id}")
async def save_resume(
    user_id: int,
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Save the uploaded file to the static folder
        file_path = f"static/{resume.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await resume.read())

        # Update the user's resume file path in the database
        db_user = db.query(PersonalInformation).filter(PersonalInformation.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.resume_file_path = file_path
        db.commit()

        return {"message": "Resume saved successfully", "file_path": file_path}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Admin registration
@app.post("/admin/register")
async def admin_register(
    admin: AdminRegister,
    db: Session = Depends(get_db)
):
    # Check if admin already exists
    db_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if db_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")

    # Hash the password
    hashed_password = pwd_context.hash(admin.password)

    # Create new admin
    db_admin = Admin(username=admin.username, hashed_password=hashed_password)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    return {"message": "Admin registered successfully"}


# Admin login
@app.post("/admin/login")
async def admin_login(
    admin: AdminLogin,
    db: Session = Depends(get_db)
):
    # Check if admin exists
    db_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if not db_admin or not db_admin.verify_password(admin.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create JWT token
    access_token = create_access_token(data={"sub": db_admin.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Admin dashboard
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    # Fetch all users with their personal information
    users = db.query(PersonalInformation).all()
    return templates.TemplateResponse("admin.html", {"request": request, "users": users})


# Admin login page
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Admin register page
@app.post("/admin/register")
async def admin_register(
    admin: AdminRegister,  # JSON input (username and password)
    db: Session = Depends(get_db)
):
    # Check if admin already exists
    db_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if db_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")

    # Hash the password
    hashed_password = pwd_context.hash(admin.password)

    # Create new admin
    db_admin = Admin(username=admin.username, hashed_password=hashed_password)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    return {"message": "Admin registered successfully", "username": db_admin.username}
# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)