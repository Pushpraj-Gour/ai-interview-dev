from fastapi import APIRouter, Body, HTTPException, Depends, Header, Query, Form, File, UploadFile
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Annotated
from functions.interview_questions import initial_questions
from fastapi.responses import JSONResponse
from app.utils.auth_util import basic_auth
import random
import shutil
import os
from app.config import keys
from datetime import datetime
import json
from pathlib import Path 
from functions.interview_questions import process_audio_response_2


router = APIRouter(prefix='/data_gathering')

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
    role: Annotated[str, Field(..., description="Job Role", examples=["AI/ML Engineer"]) ]
    skills: Annotated[str, Field(..., description="Skills of the candidate", examples=["Python, C, SQL, TensorFlow, OpenCV, PyTorch, FastAPI, Keras, Scikit-Learn, streamlit, Seaborn, NumPy, Pandas, Matplotlib"])]
    projects: Annotated[Optional[str], Field(None, description="Projects undertaken by the candidate", examples=["Project A description, Project B description"])]
    education: Annotated[str, Field(..., description="Highest education background of the candidate", examples=["B.Tech in Computer Science from XYZ University"])]
    achievements: Annotated[Optional[str], Field(None, description="Achievements of the candidate", examples=["Awarded Best Innovator in 2022, Published research paper on AI"])]
    experience: Annotated[Optional[str], Field(None, description="Work experience of the candidate", examples=["2 years at ABC Corp as a Data Scientist, 1 year at DEF Ltd as a Machine Learning Engineer"])]
    # resume: Optional[str] Gona to take entire resume pdf file, and then extract the details from it.

@router.post("/candidate_details" ,dependencies=[Depends(basic_auth)])
async def candidate_details(
    candidate_details: CandidateDetails
):
    candidate_info = candidate_details.model_dump()

    try:
        response = await initial_questions(candidate_info)
        return JSONResponse(
            content={
                "status": "success",
                "message": "Interview questions generated successfully.",
                "data": response
            },
            status_code=200
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating interview questions: {str(e)}"
        )
    
@router.get("/get_questions", )
async def get_questions():

    questions = [
      "Can you explain the core differences between supervised and unsupervised learning?",
      "How do you typically use Python's Pandas library for data manipulation and cleaning?",
      "What are the primary differences between TensorFlow and PyTorch, and when would you choose one over the other?",
      "Describe a scenario where you would use Scikit-Learn versus a deep learning framework like Keras.",
      "How do you leverage OpenCV for computer vision tasks?",
      "Explain the process of building a simple web application for a machine learning model using FastAPI or Streamlit.",
      "What is the purpose of SQL in an AI/ML project workflow?",
      "How do you approach handling missing data in a dataset?",
      "Can you describe a project where you applied deep learning concepts using TensorFlow or PyTorch?",
      "How do you interpret and visualize model performance metrics using libraries like Matplotlib or Seaborn?",
      "What techniques do you use to prevent overfitting in machine learning models?",
      "Describe your experience with model deployment and monitoring in a production environment.",
      "How do you optimize a machine learning model for performance and efficiency?",
      "Can you explain the concept of transfer learning and when it is beneficial?",
      "Discuss a challenging AI/ML problem you've encountered and how you resolved it."
    ]

    # return any random question from the list
    random.shuffle(questions)
    return { "question": questions[0] }

@router.post('/transcribe-response')
async def transcribe_response(response: str = Body(..., description="User's response to the interview question")):
    """
    Endpoint to submit the user's response to an interview question.
    This is a placeholder for future implementation of response handling.
    """
    # Here you would typically process the response, e.g., store it or analyze it.
    print(response)
    return JSONResponse(
        content={
            "status": "success",
            "message": "Response submitted successfully.",
            "data": {"response": response}
        },
        status_code=200
    )

# Store Q&A for later evaluation
interview_data = []  # Each entry: { "question": str, "transcript": str, "audio_file": str }


@router.post("/upload-response")
async def upload_response(question: str = Form(...), audio: UploadFile = File(...)):
    try:
        file_bytes = await audio.read()
        if not file_bytes:
            raise ValueError("Uploaded audio file is empty.")
        # Save audio file locally
        audio_dir = Path(keys.directory).joinpath("responses_audio")  # .wav lossless format
        os.makedirs(audio_dir, exist_ok=True)

        # Generate a clear and concise file name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        sanitized_question = "_".join(question.split()[:5])  # Use first 5 words of the question
        file_name = f"question_{sanitized_question}_{timestamp}.wav"

        with open(audio_dir.joinpath(file_name), "wb") as buffer:
            buffer.write(file_bytes)

        # Placeholder for actual transcription logic
        transcript_text = await process_audio_response_2(file_bytes)

        # Save question + transcription for later evaluation
        interview_data.append({
            "question": question,
            "transcript": transcript_text,
            "audio_file": str(audio_dir.joinpath(file_name))
        })

        await write_to_json(interview_data, "interview_data.json")

        return {
            "status": "success",
            "message": "Audio uploaded and transcribed successfully.",
            "transcript": transcript_text
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
