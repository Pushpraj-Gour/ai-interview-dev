import requests
import json
from app.config import keys
from fastapi import HTTPException
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import Any, List
import sys
import openai

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

from google import genai

async def llm_genai(prompt):

	client = genai.Client(api_key="AIzaSyAGaSSUKGMBPrQuMsWrlLlycJ6B6rWJqCA")

	response = client.models.generate_content(
		model="gemini-2.5-flash",
		# model="google/gemma-3n-e4b-it:free",
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
