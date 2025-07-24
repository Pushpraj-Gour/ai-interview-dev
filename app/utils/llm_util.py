import requests
import json
from app.config import keys
from fastapi import HTTPException
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import Any, List
import sys
import openai
from pydantic import BaseModel, RootModel, ValidationError
from google import genai

class Questions(BaseModel):
	candidate_name: str
	questions: List[str]

async def llm_openrouter(prompt):

	openrouter_client = openai.AsyncOpenAI(
	api_key=keys.open_router_key,
	base_url="https://openrouter.ai/api/v1",
	)
	response = await openrouter_client.chat.completions.create(
	model="google/gemma-3n-e4b-it:free",
	messages=[
		{
		"role": "user",
		"content": prompt

		}
	]
	)
	return response.choices[0].message.content


async def llm_openrouter_2(prompt):

	openrouter_client = openai.AsyncOpenAI(
	api_key=keys.open_router_key,
	base_url="https://openrouter.ai/api/v1",
	)

	params = {
		"model": "qwen/qwen3-30b-a3b:free",
		"messages": [
			{
				"role": "user",
				"content": prompt
			}
		]
	}
	response = await openrouter_client.chat.completions.create(**params)
	return response.choices[0].message.content

async def llm_genai(prompt):

	client = genai.Client(api_key=keys.genai_api_key)

	response = client.models.generate_content(
		model="gemini-2.5-flash",
		contents=prompt,
		config={
        "response_mime_type": "application/json",
        "response_schema": Questions,
    },
	)

	if response and response.text is not None:
		response_raw = response.text
		formmated_response = json.loads(response_raw)
	else:
		formmated_response = None

	return formmated_response
from typing import Optional, Type
from typing import cast
from google.genai.types import GenerateContentConfigDict

async def llm_genai_2(prompt, response_schema: Optional[Type[BaseModel]] = None):

	client = genai.Client(api_key=keys.genai_api_key)

	config: GenerateContentConfigDict = {"response_mime_type": "application/json"}
	if response_schema:
		config["response_schema"] = response_schema 
	response = client.models.generate_content(
		model="gemini-2.5-flash",
		contents=prompt,
		config=config,
	)

	if response and response.text is not None:
		response_raw = response.text
		formmated_response = json.loads(response_raw)
	else:
		formmated_response = None

	return formmated_response

import requests

async def llm_perplexity(prompt: str) -> Any:

	response = requests.post(
		'https://api.perplexity.ai/chat/completions',
		headers={
			'Authorization': f'Bearer {keys.perplexity_api_key}',
			'Content-Type': 'application/json'
		},
		json={
			'model': 'sonar',
			'messages': [
				{
					'role': 'user',
					'content': prompt
				}
			],
			'response_format': {
				'type': 'json_schema',
				'json_schema': {
					'schema': Questions.model_json_schema()
				}
			}
		}
	)

	return response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No content found')

# from typing import Optional, Type
# from pydantic import BaseModel
# import json

# async def llm_genai(prompt: str, response_format: Optional[Type[BaseModel]] = None):
#     client = genai.Client(api_key=keys.genai_api_key)

#     config = {"response_mime_type": "application/json"}
#     if response_format:
#         config["response_schema"] = response_format  # ✅ Pass schema dynamically

#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt,
#         config=config,
#     )

#     if response and response.text is not None:
#         response_raw = response.text
#         try:
#             formatted_response = json.loads(response_raw)
#         except json.JSONDecodeError:
#             formatted_response = None
#     else:
#         formatted_response = None

#     return formatted_response
