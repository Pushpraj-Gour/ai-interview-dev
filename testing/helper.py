# Project idea main
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

# Project idea first draft
"""
I am building a project that simulates a demo or mock interview experience. The process begins by receiving a user's profile details (such as a resume) via an API. Based on this information, I will use a language model to generate personalized interview questions.

The goal is to create a real-time, audio-based interview simulation.

1. Present the first question to the user by making an API call.
2. Now as soon as the user starts speaking, capture their audio response from a button click, which is there to start the recording and as soon as the user is done, they can stop the recording.
3. Prompt the next question once the previous response is complete.
4. Continue this process until all questions are asked and answered as there will be a button to end the interview.

After the interview, all questions and audio responses which were passed to backed the backend will make a call to language model (LLM) for evaluation. The LLM will then generate a report assessing the user's performance and providing feedback.

Currently, I have developed the part of the system that generates questions using an API and a language model. Now I am working for the next parts help me to complete the project. Next steps include:

1. Creating a front-end interface for the user to interact with.
2. Implementing real-time audio capture and send to the backend.
4. Evaluating and generating feedback after the session.

The entire system will be audio-only—no video involved.

If till now everything is clear, then I am having some node.js code which is used to generate the questions and then I will be using the same code to generate the audio questions and then send it to the backend. if you have any questions or need further clarification, feel free to ask or else I need assistance with the node.js code, to add some more functionality to it.

"""


# Project idea second draft
"""
I am building a project that simulates a demo or mock interview experience. The process begins by receiving a user's profile details (such as a resume) via an API. Based on this information, I will use a language model to generate personalized interview questions.

The goal is to create a real-time, audio-based interview simulation.

1. Present the first question to the user by making an API call.
2. Now as soon as the user starts speaking, capture their audio response from a button click, which is there to start the recording and as soon as the user is done, they can stop the recording.
3. Prompt the next question once the previous response is complete.
4. Continue this process until all questions are asked and answered as there will be a button to end the interview.

After the interview, all questions and audio responses which were passed to backed the backend will make a call to language model (LLM) for evaluation. The LLM will then generate a report assessing the user's performance and providing feedback.

Currently, I have developed the part of the system that generates questions using an API and a language model. Now I am working for the next parts help me to complete the project. Next steps include:

1. Creating a front-end interface for the user to interact with.
2. 

The entire system will be audio-only—no video involved.

If till now everything is clear, then I am having some node.js code which is used to generate the questions and then I will be using the same code to generate the audio questions and then send it to the backend. if you have any questions or need further clarification, feel free to ask or else I need assistance with the node.js code, to add some more functionality to it.


Following is the structure of the front end application:
after creating the my-react-app I just have added a file InterviewSimulator.jsx in src and added some code into it.

Now as this file is having the main code for the interview simulator. But Now I want for the front-end to have the following flow.

1. Landing page or introduction page.
2. Now there should be a option that user is an existing user or a new user.
3. If the user is a new user, then we will redirect it to another page to fill all the user details like name, email, resume, etc. and call an api to save the user details to the database by making the api call to the backend.
4. If the user is an existing user, then after taking user name and email, we will check if the user is present in the database or not, if not then we will redirect it to the new user page. or else direct it to the dashboard page
5. Dashboard page will have the option to start the interview, view previous interviews, and view the user profile. or update the user profile.
6. When the user clicks on the start interview button, we will redirect it to the InterviewSimulator page.

Now suggest how good this flow is and what changes you would suggest to make it better. Also, I need help with the code for the front-end part, so that I can implement this flow in my application.
"""

# Project idea thrid draft
"""
I am building a project that simulates a demo or mock interview experience. The process begins by receiving a user's profile details (such as a resume) via an API. Based on this information, I will use a language model to generate personalized interview questions.

The goal is to create a real-time, audio-based interview simulation.

1. Present the first question to the user by making an API call.
2. Now as soon as the user starts speaking, capture their audio response from a button click, which is there to start the recording and as soon as the user is done, they can stop the recording.
3. Once the recording is stopped, calling the backend API to pass the audio response and calling another api for next question. (We have two apis here - one for audio response and another for next question and the next question api is different from the api which we called to get the first question).
3. Prompt the next question once the previous response is complete.
4. Continue this process until all questions are asked and answered as there will be a button to end the interview.

After the interview, all questions and audio responses which were passed to backed which altough we already did when asked the next question, the backend will make a call to language model (LLM) for evaluation. The LLM will then generate a report assessing the user's performance and providing feedback.

Currently, I have developed the part of the system that generates the first question lists using an API and a language model. Now I am working for the next parts help me to complete the project. Next steps include:

1. Creating a front-end interface for the user to interact with.
2. Connection the app with sql database to store user details and all the interview responses.

The entire system will be audio-only—no video involved.

If till now everything is clear, then I am having some front-end code which is used to get the questions and pass the audio response to the backend. if you have any questions or need further clarification, feel free to ask or else I need assistance with the front-end code, to add some more functionality to it and to fix some bugs and issues which I am facing.


Following is the structure of the front end application:
After creating the my-react-app I just have added a file InterviewSimulator.jsx in src and added some code into it.

Now as this file is having the main code for the interview simulator. But Now I want for the front-end to have the following flow.

1. Landing page or Home page.
2. Now there are two option that user is an existing user or a new user.
3. If the user is a new user, then we will redirect it to another page to fill all the user details like name, email, resume, etc. and call api the backend api to save the user details to the database by making the api call to the backend.
4. If the user is an existing user, then after taking email, we will check if the user is present in the database or not which the backend will check and return the response accordingly, if not then we will redirect it to the new user page, and if it is in the database we will direct it to the dashboard page
5. Dashboard page will have the option to start the interview, view previous interviews, and view the user profile, or update the user profile.
6. When the user clicks on the start interview button, we will redirect it to the InterviewSimulator page.

Now suggest how good this flow is and what changes you would suggest to make it better. Also, I need help with the code for the front-end part, so that I can implement this flow in my application.

"""

