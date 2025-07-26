from fastapi import APIRouter, Body, HTTPException, Depends, Header, Query, Form, File, UploadFile
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Annotated
from functions.interview_questions import *
from fastapi.responses import JSONResponse
from app.utils.auth_util import basic_auth
import random
import shutil
import os
from app.config import keys
from datetime import datetime
import json
from pathlib import Path 
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import Candidate, Interview
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging


# router = APIRouter(prefix='/AI_Interview')
router = APIRouter()
logger = logging.getLogger(__name__)

CANDIDATE_INFO = {}

async def write_to_json(data, file_name):
	current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	filepath = Path(keys.directory).joinpath(current_time)
	os.makedirs(filepath, exist_ok=True)
	
	filepath_with_name = Path(filepath).joinpath(file_name)
	
	with open(filepath_with_name, 'w', encoding='utf-8') as f:
		json.dump(data, f, indent=4, default=str)
		print(f"Wrote {file_name} at {filepath_with_name}")

class CandidateDetails(BaseModel):
    candidate_name: Annotated[str, Field(..., description="Candidate Name", examples=["Pushpraj Gour"]) ]
    candidate_email: Annotated[str, Field(..., description="Candidate Email", examples=["abc@gmail.com"]) ]
    role: Annotated[str, Field(..., description="Job Role", examples=["AI/ML Engineer"]) ]
    skills: Annotated[str, Field(..., description="Skills of the candidate", examples=["Python, C, SQL, TensorFlow, OpenCV, PyTorch, FastAPI, Keras, Scikit-Learn, streamlit, Seaborn, NumPy, Pandas, Matplotlib"])]
    projects: Annotated[Optional[str], Field(None, description="Projects undertaken by the candidate", examples=["Project A description, Project B description"])]
    education: Annotated[str, Field(..., description="Highest education background of the candidate", examples=["B.Tech in Computer Science from XYZ University"])]
    achievements: Annotated[Optional[str], Field(None, description="Achievements of the candidate", examples=["Awarded Best Innovator in 2022, Published research paper on AI"])]
    experience: Annotated[Optional[str], Field(None, description="Work experience of the candidate", examples=["2 years at ABC Corp as a Data Scientist, 1 year at DEF Ltd as a Machine Learning Engineer"])]
    # resume: Optional[str] Gona to take entire resume pdf file, and then extract the details from it.

@router.post("/candidates/register")
async def register_candidate(
    candidate_data: CandidateDetails,
    db: AsyncSession = Depends(get_db)
):
    try:
        candidate_dict = candidate_data.model_dump()

        logger.info("Received candidate registration request for email: %s", candidate_dict.get('candidate_email'))

        candidate  = Candidate(
            name=candidate_dict['candidate_name'],
            email=candidate_dict['candidate_email'],
            role=candidate_dict['role'],
            skills=candidate_dict['skills'],
            projects=candidate_dict.get('projects'),
            education=candidate_dict['education'],
            achievements=candidate_dict.get('achievements'),
            experience=candidate_dict.get('experience')
        )

        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)

        logger.info("Candidate registered successfully with ID: %s", candidate.id)

        return JSONResponse(
            content={
                "status": "success",
                "message": "Candidate registered successfully.",
                "data": {
                    "id": candidate.id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "role": candidate.role,
                    "skills": candidate.skills,
                    "projects": candidate.projects,
                    "education": candidate.education,
                    "achievements": candidate.achievements,
                    "experience": candidate.experience
                }
            }
        )

    except SQLAlchemyError as db_err:
        logger.error("Database error during candidate registration: %s", str(db_err))
        await db.rollback()
        raise HTTPException(
            status_code=500,  #TODO: correct the status code
            detail="An error occurred while saving candidate data."
        )

    except Exception as exc:
        logger.exception("Unexpected error during candidate registration: %s", str(exc))
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while processing the registration. {exc}")

