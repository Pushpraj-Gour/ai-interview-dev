import requests
import json
from config import key

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {key.open_router_key}",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "meta-llama/llama-3.1-8b-instruct",
    "messages": [
      {
        "role": "user",
        "content": "Write a very very long story. The story should be about a Boy struggling to get a job in the AI field. He has done his Bachelors in Computer Science and has some experience in Python, C, SQL, TensorFlow, OpenCV, PyTorch, FastAPI, Keras, Scikit-Learn, streamlit, Seaborn, NumPy, Pandas, Matplotlib. The story should be engaging and inspiring."
      }
    ],
    
  })
)
if response.status_code == 200:
    # Parse the JSON response
    result = response.json()
    print(json.dumps(result, indent=4))  # Pretty print the JSON result
else:
    print(f"Error: {response.status_code} - {response.text}")