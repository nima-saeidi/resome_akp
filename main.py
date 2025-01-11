from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import os

# Database connection URL for PostgreSQL
DATABASE_URL = "postgresql://postgres:n1m010@localhost:5432/akp"

# Create the engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()


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
        # Ensure the static folder exists
        os.makedirs("static", exist_ok=True)

        # Save the uploaded file to the static folder as bytes
        file_path = f"static/{resume.filename}"
        with open(file_path, "wb") as buffer:
            # Read the file content as bytes and write it to the file
            buffer.write(await resume.read())

        # Update the user's resume file path in the database
        db_user = db.query(PersonalInformation).filter(PersonalInformation.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.resume_file_path = file_path
        db.commit()

        return {"message": "Resume saved successfully", "file_path": file_path}
    except HTTPException as http_exc:
        # Re-raise HTTPException to avoid wrapping it in another exception
        raise http_exc
    except Exception as e:
        db.rollback()
        # Return a generic error message without exposing the binary data
        raise HTTPException(status_code=500, detail="Failed to save resume. Please try again.")

# API to save technology skill for a user
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