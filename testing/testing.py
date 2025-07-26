
import requests
import json
import requests
import json
import asyncio
# from app.config import keys

import requests
import json
from functions.interview_questions import *

# response = requests.post(
#   url="https://openrouter.ai/api/v1/chat/completions",
#   headers={
#     "Authorization": f"Bearer {key.open_router_key}",
#     "Content-Type": "application/json",
#   },
#   data=json.dumps({
#     "model": "google/gemini-2.0-pro-exp-02-05:free",
#     "messages": [
#       {
#         "role": "user",
#         "content": [
#           {
#             "type": "text",
#             "text": "Generate some basic begginer level interview questions which can be asked for AI engineer role."
#           },
#           {
#             "type": "image_url",
#             "image_url": {
#               "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
#             }
#           }
#         ]
#       }
#     ],
    
#   })
# )
# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the JSON response
#     result = response.json()
#     print(json.dumps(result, indent=4))  # Pretty print the JSON result
# else:
#     print(f"Error: {response.status_code} - {response.text}")


# response = requests.post(
#   url="https://openrouter.ai/api/v1/chat/completions",
#   headers={
#     "Authorization": f"Bearer {keys.open_router_key}",
#     "Content-Type": "application/json",
#   },
#   data=json.dumps({
#     "model": "qwen/qwq-32b:free",
#     "messages": [
#       {
#         "role": "user",
#         "content": "What is the meaning of life?"
#       }
#     ],
    
#   })
# )
# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the JSON response
#     result = response.json()
#     print(json.dumps(result, indent=4))  # Pretty print the JSON result
# else:
#     print(f"Error: {response.status_code} - {response.text}")

async def test():
    print('------')
    print("Testing function")
    print('------')



async def h1():
  await process_and_give_overall_feedback()

if __name__ == "__main__":
    # asyncio.run(test())
  audio_file = r"C:\Users\rajr1\Desktop\projects\files\llm_interviewer\responses_audio\question_When_would_you_choose_Matplotlib_2025-07-17_09-28-06.wav"  # Replace with your audio file path
  asyncio.run(h1())