@router.post("/responses/upload")
async def upload_audio_response(question: str = Form(...), audio_file: UploadFile = File(...)):

    try:
        file_bytes = await audio_file.read()
        if not file_bytes:
            logger.warning("Empty audio file uploaded.")
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")
        

        audio_dir = Path(keys.directory).joinpath("responses_audio")  # .wav lossless format
        os.makedirs(audio_dir, exist_ok=True)

        # Generate a clear and concise file name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sanitized_question =  "_".join(question.strip().split()[:5]).replace("/", "_")  # Use first 5 words of the question
        file_name = f"response_{sanitized_question}_{timestamp}.wav"

        with open(audio_dir.joinpath(file_name), "wb") as f:
            f.write(file_bytes)

        logger.info("Audio file saved: %s", file_name)

        transcript_text = await process_audio_response(question, file_bytes)

        if not transcript_text:
            logger.warning("No transcript returned from processor.")
            raise HTTPException(
                status_code=500,
                detail="Failed to transcribe the audio response."
            )
        
        logger.info("Transcription successful for file: %s", file_name)

        return {
            "status": "success",
            "message": "Audio uploaded and transcribed successfully.",
            "transcript": transcript_text
        }

    except Exception as err:
        logger.exception(f"Error during audio upload/transcription. Error is {err}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the audio file. The error is {err}"
        )
    
@router.get("/candidate/{email}")
async def fetch_candidate_by_email(email: str, db: AsyncSession = Depends(get_db)):

    try:
        logger.info("Fetching candidate details for email: %s", email)

        result = await db.execute(select(Candidate).where(Candidate.email == email))
        candidate = result.scalar_one_or_none()
        logger.info("Fetched candidate details for email: %s", email)

        if not candidate:
            logger.warning("Candidate not found for email: %s", email)
            raise HTTPException(
                status_code=404,
                detail="Candidate not found."
            )

        logger.info("Candidate details successfully retrieved for email: %s", email)

        return {
            "status": "success",
            "message": "Candidate details fetched successfully.",
            "data": {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "role": candidate.role,
                "skills": candidate.skills,
                "projects": candidate.projects,
                "education": candidate.education,
                "achievements": candidate.achievements,
                "experience": candidate.experience
            }
        }


    except SQLAlchemyError as db_err:
        logger.error("Database error while fetching candidate details: %s", str(db_err))
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching candidate details. Error is {db_err}"
        )
    except Exception as exc:
        logger.exception("Unexpected error while fetching candidate: %s", str(exc))
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred while retrieving candidate information."
        )

# TODO: Implement get all interviews endpoint
@router.get("/candidates/{email}/interviews")
async def fetch_candidate_interviews(email: str, db: AsyncSession = Depends(get_db)):

    try:
        logger.info("Fetching interviews for candidate email: %s", email)
        result = await db.execute(
            select(Interview).join(Candidate).where(Candidate.email == email)
        )
        interviews = result.scalars().all()

        logger.info("Fetched %d interviews for candidate email: %s", len(interviews), email)

        if not interviews:
            logger.info("No interviews found for candidate email: %s", email)
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "No interviews found for this candidate.",
                    "data": []
                },
                status_code=200
            )
        logger.info("Found %d interview(s) for candidate: %s", len(interviews), email)

        interview_data =  [
            {
                "id": iv.id,
                "date": iv.date,
                "score": iv.score,
                "summary": iv.summary
            } for iv in interviews
        ]

        return JSONResponse(
            content={
                "status": "success",
                "message": "Interviews fetched successfully.",
                "data": interview_data
            })
    
    except SQLAlchemyError as db_err:
        logger.error("Database error while fetching interviews: %s", str(db_err))
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching interviews. Error is {db_err}"
        )
    except Exception as exc:
        logger.exception("Unexpected error while fetching interviews: %s", str(exc))
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred while retrieving interviews."
        )


