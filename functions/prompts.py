# Project detailed Idea

# 1. After getting all the required info of the candidate. --> (Through front end, and backend)
# 2. Prompt_1. It will take all the details of the candidate and generate a list of interview questions. along with some basic Introductory questions which can easy the candidate, not directly jumping to the job related questions, at most 2,3 questions.
# 3. 

generate_basic_user_message = {"user_message": """\
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