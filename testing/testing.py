import requests
import json
from config import key

import requests
import json

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


import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {key.open_router_key}",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "qwen/qwq-32b:free",
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ],
    
  })
)
# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    result = response.json()
    print(json.dumps(result, indent=4))  # Pretty print the JSON result
else:
    print(f"Error: {response.status_code} - {response.text}")