# TODO: Implement update candidate details endpoint 
# TODO: Baisc idea is to have the existing candidate details fetched from the database, and then update the fields which are not None in the request body.
@router.put("/update_candidate/{email}")
async def update_candidate(email: str, updated_data: CandidateDetails, db: AsyncSession = Depends(get_db)):

    try:
        logger.info("Attempting to update candidate with email: %s", email)

        result = await db.execute(select(Candidate).where(Candidate.email == email))
        candidate = result.scalar_one_or_none()

        logger.info("Fetched candidate details for email: %s", email)

        if not candidate:
            logger.warning("Candidate not found with email: %s", email)
            raise HTTPException(
                status_code=404,
                detail="Candidate not found."
            )

        
        update_fields = updated_data.dict(exclude_unset=True)
        if not update_fields:
            logger.info("No fields provided to update for candidate: %s", email)
            raise HTTPException(
                status_code=400,
                detail="No update fields provided."
            )


        for field, value in updated_data.dict(exclude_unset=True).items():
            setattr(candidate, field, value)

        await db.commit()
        logger.info("Candidate details updated successfully for email: %s", email)
        return JSONResponse(
            content={
                "status": "success",
                "message": "Candidate details updated successfully.",
                "data":  list(update_fields.keys())}
        )
    

    
    except SQLAlchemyError as db_error:
        logger.warning(f"Error updating candidate details for email {email}: {db_error}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating candidate details. Error is {db_error}")
    
    except Exception as exc:
        logger.exception(f"Unexpected error while updating candidate: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating candidate details. The error is {exc}"
        )

@router.get("/candidates/{email}/interview-questions")
async def fetch_initial_interview_questions(email: str, db: AsyncSession = Depends(get_db)):

    try:
        logger.info("Fetching candidate details for email: %s", email)
        result = await db.execute(select(Candidate).where(Candidate.email == email))
        candidate = result.scalar_one_or_none()

        if not candidate:
            logger.warning("Candidate not found for email: %s", email)
            raise HTTPException(status_code=404, detail="Candidate not found")

        logger.info("Fetched candidate details for email: %s", email)
        
        candidate_info = {column.name: getattr(candidate, column.name) for column in candidate.__table__.columns}

        CANDIDATE_INFO.update(candidate_info)

    except SQLAlchemyError as db_err:
        logger.error("Database error while fetching candidate details: %s", str(db_err))
        raise HTTPException(
            status_code=500,
            detail=f"Database error while fetching candidate details. Error is {db_err}"
        )
    except Exception as exc:
        logger.exception("Unexpected error while fetching candidate: %s", str(exc))
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred while retrieving candidate information: {exc}"
        )

    try:
        logger.info("Generating initial questions for candidate email: %s", email)
        initial_question = await generate_initial_questions(candidate_info)

        if not initial_question:
            logger.error("Failed to generate initial questions for candidate email: %s", email)
            raise HTTPException(status_code=500, detail="Failed to generate initial questions.")
        
        logger.info("Initial questions successfully generated for email: %s", email)

        return JSONResponse(
            content={
                "status": "success",
                "message": "Initial questions generated successfully.",
                "data": {"question": initial_question}
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating initial questions: {str(e)}"
        )


@router.get("/interview/next-question")
async def fetch_next_interview_question():
    """
    This endpoint is to get the next question based on the last question response and the questions asked so far.
    """

    try:
        logger.info("Fetching next question based on last response and asked questions.")
        
        question = await next_question()

        if not question:
            logger.warning("No further questions available after the last response.")
            raise HTTPException(status_code=404, detail="No further questions available.")

        logger.info("Next question fetched successfully.")

        return JSONResponse(
            status_code=200,
            content = {
                "status": "success",
                "message": "Next question fetched successfully.",
                "data": {"question": question}
            }
        )
    
    except Exception as e:
        logger.exception("Error while fetching next question: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the next question: {str(e)}"
        )


@router.get("/candidate/feedback")
async def fetch_candidate_feedback():

    try:
        logging.info("Fetching feedback for the candidate based on responses and questions asked.")
        feedback_by_question, overall_analysis = await generate_feedback()

        if not feedback_by_question or not overall_analysis:
            logging.warning("No feedback available based on the responses and questions asked.")
            raise HTTPException(status_code=404, detail="No feedback available.")
        
        logging.info("Feedback fetched successfully for the candidate.")
        

        return JSONResponse(
            content={
                "status": "success",
                "message": "Feedback fetched successfully.",
                "data": {
                    "overall_feedback": overall_analysis,
                    "feedback_by_question": feedback_by_question
                    },
            },
            status_code=200
        )
    except Exception as e:
        logging.exception("Error while fetching feedback: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching feedback: {str(e)}"
        )