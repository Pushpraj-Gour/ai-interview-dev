from fastapi import APIRouter, Body, HTTPException, Depends, Header, Query, Form, File, UploadFile, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Annotated, Callable, Awaitable, TypeVar
from functions.interview_questions import *
from fastapi.responses import JSONResponse
from app.utils.auth_util import basic_auth
import random
import shutil
import os
import asyncio
from app.config import keys
from datetime import datetime
import json
from pathlib import Path 
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.models import Candidate, Interview, InterviewFeedback
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# router = APIRouter(prefix='/AI_Interview')
router = APIRouter()
logger = logging.getLogger(__name__)

CANDIDATE_INFO = {}

T = TypeVar('T')

async def execute_with_retry(
    operation: Callable[[AsyncSession], Awaitable[T]], 
    db_session: AsyncSession, 
    max_retries: int = 3
) -> T:
    """
    Execute database operation with retry logic for connection issues.
    
    Args:
        operation: A callable that takes db_session as parameter and returns a coroutine
        db_session: The database session
        max_retries: Maximum number of retry attempts
    
    Returns:
        Result of the operation
        
    Raises:
        HTTPException: If operation fails after all retries
    """
    for attempt in range(max_retries):
        try:
            return await operation(db_session)
        except SQLAlchemyError as db_err:
            error_msg = str(db_err)
            logger.error(f"Database error (attempt {attempt + 1}): {error_msg}")
            
            # Check if it's a connection-related error
            if ("connection is closed" in error_msg.lower() or 
                "interface error" in error_msg.lower() or
                "connection was closed" in error_msg.lower()):
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying database operation (attempt {attempt + 2})")
                    await asyncio.sleep(1)  # Wait before retry
                    continue
                else:
                    raise HTTPException(
                        status_code=503,
                        detail="Database connection unavailable. Please try again later."
                    )
            else:
                # Non-connection related database error, don't retry
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error: {db_err}"
                )
        except Exception as exc:
            logger.exception(f"Unexpected error (attempt {attempt + 1}): {str(exc)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying due to unexpected error (attempt {attempt + 2})")
                await asyncio.sleep(1)
                continue
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected error occurred during database operation."
                )
    
    # This should never be reached due to the logic above, but needed for type checking
    raise HTTPException(
        status_code=500,
        detail="Unexpected error: All retry attempts exhausted without proper exception handling."
    )

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
    async def register_operation(db_session: AsyncSession) -> Candidate:
        candidate_dict = candidate_data.model_dump()
        logger.info(f"Received candidate registration request for email:{candidate_dict.get('candidate_email')}")

        candidate = Candidate(
            name=candidate_dict['candidate_name'],
            email=candidate_dict['candidate_email'],
            role=candidate_dict['role'],
            skills=candidate_dict['skills'],
            projects=candidate_dict.get('projects'),
            education=candidate_dict['education'],
            achievements=candidate_dict.get('achievements'),
            experience=candidate_dict.get('experience')
        )

        db_session.add(candidate)
        await db_session.commit()
        await db_session.refresh(candidate)

        logger.info(f"Candidate registered successfully with ID: {candidate.id}")
        return candidate

    try:
        candidate = await execute_with_retry(register_operation, db)
        
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
    except HTTPException:
        # Re-raise HTTP exceptions from execute_with_retry
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error during candidate registration: {str(exc)}")
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

        # with open(audio_dir.joinpath(file_name), "wb") as f:
        #     f.write(file_bytes)

        logger.info(f"Audio file saved: {file_name}")

        transcript_text = await process_audio_response(question, file_bytes)

        if not transcript_text:
            logger.warning("No transcript returned from processor.")
            raise HTTPException(
                status_code=500,
                detail="Failed to transcribe the audio response."
            )
        
        logger.info(f"Transcription successful for file: {file_name}")

        return JSONResponse(content={
        "status": "success",
        "message": "Audio uploaded and transcribed successfully.",
        "transcript": transcript_text
    })

    except Exception as err:
        logger.exception(f"Error during audio upload/transcription. Error is {err}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the audio file. The error is {err}"
        )
    