"""

Project Overview:
The goal is to build a real-time, audio-only mock interview simulator that allows users to practice answering personalized interview questions. These questions are generated based on the user's profile (such as resume and basic information) and evaluated by a language model (LLM) for feedback.

🚀 Core Workflow:

1. User Interaction Flow (Frontend)
A. Landing Page
    Initial entry point for all users.
    Presents two options:
        New User
        Existing User

B. New User Flow
    Redirected to a registration page.
    Fills in details such as:
        Name
        Email
        role
        Skills
        Projects
        Education
        Achievements
        Experience  

    Upon submission:
    The frontend makes an API call to save the user details to the SQL database via the backend.

C. Existing User Flow

    Enters their email.
    An API call checks if the user exists in the database.
    If the user exists, redirect to the Dashboard.
    If the user does not exist, redirect to the New User page to complete profile setup.

D. Dashboard Page
    Provides the following user options:
        ✅ Start Interview
        📁 View Previous Interviews
        👤 View or Update Profile

Clicking Start Interview redirects to the InterviewSimulator page to begin the real-time simulation.

2. Interview Simulation Flow
    A. Start Interview
    The system initiates the interview by making an API call to get the first personalized question, using the user's resume/profile.

    B. Question-Answer Loop
        The user hears the question.
        A “Start Recording” button allows the user to begin speaking.
        Once finished, the user clicks “Stop Recording”.

The audio file is:

Sent to the backend via an API along with corresponding question.
A separate API call fetches the next interview question.
This process continues until all questions are asked and answered.

C. Interview Termination
    The user can end the interview at any time using an “End Interview” button.

    If the user refreshes the page, the interview will end immediately (no session restoration or auto-resume).

3. Post-Interview Evaluation
    Once the interview is complete:

    All the collected audio responses and questions are passed to the backend.

    The backend invokes a language model (LLM) to evaluate the answers.

    The LLM returns:

    A detailed performance report

    Feedback and suggestions for improvement, stored and optionally displayed to the user.

"""

# Prompt for feedback generation

"""
Objective:
Design a reusable prompt that simulates the evaluation process of a live interview response for a specific role or domain provided at runtime. The goal is to mimic a real interview scenario where an interviewer poses a question, the candidate responds, and an expert (AI) evaluates the response critically and professionally.

# Prompt Functionality Requirements

## The prompt should:

### Input:
  - A specific interview question.
  - The candidate's actual response.
  - The role or domain the interview is for (e.g., Software Engineer, Product Manager, Data Analyst).

## Output:

### Comprehensive Analysis of the candidate's response, including:

  - Strengths.
  - Weaknesses.
  - Gaps or missing elements.
  - Overall effectiveness in the context of the role.

## Suggestions for Improvement, clearly outlining:

  - What could be done better.
  - How the answer can be made more aligned with expectations for the role.

## Evaluation Parameters Used, such as (but not limited to):

  - Relevance and completeness of the answer.
  - Clarity and communication.
  - Depth of domain knowledge.
  - Logical structure and flow.
  - Use of real-world examples.
  - Role alignment and professional tone.

## Ideal Model Answer:

  - A well-structured, role-specific ideal response to the given question.
  - Should serve as a benchmark for comparison.
"""

"""
Task:
Create a prompt that simulates the evaluation of a live interview scenario. The prompt should accept:

1. An interview question.
2. The candidate's response.
3. The specific role or domain (e.g., Software Engineering, Product Management, Data Science, etc.).

Based on this input, the language model should:

1. Perform a deep and thoughtful analysis of the candidate's response.
2. Offer insights into how well the candidate answered the question.
3. Identify what was strong and what could be improved.
4. Reflect on the overall effectiveness of the answer.
5. Provide an ideal or model answer to the same question for comparison.
The evaluation criteria and analytical approach should be internally decided by the model based on the context and role provided. The tone should mimic that of a real interview assessment.
"""