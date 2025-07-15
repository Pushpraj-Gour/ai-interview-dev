import asyncio
import json
from app.utils import llm_util
from app.config import model
from app.config import keys
from functions import prompts
from pathlib import Path
from datetime import datetime
import os


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