@router.get("/candidate/{email}")
async def fetch_candidate_by_email(email: str, db: AsyncSession = Depends(get_db)):

    async def fetch_operation(db_session: AsyncSession) -> Candidate:
        logger.info(f"Fetching candidate details for email: {email}")
        result = await db_session.execute(select(Candidate).where(Candidate.email == email))
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            logger.warning(f"Candidate not found for email: {email}")
            raise HTTPException(
                status_code=404,
                detail="Candidate not found."
            )
        
        logger.info(f"Candidate details successfully retrieved for email: {email}")
        return candidate

    try:
        candidate = await execute_with_retry(fetch_operation, db)
        
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
    except HTTPException:
        # Re-raise HTTP exceptions from execute_with_retry
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error while fetching candidate: {str(exc)}")
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred while retrieving candidate information."
        )

# # TODO: Implement get all interviews endpoint
# @router.get("/candidates/{email}/interviews")
# async def fetch_candidate_interviews(email: str, db: AsyncSession = Depends(get_db)):

#     async def fetch_interviews_operation(db_session: AsyncSession):
#         logger.info(f"Fetching interviews for candidate email: {email}")
#         result = await db_session.execute(
#             select(Interview).join(Candidate).where(Candidate.email == email)
#         )
#         interviews = result.scalars().all()
#         logger.info(f"Fetched {len(interviews)} interviews for candidate email: {email}")
#         return interviews

#     try:
#         interviews = await execute_with_retry(fetch_interviews_operation, db)

#         if not interviews:
#             logger.info(f"No interviews found for candidate email: {email}")
#             return JSONResponse(
#                 content={
#                     "status": "success",
#                     "message": "No interviews found for this candidate.",
#                     "data": []
#                 },
#                 status_code=200
#             )
#         logger.info(f"Found {len(interviews)} interview(s) for candidate: {email}")

#         interview_data =  [
#             {
#                 "id": iv.id,
#                 "date": iv.date,
#                 "score": iv.score,
#                 "summary": iv.summary
#             } for iv in interviews
#         ]

#         return JSONResponse(
#             content={
#                 "status": "success",
#                 "message": "Interviews fetched successfully.",
#                 "data": interview_data
#             })
#     except HTTPException:
#         # Re-raise HTTP exceptions from execute_with_retry
#         raise
#     except Exception as exc:
#         logger.exception(f"Unexpected error while fetching interviews: {str(exc)}")
#         raise HTTPException(
#             status_code=500,
#             detail="Unexpected error occurred while retrieving interviews."
#         )


