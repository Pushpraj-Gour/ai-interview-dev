import asyncio
import json
import uuid
from app.utils import llm_util
from app.config import model
from app.config import keys
from functions import prompts
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
from io import BytesIO
import requests
from elevenlabs.client import ElevenLabs
from fastapi import APIRouter, Body, HTTPException, Depends, Header, Query, Form, File, UploadFile
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, RootModel, ValidationError
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)
# Add logs to a all the important places

CANDIDATE_INFO = {}
MAJOR_QUESTIONS = []
QUESTION_ASKED = []
QUESTION_ANSWERED = {}
LAST_QUESTION_ASKED = ""
LAST_QUESTION_ASKED_IS_FOLLOW_UP = False


async def write_to_json(data, file_name):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = Path(keys.directory).joinpath(current_time)
    os.makedirs(filepath, exist_ok=True)
    
    filepath_with_name = Path(filepath).joinpath(file_name)
    
    with open(filepath_with_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, default=str)
        print(f"Wrote {file_name} at {filepath_with_name}")
        logging.info(f"Wrote {file_name} at {filepath_with_name}")

class Questions(BaseModel):
            questions: List[str]


@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
async def generate_initial_questions(candidate_info: Dict):

    try:
        CANDIDATE_INFO.update(candidate_info)

        data = {
            "candidate_name": candidate_info.get("name"),
            "role": candidate_info.get("role"),
            "skills": candidate_info.get("skills"),
            "education": candidate_info.get("education"),
        }
    
    except Exception as e:
        logging.error(f"An error occurred while gathering candidate information: {str(e)}")
        raise HTTPException(status_code=400, detail=f"An error occurred while gathering candidate information: {str(e)}")
    
    logging.info(f"Candidate info validated and stored.")
    
    try:
        user_message = prompts.generate_basic_user_message["user_message"].format(**data)
        output = await llm_util.llm_genai_2(prompt=user_message, response_schema=Questions)
        logging.info(f"Successfully received questions from LLM.")

        await write_to_json(output, "initial_questions.json")

    except Exception as e:
        logging.error(f"Failed to generate questions via LLM.{str(e)}")
        raise HTTPException(status_code=400, detail=f"An error occurred while generating initial questions: {str(e)}")

    if not output:
        logging.error("No questions returned by LLM.")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate initial questions. Please try again later."
        )
    
    MAJOR_QUESTIONS.extend(output.get("questions", []))	
    
    question_to_ask = MAJOR_QUESTIONS.pop(0)
    QUESTION_ASKED.append(question_to_ask)
    global LAST_QUESTION_ASKED
    LAST_QUESTION_ASKED = question_to_ask

    logging.info(f"First question to ask: {question_to_ask}")

    return question_to_ask

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
async def transcribe_audio(elevenlabs, audio_data: BytesIO):
    return elevenlabs.speech_to_text.convert(
        file=audio_data,
        model_id="scribe_v1",
        tag_audio_events=True,
        language_code="eng",
        diarize=True,
    )


async def process_audio_response(question:str, audio_file: bytes):

    if not audio_file:
        logging.error("Uploaded audio file is empty.")
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    try:
        elevenlabs = ElevenLabs(api_key=keys.elevenlabs_api_key)
        audio_data = BytesIO(audio_file)
        audio_data.seek(0) # Ensure pointer is at the beginning
        
        logging.info("Audio file loaded into memory successfully.")

    except Exception as e:
        logging.error(f"Failed to initialize ElevenLabs or load audio.")
        raise HTTPException(status_code=500, detail=f"Internal error while preparing audio for transcription.")

    logging.info("Audio file processed successfully.")

    try:
        response = await transcribe_audio(elevenlabs, audio_data)
    except Exception as e:
        logging.error(f"Audio transcription failed after retries.")
        raise ValueError(f"An error occurred while processing the audio file: {str(e)}")
    
    if not response or not getattr(response, "text", None):
        logging.error("Failed to transcribe the audio file.")
        raise HTTPException(
            status_code=500,
            detail="Failed to transcribe the audio. Ensure audio quality is sufficient and try again."
        )

    # transcription = {
    #     "transcription": response.text,
    #     "transcription_response": response,
    #     "timestamp": datetime.now().isoformat(),
    # }
    # await write_to_json(transcription, f"transcription_{uuid.uuid4().hex}.json")

    transcription = response.text
    QUESTION_ANSWERED[LAST_QUESTION_ASKED] = transcription

    logging.info(f"Transcription for question '{question}' completed successfully.")
    return transcription

