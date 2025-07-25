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
from typing import List, Literal, Optional
from pydantic import BaseModel, RootModel, ValidationError

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


async def initial_questions(candidate_info: dict):

    CANDIDATE_INFO.update(candidate_info)

    class Questions(BaseModel):
        questions: List[str]

    data = {
        "candidate_name": candidate_info.get("name"),
        "role": candidate_info.get("role"),
        "skills": candidate_info.get("skills"),
        "education": candidate_info.get("education"),
    }
    
    try:
        user_message = prompts.generate_basic_user_message["user_message"].format(**data)
        output = await llm_util.llm_genai_2(prompt=user_message, response_schema=Questions)
        

        await write_to_json(output, "first_draft.json")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred while generating initial questions: {str(e)}")

    if not output:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate initial questions. Please try again later."
        )
    
    MAJOR_QUESTIONS.extend(output.get("questions", []))	
    
    question_to_ask = MAJOR_QUESTIONS.pop(0)
    QUESTION_ASKED.append(question_to_ask)
    global LAST_QUESTION_ASKED
    LAST_QUESTION_ASKED = question_to_ask

    return question_to_ask

# This function is to process the audio response which we are getting from the frontend, the idea is to convert audio to text.
async def process_audio_response(audio_file: str):

    elevenlabs = ElevenLabs(
    api_key=keys.elevenlabs_api_key,
    )

    with open(audio_file, 'rb') as audio:
        audio_data = BytesIO(audio.read())

    response = elevenlabs.speech_to_text.convert(
        file=audio_data,
        model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
        tag_audio_events=True, # Tag audio events like laughter, applause, etc.
        language_code="eng", # Language of the audio file. If set to None, the model will detect the language automatically.
        diarize=True, # Whether to annotate who is speaking
    )

    transcription = {
        "transcription": response.text,
        "audio_file": audio_file,
        "transcription_response": response,
        "timestamp": datetime.now().isoformat(),
    }

    await write_to_json(transcription, "transcription.json")

    return response.text

async def process_audio_response_2(question:str, audio_file: bytes):

    elevenlabs = ElevenLabs(
    api_key=keys.elevenlabs_api_key,
    )

    if not audio_file:
        raise ValueError("Uploaded audio file is empty.")
    

    audio_data = BytesIO(audio_file)

    # Reset pointer
    audio_data.seek(0)

    try:
        if not audio_data:
            raise ValueError("Audio data is empty or invalid.")
        response = elevenlabs.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
            tag_audio_events=True, # Tag audio events like laughter, applause, etc.
            language_code="eng", # Language of the audio file. If set to None, the model will detect the language automatically.
            diarize=True, # Whether to annotate who is speaking
        )
    except Exception as e:
        raise ValueError(f"An error occurred while processing the audio file: {str(e)}")
    
    if not response or not response.text:
        raise ValueError("Failed to transcribe the audio file. Please ensure the audio is clear and try again.")

    transcription = {
        "transcription": response.text,
        "transcription_response": response,
        "timestamp": datetime.now().isoformat(),
    }

    QUESTION_ANSWERED[LAST_QUESTION_ASKED] = response.text

    await write_to_json(transcription, f"transcription_{uuid.uuid4().hex}.json")

    return response.text

async def process_audio_response_3(question: str, response: str):

    QUESTION_ANSWERED[question] = response

    return response

