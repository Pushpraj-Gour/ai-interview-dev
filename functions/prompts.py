# Project detailed Idea

# 1. After getting all the required info of the candidate. --> (Through front end, and backend)
# 2. Prompt_1. It will take all the details of the candidate and generate a list of interview questions. along with some basic Introductory questions which can easy the candidate, not directly jumping to the job related questions, at most 2,3 questions.
# 3.

generate_basic_user_message = {
    "user_message": """
Generate a list of interview questions for a candidate based on their profile.

                               
Candidate_details:

1. Candidate Name:
<candidate_name>
{candidate_name}
</candidate_name>

2. Job Role:
<role>
{role}
<role>

3. Candidate Skills:
<skills>
{skills}
</skills>

Instructions for Generating Questions:
  a. The questions must be directly related to the job role and skills mentioned in the candidate's profile.
  b. Ensure that each question is short, clear, and easy to understand.
  c. Start with basic questions and gradually increase the difficulty level as the list progresses.
  d. Tailor the questions to the specific job responsibilities and expertise required for the role, using the skills mentioned by the candidate.
"""}


generate_question_based_on_response = {
    "user_message": """
For the following candidate details and their response to the given question, generate the next interview question.

Candidate_details:

1. Candidate name:
<candidate_name>
{candidate_name}
</candidate_name>

2. Job role:
<role>
{role}
<role>

3. Candidate skills:
<skills>
{skills}
</skills>

4. Candidate question asked so far:
<questions_asked>
{questions_asked}
</questions_asked>

5. Candidate Response to the Last Question along with question:
<last_question_along_with_response>
{last_question_along_with_response}
</last_question_along_with_response>


6. Major questions not asked so far:
<major_questions>
{major_questions}
</major_questions>


Instructions for Generating Next Question:
  a. The questions must be directly related to the job role and skills mentioned in the candidate's profile.
  b. Ensure that each question is short, clear, and easy to understand.
  c. Generate the next question based on the last question and the candidate's response, if the response is having something from which we can ask the next question to make the interview more interactive, and somewhat it is related to the major_quesitons or candidate's profile create it.
  d. If the candidate's response is not sufficient to generate a new question, select a question from the major questions that have not been asked yet.
"""}


generate_question_based_on_response_2 = {
    "user_message": """
You are assisting in a live job interview. You have the following information:

1. Candidate Name:
<candidate_name>
{{candidate_name}}
</candidate_name>

2. Job Role:
<job_role>
{{job_role}}
</job_role>

3. Candidate Skills:
<skills_list>
{{skills_list}}
</skills_list>

4. List of Major Questions:
<major_questions_list>
{{major_questions_list}}
</major_questions_list>

5. Questions Already Asked:
<asked_questions_list>
{{asked_questions_list}}
</asked_questions_list>

6. Most Recent Question Asked along with the Candidate's Response:
<last_question_along_with_response>
{{last_question_along_with_response}}
<>last_question_along_with_response>

Based on all the above:

a. Analyze the most recent response to see if a follow-up or deeper question can be formed to explore the candidate's understanding or experience more interactively.

b. If a meaningful follow-up is possible, generate a contextual follow-up question.

c. If not, select a relevant question from the list of unasked major questions that aligns well with the candidate's profile and keeps the interview engaging.

"""}