class QuestionSuggestion(BaseModel):
    decision: Literal["follow_up", "major_question"]
    reasoning: str  # Why this choice was made
    follow_up_question: Optional[str]  # Populated if decision == "follow_up"
    major_question_selected: Optional[str]  # Populated if decision == "major_question"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
async def fetch_next_question_from_llm(data):
    user_message_template = prompts.generate_question_based_on_response_3["user_message"]
    user_message = user_message_template.format(**data)
    return await llm_util.llm_genai_2(user_message, response_schema=QuestionSuggestion)

async def next_question():

    global LAST_QUESTION_ASKED_IS_FOLLOW_UP, LAST_QUESTION_ASKED

    try:

        if LAST_QUESTION_ASKED_IS_FOLLOW_UP:
            LAST_QUESTION_ASKED_IS_FOLLOW_UP = False
            if not MAJOR_QUESTIONS:
                logging.error("No more major questions available after follow-up.")
                raise HTTPException(status_code=404, detail="No more questions available.")
            
            question_to_ask = MAJOR_QUESTIONS.pop(0)
            QUESTION_ASKED.append(question_to_ask)
            LAST_QUESTION_ASKED = question_to_ask

            logging.info(f"Next question to ask after follow-up: {question_to_ask}")
            return question_to_ask


        if not CANDIDATE_INFO:
            logging.error("Candidate information is not provided, cannot generate next question.")
            raise HTTPException(status_code=400, detail="Candidate information is not provided.")
        
        if not MAJOR_QUESTIONS:
            logging.error("No more major questions available.")
            raise HTTPException(status_code=404, detail="No more Initial questions available.")
        
        candidate_info = CANDIDATE_INFO.copy()

        data = {
            "candidate_name": candidate_info.get("name"),
            "role": candidate_info.get("role"),
            "skills": candidate_info.get("skills"),
            "major_questions": MAJOR_QUESTIONS,
            "questions_asked": QUESTION_ASKED,
            "last_question": LAST_QUESTION_ASKED,
            "response": QUESTION_ANSWERED[LAST_QUESTION_ASKED]
        }

        # user_message = prompts.generate_question_based_on_response_3["user_message"].format(**data)

        # with open("user_message.json", "w") as f:
        #     json.dump(user_message, f, indent=4)
        
        output = await fetch_next_question_from_llm(data)

        if not output:
            logging.error("No output received from LLM for next question generation.")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate the next question. Please try again later."
            )
        logging.info(f"LLM output for next question: {output}")

    except Exception as e:
        logging.error(f"Error generating next question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the next question: {str(e)}")

    # with open("output.json", "w") as f:
    #     json.dump(output, f, indent=4)

    try:

        decision = output.get("decision")

        if decision == "follow_up":
            follow_up_question = output.get("follow_up_question")
            if not follow_up_question:
                logging.error("Follow-up question is not provided in the output of llm call.")
                raise HTTPException(status_code=400, detail="Follow-up question is not provided.")
            
            QUESTION_ASKED.append(follow_up_question)
            LAST_QUESTION_ASKED = follow_up_question
            LAST_QUESTION_ASKED_IS_FOLLOW_UP = True

            logging.info(f"Follow-up question to ask: {follow_up_question}")
            return follow_up_question
        
        elif decision == "major_question":
            major_question_selected = output.get("major_question_selected")
            if not major_question_selected:
                raise HTTPException(status_code=400, detail="Major question is not provided.")
            
            if major_question_selected not in MAJOR_QUESTIONS:
                logging.warning(f"Selected major question '{major_question_selected}' has already been asked or does not exist.")
            
            QUESTION_ASKED.append(major_question_selected)
            MAJOR_QUESTIONS.remove(major_question_selected)
            LAST_QUESTION_ASKED = major_question_selected
            return major_question_selected
        
    # If anything goes wrong, we will select a question from the major questions that have not been asked yet
    except Exception as e:
        logging.exception(f"Error processing LLM output for next question: {str(e)}")

        if not MAJOR_QUESTIONS:
            logging.error("No more major questions available after processing LLM output.")
            raise HTTPException(status_code=404, detail="No more major questions available.")
        
        fallback_question = MAJOR_QUESTIONS.pop(0)
        QUESTION_ASKED.append(fallback_question)
        LAST_QUESTION_ASKED = fallback_question

        logging.info(f"Fallback major question selected: {fallback_question}")
        return fallback_question
    
