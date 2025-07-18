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

async def write_to_json(data, file_name):
	current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	filepath = Path(keys.directory).joinpath(current_time)
	os.makedirs(filepath, exist_ok=True)
	
	filepath_with_name = Path(filepath).joinpath(file_name)
	
	with open(filepath_with_name, 'w', encoding='utf-8') as f:
		json.dump(data, f, indent=4, default=str)
		print(f"Wrote {file_name} at {filepath_with_name}")

async def initial_questions(candidate_info: dict):

	data = {
		"candidate_name": candidate_info.get("candidate_name"),
		"role": candidate_info.get("role"),
		"skills": candidate_info.get("skills"),
		"education": candidate_info.get("education"),
	}
	
	user_message = prompts.generate_basic_user_message["user_message"].format(**data)
	output = await llm_util.llm_genai(user_message)

	await write_to_json(output, "first_draft.json")
	
	return output

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

async def process_audio_response_2(audio_file: bytes):

	elevenlabs = ElevenLabs(
	api_key=keys.elevenlabs_api_key,
	)

	if not audio_file:
		raise ValueError("Uploaded audio file is empty.")
	

	audio_data = BytesIO(audio_file)

	# Reset pointer
	audio_data.seek(0)

	response = elevenlabs.speech_to_text.convert(
		file=audio_data,
		model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
		tag_audio_events=True, # Tag audio events like laughter, applause, etc.
		language_code="eng", # Language of the audio file. If set to None, the model will detect the language automatically.
		diarize=True, # Whether to annotate who is speaking
	)

	transcription = {
		"transcription": response.text,
		"transcription_response": response,
		"timestamp": datetime.now().isoformat(),
	}

	await write_to_json(transcription, f"transcription_{uuid.uuid4().hex}.json")

	return response.text

async def main(filename: str):

	result = await process_audio_response(filename)
	print(result)

if __name__ == "__main__":
	audio_file = r"C:\Users\rajr1\Desktop\projects\files\llm_interviewer\responses_audio\question_When_would_you_choose_Matplotlib_2025-07-17_09-28-06.wav"  # Replace with your audio file path
	asyncio.run(main(audio_file))