async def next_question():

    global LAST_QUESTION_ASKED_IS_FOLLOW_UP
    global LAST_QUESTION_ASKED

    if LAST_QUESTION_ASKED_IS_FOLLOW_UP:
        # If the last question was a follow-up, we will not ask a follow-up question again
        LAST_QUESTION_ASKED_IS_FOLLOW_UP = False
        if not MAJOR_QUESTIONS:
            raise HTTPException(status_code=404, detail="No more questions available.")
        question_to_ask = MAJOR_QUESTIONS.pop(0)
        QUESTION_ASKED.append(question_to_ask)
        LAST_QUESTION_ASKED = question_to_ask

        return question_to_ask

    if not CANDIDATE_INFO:
        raise HTTPException(status_code=400, detail="Candidate information is not provided.")
    
    candidate_info = CANDIDATE_INFO.copy()

    data = {
        "candidate_name": candidate_info.get("name"),
        "role": candidate_info.get("role"),
        "skills": candidate_info.get("skills")
    }

    if not MAJOR_QUESTIONS:
        raise HTTPException(status_code=404, detail="No more Initial questions available.")
    
    data["major_questions"] = MAJOR_QUESTIONS
    data["questions_asked"] = QUESTION_ASKED
    data["last_question"] = LAST_QUESTION_ASKED
    data["response"] = QUESTION_ANSWERED[LAST_QUESTION_ASKED]


    user_message = prompts.generate_question_based_on_response_3["user_message"].format(**data)

    class QuestionSuggestion(BaseModel):
        decision: Literal["follow_up", "major_question"]
        reasoning: str  # Why this choice was made
        follow_up_question: Optional[str]  # Populated if decision == "follow_up"
        major_question_selected: Optional[str]  # Populated if decision == "major_question"

    with open("user_message.json", "w") as f:
        json.dump(user_message, f, indent=4)
    
    output = await llm_util.llm_genai_2(user_message, response_schema=QuestionSuggestion)

    if not output or "error" in output:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate the next question. Please try again later."
        )
    
    # Check if the output contains a question or not:
    # If it does not contain a question, we will select a question from the major questions that have not been asked yet and update the things like last question and asked question and remove that question from major question else update the question 

    with open("output.json", "w") as f:
        json.dump(output, f, indent=4)

    try:
        if output.get("decision") == "follow_up":
            follow_up_question = output.get("follow_up_question")
            if not follow_up_question:
                raise HTTPException(status_code=400, detail="Follow-up question is not provided.")
            
            QUESTION_ASKED.append(follow_up_question)
            LAST_QUESTION_ASKED = follow_up_question
            LAST_QUESTION_ASKED_IS_FOLLOW_UP = True
            return follow_up_question
        
        elif output.get("decision") == "major_question":
            major_question_selected = output.get("major_question_selected")
            if not major_question_selected:
                raise HTTPException(status_code=400, detail="Major question is not provided.")
            
            if major_question_selected not in MAJOR_QUESTIONS:
                raise HTTPException(status_code=400, detail="Selected major question has already been asked or does not exist.")
            
            QUESTION_ASKED.append(major_question_selected)
            MAJOR_QUESTIONS.remove(major_question_selected)
            LAST_QUESTION_ASKED = major_question_selected
            return major_question_selected
        
    # If anything goes wrong, we will select a question from the major questions that have not been asked yet
    except Exception as e:
        print(f"Error processing output: {str(e)}")
        if not MAJOR_QUESTIONS:
            raise HTTPException(status_code=404, detail="No more major questions available.")
        
        question_to_ask = MAJOR_QUESTIONS.pop(0)
        QUESTION_ASKED.append(question_to_ask)
        LAST_QUESTION_ASKED = question_to_ask
        return question_to_ask
    
async def process_feedback_for_each_response():
    # Save all the information we have gathered so far in a json file, all the questions asked, the responses, the candidate information, etc. Along with it we will update the sql database with the candidate information and the questions asked so far.


    with open("output.json", "r", encoding='utf-8') as f:
        details = json.load(f)

    questions_answers = details.get("question_answered")
    role = details.get("candidate_info").get("role")
    formatted_questions_and_responses = ""
    for question, response in questions_answers.items(): # TODO: Update this to use the actual questions and responses
        formatted_questions_and_responses += f"- Question: {question}\n  Response: {response}\n\n"

    data = {
        "role": role, #TODO: Update this to use the actual role
        "questions_and_responses": formatted_questions_and_responses,
    }

    class DetailedAnalysisResponse(BaseModel):
        communication_score: int
        # communication_reasoning: str
        content_quality_score: int
        # content_quality_reasoning: str
        domain_insight_score: int
        # domain_insight_reasoning: str
        strategic_depth_score: int
        # strategic_depth_reasoning: str
        professional_tone_score: int
        # professional_tone_reasoning: str
        ideal_answer: str

    class DedicatedAnalysis(BaseModel):
        question: str
        overall_score: int
        overall_reasoning: str
        question_and_response_detailed_analysis: List[DetailedAnalysisResponse]

    class Analysis(BaseModel):
        overall_analysis: str
        question_analysis: List[DedicatedAnalysis]


    user_message = prompts.generate_dedicated_analysis_3["user_message"].format(**data)

    output = await llm_util.llm_genai_2(prompt=user_message, response_schema=Analysis)
    
    await write_to_json(output, "response_analysis.json")
    # Update the SQL database with the candidate information and the questions asked so far
    # This is a placeholder for the actual database update logic
    # TODO: Implement the database update logic here

    return output
    
async def process_and_give_overall_feedback():
    # Save all the information we have gathered so far in a json file, all the questions asked, the responses, the candidate information, etc. Along with it we will update the sql database with the candidate information and the questions asked so far.
    data = {
        "candidate_info": CANDIDATE_INFO,
        "major_questions": MAJOR_QUESTIONS,
        "questions_asked": QUESTION_ASKED,
        "question_answered": QUESTION_ANSWERED,
    }

    
    await write_to_json(data, "processed_result.json")
    # Update the SQL database with the candidate information and the questions asked so far
    # This is a placeholder for the actual database update logic
    # TODO: Implement the database update logic here

async def main(filename: str):

    result = await process_audio_response(filename)
    print(result)

if __name__ == "__main__":
    audio_file = r"C:\Users\rajr1\Desktop\projects\files\llm_interviewer\responses_audio\question_When_would_you_choose_Matplotlib_2025-07-17_09-28-06.wav"  # Replace with your audio file path
    asyncio.run(main(audio_file))
