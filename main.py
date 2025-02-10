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
from sqlalchemy.orm import joinedload
from io import BytesIO
# Database connection URL for PostgreSQL
DATABASE_URL = "postgresql://alborz:n1m010@localhost:5432/akp"
# DATABASE_URL = "postgresql://postgres:n1m010@localhost:5432/akp"

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
    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

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


class AdminCreate(BaseModel):
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

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Security

def get_current_admin(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    """Validate JWT token and return current admin"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        admin = db.query(Admin).filter(Admin.username == username).first()

        if admin is None:
            raise HTTPException(status_code=401, detail="Admin not found")

        return admin

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")



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

from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key="your_secret_key")


@app.post("/admin/register")
def register_admin(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_admin = db.query(Admin).filter(Admin.username == username).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")

    new_admin = Admin(username=username, hashed_password=pwd_context.hash(password))
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"message": "Admin registered successfully"}

@app.post("/admin/login")
def login_admin(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin or not pwd_context.verify(password, admin.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    request.session["admin"] = admin.username  # Store in session
    return RedirectResponse(url="/admin/dashboard", status_code=303)

@app.get("/admin/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    admin = request.session.get("admin")
    if not admin:
        return RedirectResponse(url="/admin/login")

    return templates.TemplateResponse("dashboard.html", {"request": request, "admin": admin})

@app.get("/admin/logout")
def logout_admin(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login")

from fastapi.responses import StreamingResponse

# Download Excel
@app.get("/admin/download-excel")
async def download_excel(db: Session = Depends(get_db)):
    try:
        # دریافت تمام کاربران به همراه اطلاعات شخصی آن‌ها
        users = db.query(PersonalInformation).all()

        # تبدیل داده‌ها به یک DataFrame در pandas
        data = [
            {
                "شناسه": user.id,
                "نام": user.first_name,
                "نام خانوادگی": user.last_name,
                "وضعیت تأهل": user.marital_status,
                "تعداد افراد تحت تکفل": user.number_of_dependents,
                "نام پدر": user.father_name,
                "وضعیت خدمت سربازی": user.military_status,
                "نوع معافیت": user.exemption_type,
                "محل تولد": user.place_of_birth,
                "محل صدور": user.place_of_issue,
                "سابقه بیمه": user.insurance_history,
                "مدت بیمه": user.insurance_duration,
                "آدرس محل سکونت": user.residence_address,
                "نوع تولد": user.birth_type,
                "تلفن ثابت": user.fixed_number,
                "تلفن همراه": user.mobile_number,
                "نحوه آشنایی با ما": user.how_you_knew_us,
                "مسیر فایل رزومه": user.resume_file_path,
            }
            for user in users
        ]

        df = pd.DataFrame(data)

        # ایجاد یک فایل اکسل در حافظه
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="کاربران")
        output.seek(0)  # انتقال مکان‌نما به ابتدای فایل

        # استفاده از StreamingResponse برای ارسال فایل به عنوان پاسخ
        headers = {
            "Content-Disposition": "attachment; filename=users.xlsx"
        }
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/user/{user_id}")
async def get_user_details(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    # Fetch user details along with related information
    user = (
        db.query(PersonalInformation)
        .filter(PersonalInformation.id == user_id)
        .options(
            joinedload(PersonalInformation.job_applications),
            joinedload(PersonalInformation.educations),
            joinedload(PersonalInformation.work_experiences),
            joinedload(PersonalInformation.language_skills),
            joinedload(PersonalInformation.technology_skills),
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prepare the user data
    user_data = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "marital_status": user.marital_status,
        "number_of_dependents": user.number_of_dependents,
        "father_name": user.father_name,
        "military_status": user.military_status,
        "exemption_type": user.exemption_type,
        "place_of_birth": user.place_of_birth,
        "place_of_issue": user.place_of_issue,
        "insurance_history": user.insurance_history,
        "insurance_duration": user.insurance_duration,
        "residence_address": user.residence_address,
        "birth_type": user.birth_type,
        "fixed_number": user.fixed_number,
        "mobile_number": user.mobile_number,
        "how_you_knew_us": user.how_you_knew_us,
        "resume_file_path": user.resume_file_path,
        "job_applications": [
            {
                "id": job.id,
                "job_title": job.job_title,
                "cooperation_type": job.cooperation_type,
            }
            for job in user.job_applications
        ],
        "educations": [
            {
                "id": edu.id,
                "year": edu.year,
                "institution_name": edu.institution_name,
                "field_of_study": edu.field_of_study,
                "degree": edu.degree,
            }
            for edu in user.educations
        ],
        "work_experiences": [
            {
                "id": work.id,
                "organization": work.organization,
                "position": work.position,
                "start_date": work.start_date,
                "end_date": work.end_date,
                "last_salary": work.last_salary,
                "reason_for_leaving": work.reason_for_leaving,
            }
            for work in user.work_experiences
        ],
        "language_skills": [
            {
                "id": lang.id,
                "language": lang.language,
                "proficiency": lang.proficiency,
            }
            for lang in user.language_skills
        ],
        "technology_skills": [
            {
                "id": tech.id,
                "technology": tech.technology,
                "proficiency": tech.proficiency,
            }
            for tech in user.technology_skills
        ],
    }

    # Render the user-detail.html template with all the user data
    return templates.TemplateResponse(
        "user-details.html",
        {"request": request, "user": user_data}
    )

@app.get("/admin/user/{user_id}/download-excel")
async def download_user_excel(user_id: int, db: Session = Depends(get_db)):
    # دریافت اطلاعات کاربر
    user = db.query(PersonalInformation).filter(PersonalInformation.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    # دریافت اطلاعات مرتبط
    job_applications = db.query(JobApplication).filter(JobApplication.personal_information_id == user_id).all()
    educations = db.query(Education).filter(Education.personal_information_id == user_id).all()
    work_experiences = db.query(WorkExperience).filter(WorkExperience.personal_information_id == user_id).all()
    language_skills = db.query(LanguageSkill).filter(LanguageSkill.personal_information_id == user_id).all()
    technology_skills = db.query(TechnologySkill).filter(TechnologySkill.personal_information_id == user_id).all()

    # تبدیل داده‌ها به DataFrame
    user_data = pd.DataFrame([{
        "شناسه": user.id,
        "نام": user.first_name,
        "نام خانوادگی": user.last_name,
        "وضعیت تأهل": user.marital_status,
        "تعداد افراد تحت تکفل": user.number_of_dependents,
        "نام پدر": user.father_name,
        "وضعیت خدمت سربازی": user.military_status,
        "نوع معافیت": user.exemption_type,
        "محل تولد": user.place_of_birth,
        "محل صدور": user.place_of_issue,
        "سابقه بیمه": "بله" if user.insurance_history else "خیر",
        "مدت بیمه": user.insurance_duration,
        "آدرس محل سکونت": user.residence_address,
        "نوع تولد": user.birth_type,
        "تلفن ثابت": user.fixed_number,
        "تلفن همراه": user.mobile_number,
        "نحوه آشنایی با ما": user.how_you_knew_us,
        "مسیر فایل رزومه": f"http://185.208.175.233:5000/{user.resume_file_path}" if user.resume_file_path else "رزومه موجود نیست"
    }])

    job_data = pd.DataFrame([{
        "شناسه شغل": job.id,
        "عنوان شغل": job.job_title,
        "نوع همکاری": job.cooperation_type,
    } for job in job_applications]) if job_applications else pd.DataFrame(columns=["شناسه شغل", "عنوان شغل", "نوع همکاری"])

    education_data = pd.DataFrame([{
        "شناسه تحصیلات": edu.id,
        "مؤسسه": edu.institution_name,
        "مدرک": edu.degree,
        "رشته تحصیلی": edu.field_of_study,
    } for edu in educations]) if educations else pd.DataFrame(columns=["شناسه تحصیلات", "مؤسسه", "مدرک", "رشته تحصیلی"])

    work_data = pd.DataFrame([{
        "شناسه کار": work.id,
        "شرکت": work.organization,
        "سمت": work.position,
        "تاریخ شروع": work.start_date,
        "تاریخ پایان": work.end_date
    } for work in work_experiences]) if work_experiences else pd.DataFrame(columns=["شناسه کار", "شرکت", "سمت", "تاریخ شروع", "تاریخ پایان"])

    language_data = pd.DataFrame([{
        "شناسه زبان": lang.id,
        "زبان": lang.language,
        "سطح مهارت": lang.proficiency
    } for lang in language_skills]) if language_skills else pd.DataFrame(columns=["شناسه زبان", "زبان", "سطح مهارت"])

    tech_data = pd.DataFrame([{
        "شناسه مهارت فنی": tech.id,
        "فناوری": tech.technology,
        "سطح مهارت": tech.proficiency
    } for tech in technology_skills]) if technology_skills else pd.DataFrame(columns=["شناسه مهارت فنی", "فناوری", "سطح مهارت"])

    # ایجاد فایل اکسل در حافظه
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        user_data.to_excel(writer, index=False, sheet_name="اطلاعات کاربر")
        job_data.to_excel(writer, index=False, sheet_name="درخواست‌های شغلی")
        education_data.to_excel(writer, index=False, sheet_name="تحصیلات")
        work_data.to_excel(writer, index=False, sheet_name="سوابق کاری")
        language_data.to_excel(writer, index=False, sheet_name="مهارت‌های زبانی")
        tech_data.to_excel(writer, index=False, sheet_name="مهارت‌های فنی")

    output.seek(0)  # انتقال مکان‌نما به ابتدای فایل

    # استفاده از StreamingResponse برای ارسال فایل به عنوان پاسخ
    headers = {
        "Content-Disposition": f"attachment; filename=user_{user_id}_details.xlsx"
    }
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
from fastapi.responses import FileResponse
import os

@app.get("/admin/view-resume/{user_id}")
async def view_resume(user_id: int, db: Session = Depends(get_db)):
    user = db.query(PersonalInformation).filter(PersonalInformation.id == user_id).first()
    if not user or not user.resume_file_path:
        raise HTTPException(status_code=404, detail="Resume not found")

    return FileResponse(user.resume_file_path, media_type="application/pdf")


@app.get("/admin/users")
async def users_page(request: Request, db: Session = Depends(get_db)):
    users = db.query(PersonalInformation).all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


@app.get("/admin/download-resume/{user_id}")
async def download_resume(user_id: int, db: Session = Depends(get_db)):
    # Get user data
    user = db.query(PersonalInformation).filter(PersonalInformation.id == user_id).first()
    if not user or not user.resume_file_path:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume_path = Path(user.resume_file_path)

    # Convert relative path to absolute
    if not resume_path.is_absolute():
        resume_path = Path(os.getcwd()) / resume_path

    # Ensure file exists
    if not resume_path.exists():
        raise HTTPException(status_code=404, detail="Resume file not found")

    # Detect file MIME type
    mime_type, _ = mimetypes.guess_type(resume_path)
    mime_type = mime_type or "application/octet-stream"  # Default if unknown

    # Return file as downloadable response
    return FileResponse(
        path=resume_path,
        media_type=mime_type,
        filename=resume_path.name,
        headers={"Content-Disposition": f"attachment; filename={resume_path.name}"}
    )




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)