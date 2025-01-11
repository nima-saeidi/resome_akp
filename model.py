from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Database connection URL for PostgreSQL
DATABASE_URL = "postgresql://postgres:n1m010@localhost:5432/akp"

# Create the engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()


class PersonalInformation(Base):
    __tablename__ = 'personal_information'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    marital_status = Column(String)  # مجرد or متاهل
    number_of_dependents = Column(Integer)
    father_name = Column(String)
    military_status = Column(String)  # پایان خدمت or معاف
    exemption_type = Column(String)
    place_of_birth = Column(String)
    place_of_issue = Column(String)
    insurance_history = Column(Boolean)
    insurance_duration = Column(String)
    residence_address = Column(String)
    birth_type = Column(String)
    fixed_number = Column(String)
    mobile_number = Column(String)
    how_you_knew_us = Column(String)  # بونت, لبات, نگرام, بستارام, سایر
    resume_file_path = Column(String)  # New column to store the resume file path

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
    cooperation_type = Column(String)  # تمام وقت, پاره وقت, همکاری خارج از سازمان
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
    proficiency = Column(String)  # خوب, متوسط, ضعیف
    personal_information = relationship("PersonalInformation", back_populates="language_skills")


class TechnologySkill(Base):
    __tablename__ = 'technology_skill'

    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_information_id = Column(Integer, ForeignKey('personal_information.id'))
    technology = Column(String)
    proficiency = Column(String)  # خوب, متوسط, ضعیف
    personal_information = relationship("PersonalInformation", back_populates="technology_skills")


# Create all tables in the database
Base.metadata.create_all(bind=engine)