# TODO: Implement update candidate details endpoint 
# TODO: Baisc idea is to have the existing candidate details fetched from the database, and then update the fields which are not None in the request body.
@router.put("/update_candidate/{email}")
async def update_candidate(email: str, updated_data: CandidateDetails, db: AsyncSession = Depends(get_db)):

    async def update_operation(db_session: AsyncSession) -> Candidate:
        logger.info(f"Attempting to update candidate with email: {email}")

        result = await db_session.execute(select(Candidate).where(Candidate.email == email))
        candidate = result.scalar_one_or_none()

        logger.info(f"Fetched candidate details for email: {email}")

        if not candidate:
            logger.warning(f"Candidate not found with email: {email}")
            raise HTTPException(
                status_code=404,
                detail="Candidate not found."
            )

        update_fields = updated_data.dict(exclude_unset=True)
        if not update_fields:
            logger.info(f"No fields provided to update for candidate: {email}")
            raise HTTPException(
                status_code=400,
                detail="No update fields provided."
            )

        for field, value in updated_data.dict(exclude_unset=True).items():
            setattr(candidate, field, value)

        await db_session.commit()
        logger.info(f"Candidate details updated successfully for email: {email}")
        return candidate

    try:
        candidate = await execute_with_retry(update_operation, db)
        
        update_fields = updated_data.dict(exclude_unset=True)
        return JSONResponse(
            content={
                "status": "success",
                "message": "Candidate details updated successfully.",
                "data": list(update_fields.keys())
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions from execute_with_retry
        raise
    except Exception as exc:
        logger.exception(f"Unexpected error while updating candidate: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating candidate details. The error is {exc}"
        )

# @router.get("/candidates/{email}/interview-questions")
# async def fetch_initial_interview_questions(email: str, db: AsyncSession = Depends(get_db)):
#     return JSONResponse(
#         content={
#             "status": "success",
#             "message": "Initial questions generated successfully.",
#             "data": {"question": "Can you explain the difference between a list and a tuple in Python?"}
#         }
#     )
    
@router.get("/candidates/{email}/interview-questions")
async def fetch_initial_interview_questions(email: str, db: AsyncSession = Depends(get_db)):

    async def fetch_candidate_operation(db_session: AsyncSession) -> Candidate:
        logger.info(f"Fetching candidate details for email: {email}")
        result = await db_session.execute(select(Candidate).where(Candidate.email == email))
        candidate = result.scalar_one_or_none()

        if not candidate:
            logger.warning(f"Candidate not found for email: {email}")
            raise HTTPException(status_code=404, detail="Candidate not found")

        logger.info(f"Fetched candidate details for email: {email}")
        return candidate

    try:
        candidate = await execute_with_retry(fetch_candidate_operation, db)
        
        candidate_info = {column.name: getattr(candidate, column.name) for column in candidate.__table__.columns}
        CANDIDATE_INFO.update(candidate_info)

        logger.info(f"Generating initial questions for candidate email:{email}")
        initial_question = await generate_initial_questions(candidate_info)

        if not initial_question:
            logger.error(f"Failed to generate initial questions for candidate email: {email}")
            raise HTTPException(status_code=500, detail="Failed to generate initial questions.")
        
        logger.info(f"Initial questions successfully generated for email: {email}")

        return JSONResponse(
            content={
                "status": "success",
                "message": "Initial questions generated successfully.",
                "data": {"question": initial_question}
            }
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"An error occurred while generating initial questions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating initial questions: {str(e)}"
        )


@router.get("/next-question")
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
        logger.exception(f"Error while fetching next question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the next question: {str(e)}"
        )


from sqlalchemy.future import select
from app.db.models import Candidate, InterviewFeedback

from datetime import datetime
from app.db.models import Candidate, Interview, InterviewFeedback

@router.get("/candidate/{email}/overall/feedback")
async def fetch_candidate_feedback(email: str, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Fetching feedback for: {email}")
        
        # 🎯 1. Generate feedback (from AI logic or wherever)
        feedback_by_question, overall_analysis = await generate_feedback()

        if not feedback_by_question or not overall_analysis:
            raise HTTPException(status_code=404, detail="No feedback available.")

        # 🎯 2. Get candidate
        result = await db.execute(select(Candidate).where(Candidate.email == email))
        candidate = result.scalars().first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found.")

        # 🎯 3. Create Interview entry
        new_interview = Interview(
            candidate_id=candidate.id,
            score=overall_analysis.get("overall_score", 0),      # safely fetch score
            summary=overall_analysis.get("overall_reasoning", ""),  # safely fetch summary
            created_at=datetime.utcnow()  # timestamp
        )
        db.add(new_interview)
        await db.flush()  # So new_interview.id is available

        # 🎯 4. Save to InterviewFeedback (linked to new_interview)
        feedback_record = InterviewFeedback(
            candidate_id=candidate.id,
            interview_id=new_interview.id,  # Link it!
            overall_feedback=overall_analysis,
            question_feedback=feedback_by_question,
        )
        db.add(feedback_record)

        await db.commit()

        logger.info("Feedback fetched and saved.")

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
        logger.exception("Error while saving or fetching feedback")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{interview_id}/feedback")
async def get_feedback_by_interview(interview_id: int, db: AsyncSession = Depends(get_db)):
    # Query interview with eagerly loaded feedback_data relationship
    result = await db.execute(
        select(Interview)
        .options(selectinload(Interview.feedback_data))
        .where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Now safely access the feedback_data relationship
    feedback_records = interview.feedback_data
    
    if not feedback_records:
        return {
            "status": "success",
            "data": None,
            "message": "No feedback available for this interview"
        }
    
    # Return the feedback data from the first (or most recent) feedback record
    feedback_record = feedback_records[0] if len(feedback_records) == 1 else feedback_records[-1]
    
    return {
        "status": "success",
        "data": {
            "overall_feedback": feedback_record.overall_feedback,
            "question_feedback": feedback_record.question_feedback,
            "timestamp": feedback_record.timestamp.isoformat() if feedback_record.timestamp else None
        }
    }

@router.get("/candidate/{email}/interviews")
async def get_all_interviews(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Candidate)
        .options(selectinload(Candidate.interviews))
        .where(Candidate.email == email)
    )
    candidate = result.scalars().first()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if not candidate.interviews:
        return JSONResponse(
            content={"status": "success", "interviews": []},
            status_code=200
        )

    interviews_data = [
        {
            "id": interview.id,
            "score": interview.score,
            "summary": interview.summary,
            "created_at": interview.created_at.isoformat(),
        }
        for interview in candidate.interviews
    ]

    return JSONResponse(
        content={"status": "success", "interviews": interviews_data},
        status_code=200
    )