class DetailedAnalysisResponse(BaseModel):
    communication_score: int
    communication_reasoning: str
    content_quality_score: int
    content_quality_reasoning: str
    domain_insight_score: int
    domain_insight_reasoning: str
    strategic_depth_score: int
    strategic_depth_reasoning: str
    professional_tone_score: int
    professional_tone_reasoning: str
    ideal_answer: str

class DedicatedAnalysis(BaseModel):
    question: str
    overall_score: int
    overall_reasoning: str
    question_and_response_detailed_analysis: List[DetailedAnalysisResponse]

class Analysis(BaseModel):
    overall_analysis: str
    question_analysis: List[DedicatedAnalysis]
    
async def generate_feedback():

    if not CANDIDATE_INFO or "role" not in CANDIDATE_INFO:
        logging.error("Candidate role is missing in candidate information.")
        raise HTTPException(status_code=400, detail="Candidate role is required.")

    if not QUESTION_ANSWERED:
        logging.error("No questions have been answered by the candidate.")
        raise HTTPException(status_code=400, detail="No answered questions available for analysis.")

    try:

        role = CANDIDATE_INFO.get("role")

        questions_answers = QUESTION_ANSWERED.copy()
        formatted_questions_and_responses = ""
        for question, response in questions_answers.items():
            formatted_questions_and_responses += f"- Question: {question}\n  Response: {response}\n\n"

        data = {
            "role": role,
            "questions_and_responses": formatted_questions_and_responses,
        }

        user_message = prompts.generate_dedicated_analysis_3["user_message"].format(**data)

        output = await llm_util.llm_genai_2(prompt=user_message, response_schema=Analysis)

        if not output:
            logging.error("No feedback returned by LLM.")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate feedback. Please try again later."
            )
        
        feedback_by_question = output.get("question_analysis")
        
        await write_to_json(output, "response_analysis_of_each_question.json")

        overall_analysis = await process_and_give_overall_feedback(output)

        if not overall_analysis:
            logging.error("No overall analysis returned by LLM.")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate overall feedback. Please try again later."
            )
        await write_to_json(overall_analysis, "overall_analysis.json")

        # Update the SQL database with the candidate information and the questions asked so far
        # TODO: Implement the database update logic here

        return feedback_by_question ,overall_analysis
    
    except Exception as e:
        logging.error(f"An error occurred while generating feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while generating feedback: {str(e)}")
    
class OverallAnalysis(BaseModel):
    overall_score: int
    overall_reasoning: str
    overall_communication_score: int
    overall_communication_reasoning: str
    overall_content_quality_score: int
    overall_content_quality_reasoning: str
    overall_domain_insight_score: int
    overall_domain_insight_reasoning: str
    technical_skills_with_score: List[str]
    soft_skills_with_score: List[str]

async def process_and_give_overall_feedback(per_question_analysis):

    try:

        question_analysis  = per_question_analysis.get("question_analysis")

        if not question_analysis or not isinstance(question_analysis, list):
            logging.error("Invalid or missing 'question_analysis' in input.")
            raise HTTPException(status_code=400, detail="'question_analysis' must be a non-empty list.")
        
        user_message = prompts.generate_overall_analysis_2["user_message"].format(question_analysis=question_analysis)
        output = await llm_util.llm_genai_2(prompt=user_message, response_schema=OverallAnalysis)

        
        # Update the SQL database with the candidate information and the questions asked so far
        # This is a placeholder for the actual database update logic
        # TODO: Implement the database update logic here
        if not output:
            logging.error("No overall analysis returned by LLM.")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate overall feedback. Please try again later."
            )
        
        await write_to_json(output, "final_result.json")
        
        logging.info("Overall feedback processed successfully.")
        return output
    
    except Exception as e:
        logging.error(f"An error occurred while processing overall feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing overall feedback: {str(e)}")