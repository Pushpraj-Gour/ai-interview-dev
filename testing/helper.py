# Project idea
"""
I am building a project that simulates a demo or mock interview experience. The process begins by receiving a user's profile details (such as a resume) via an API. Based on this information, I will use a language model to generate personalized interview questions.

The goal is to create a real-time, audio-based interview simulation where the user can participate via common platforms (e.g., Zoom, Google Meet, or any platform that allows integration). The system will:

1. Present the first question to the user.
2. Capture and transcribe the user's audio response in real-time.
3. Immediately store the response in text format.
4. Prompt the next question once the previous response is complete.
5. Continue this process until all questions are asked and answered.

After the interview, all questions and transcribed responses will be passed to a language model (LLM) for evaluation. The LLM will then generate a report assessing the user's performance and providing feedback.

Currently, I have developed the part of the system that generates questions using an API and a language model. I need guidance on how to proceed with the real-time audio interaction, including:

1. Choosing the right platform for live audio interviews.
2. Capturing and transcribing audio responses in real time.
3. Asking the next question seamlessly after each response.
4. Evaluating and generating feedback after the session.
5. The entire system will be audio-only—no video involved.

"""