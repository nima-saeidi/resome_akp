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
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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
import pandas as pd
from io import BytesIO
# Database connection URL for PostgreSQL
DATABASE_URL = "postgresql://alborz:n1m010@localhost:5432/akp"

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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = SessionLocal()
    db_admin = db.query(Admin).filter(Admin.username == username).first()
    if db_admin is None:
        raise credentials_exception
    return db_admin


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

@app.post("/save-technology-skill/{user_id}")
async def save_technology_skill(
    user_id: int,
    tech_skill: TechnologySkillCreate,
    db: Session = Depends(get_db)
):
    try:
        # Create a new TechnologySkill object
        db_tech_skill = TechnologySkill(**tech_skill.dict(), personal_information_id=user_id)

        # Add to the database
        db.add(db_tech_skill)
        db.commit()
        db.refresh(db_tech_skill)

        return {"message": "Technology skill saved successfully", "id": db_tech_skill.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# API to save language skill for a user
@app.post("/save-language-skill/{user_id}")
async def save_language_skill(
    user_id: int,
    lang_skill: LanguageSkillCreate,
    db: Session = Depends(get_db)
):
    try:
        # Create a new LanguageSkill object
        db_lang_skill = LanguageSkill(**lang_skill.dict(), personal_information_id=user_id)

        # Add to the database
        db.add(db_lang_skill)
        db.commit()
        db.refresh(db_lang_skill)

        return {"message": "Language skill saved successfully", "id": db_lang_skill.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# API to save job application for a user
@app.post("/save-job-application/{user_id}")
async def save_job_application(
    user_id: int,
    job_app: JobApplicationCreate,
    db: Session = Depends(get_db)
):
    try:
        # Create a new JobApplication object
        db_job_app = JobApplication(**job_app.dict(), personal_information_id=user_id)

        # Add to the database
        db.add(db_job_app)
        db.commit()
        db.refresh(db_job_app)

        return {"message": "Job application saved successfully", "id": db_job_app.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# API to save education for a user
@app.post("/save-education/{user_id}")
async def save_education(
    user_id: int,
    education: EducationCreate,
    db: Session = Depends(get_db)
):
    try:
        # Create a new Education object
        db_education = Education(**education.dict(), personal_information_id=user_id)

        # Add to the database
        db.add(db_education)
        db.commit()
        db.refresh(db_education)

        return {"message": "Education saved successfully", "id": db_education.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# API to save work experience for a user
@app.post("/save-work-experience/{user_id}")
async def save_work_experience(
    user_id: int,
    work_exp: WorkExperienceCreate,
    db: Session = Depends(get_db)
):
    try:
        # Create a new WorkExperience object
        db_work_exp = WorkExperience(**work_exp.dict(), personal_information_id=user_id)

        # Add to the database
        db.add(db_work_exp)
        db.commit()
        db.refresh(db_work_exp)

        return {"message": "Work experience saved successfully", "id": db_work_exp.id}
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
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Check if admin exists
    db_admin = db.query(Admin).filter(Admin.username == form_data.username).first()
    if not db_admin or not db_admin.verify_password(form_data.password):
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


# Download Excel
@app.get("/admin/download-excel")
async def download_excel(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    try:
        # Fetch all users with their personal information
        users = db.query(PersonalInformation).all()

        # Convert the data to a pandas DataFrame
        data = [
            {
                "ID": user.id,
                "First Name": user.first_name,
                "Last Name": user.last_name,
                "Marital Status": user.marital_status,
                "Number of Dependents": user.number_of_dependents,
                "Father Name": user.father_name,
                "Military Status": user.military_status,
                "Exemption Type": user.exemption_type,
                "Place of Birth": user.place_of_birth,
                "Place of Issue": user.place_of_issue,
                "Insurance History": user.insurance_history,
                "Insurance Duration": user.insurance_duration,
                "Residence Address": user.residence_address,
                "Birth Type": user.birth_type,
                "Fixed Number": user.fixed_number,
                "Mobile Number": user.mobile_number,
                "How You Knew Us": user.how_you_knew_us,
                "Resume File Path": user.resume_file_path,
            }
            for user in users
        ]

        df = pd.DataFrame(data)

        # Create an Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        output.seek(0)

        # Return the Excel file as a downloadable response
        return FileResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="users.xlsx",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)