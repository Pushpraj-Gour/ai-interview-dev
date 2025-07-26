from typing import List
from pydantic import BaseModel


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
{candidate_name}
</candidate_name>

2. Job Role:
<job_role>
{role}
</job_role>

3. Candidate Skills:
<skills_list>
{skills}
</skills_list>

4. List of Major Questions:
<major_questions_list>
{major_questions}
</major_questions_list>

5. Questions Already Asked:
<asked_questions_list>
{questions_asked}
</asked_questions_list>

6. Most Recent Question Asked along with the Candidate's Response:
<last_question_along_with_response>

Question: {last_question}
Candidate's Response: {response}
<>last_question_along_with_response>

Based on all the above:

a. Analyze the most recent response to see if a follow-up or deeper question can be formed to explore the candidate's understanding or experience more interactively.

b. If a meaningful follow-up is possible, generate a contextual follow-up question.

c. If not, select a relevant question from the list of unasked major questions that aligns well with the candidate's profile and keeps the interview engaging.

"""}

generate_question_based_on_response_3 = {
    "user_message": """
You are acting as a realistic interviewer in a mock interview setting. 
Your goal is to:
- Cover as many of the candidate's listed skills as possible.
- Make the interview feel natural and conversational.
- Occasionally ask follow-up questions for depth when it makes sense.

### Candidate Name:
<candidate_name>
{candidate_name}
</candidate_name>

### Job Role:
<job_role>
{role}
</job_role>

### Candidate Skills:
<skills_list>
{skills}
</skills_list>

### List of Major Questions:
<major_questions_list>
{major_questions}
</major_questions_list>

### Questions Already Asked:
<asked_questions_list>
{questions_asked}
</asked_questions_list>

### Most Recent Question Asked along with the Candidate's Response:
<last_question_along_with_response>
Question: {last_question}
Candidate's Response: {response}
</last_question_along_with_response>

### Instructions:
1. Decide if a follow-up question is needed:
   - Ask a follow-up ONLY IF:
     - The answer is brief or lacks depth (less than 50 words or surface-level).
     - The answer mentions a key skill from the profile worth exploring further.
     - The answer includes something unique or interesting (special project, uncommon tool).
     - The answer hints at decision-making, leadership, or problem-solving worth elaborating on.
   - Do NOT ask follow-up if:
     - The response is already detailed and covers reasoning, challenges, and outcomes.
     - The topic is low priority compared to other skills to cover.

2. If a follow-up is needed:
   - Generate ONE relevant, natural follow-up question.
   - Make it specific to what the candidate mentioned.
   - Keep it conversational, like a real interviewer would ask.


"""}

# class DetailedAnalysisResponse(BaseModel):
#     clarity_score: int
#     clarity_reasoning: str
#     depth_score: int
#     depth_reasoning: str
#     relevance_score: int
#     relevance_reasoning: str
#     engagement_score: int
#     engagement_reasoning: str
#     confidence_score: int
#     confidence_reasoning: str
#     overall_impression_score: int
#     overall_impression_reasoning: str
#     areas_for_improvement: list[str]
#     strengths: list[str]
#     weaknesses: list[str]
#     suggestions_for_improvement: list[str]
#     idea_answer: str


# class Analysis(BaseModel):
#     question: str
#     overall_marks: int
#     overall_reasoning: str
#     question_and_response_detailed_analysis: DetailedAnalysisResponse

generate_dedicated_analysis = {
    "user_message": """
You are an AI assistant tasked with analyzing a candidate's interview performance based on their responses to questions.

Following are the questions along with the candidate's responses:
<questons_and_responses>
{questions_and_responses}
</questons_and_responses>

Your task is to provide a detailed analysis of the candidate's performance, focusing on the following aspects for each question:

1. **Clarity**: How clear and understandable was the candidate's response?
2. **Depth**: Did the candidate provide sufficient detail and depth in their answers?
3. **Relevance**: How relevant was the response to the question asked?
4. **Engagement**: Did the candidate engage with the question in a meaningful way?
5. **Confidence**: Did the candidate demonstrate confidence in their responses?
6. **Overall Impression**: What is your overall impression of the candidate's performance based on their responses?
7. **Areas for Improvement**: Identify specific areas where the candidate could improve their responses in future interviews.

For each question, provide a concise analysis that addresses the above aspects. And for each question, also provide a score from 0 to 10, where 0 is the lowest and 10 is the highest, based on the overall performance of the candidate in that response. And the reaasoning behind the score.

For each response, provide what are the areas where the candidate performed well and what are the areas where the candidate needs to improve. For each response:

1. **Strengths**: Highlight the strengths of the candidate's response.
2. **Weaknesses**: Identify any weaknesses or areas for improvement in the response.
3. **Suggestions**: Provide specific suggestions for how the candidate could improve their response in future interviews.

Provide each question's answer suggest what ideally the candidate should have answered.

"""
}


class DetailedAnalysisResponse(BaseModel):
    communication_score: int
    communication_reasoning: str
    content_quality_score: int
    content_quality_reasoning: str
    domain_insight_score: int
    domain_insight_reasoning: str
    strategic_depth_score: int
    strategic_depth_reasoning: str
    professional_tone_score: int
    professional_tone_reasoning: str
    ideal_answer: str

class Analysis(BaseModel):
    question: str
    overall_score: int
    overall_reasoning: str
    question_and_response_detailed_analysis: DetailedAnalysisResponse

generate_dedicated_analysis_3 = {
    "user_message": """
You are simulating a senior interviewer evaluating a candidate's performance in a live interview for the role of **{role}**. Based on the interview question and candidate response provided, deliver a critical yet constructive analysis that reflects real-world hiring standards for the role.

### INPUT

- Role/Domain: `{role}`
- A list of questions and responses from the candidate: `{questions_and_responses}`

### OUTPUT

#### Evaluation Summary

Assess the candidate's response using the following parameters:

- **Relevance & Completeness**: Does the answer fully address the question and stay focused on key points?
- **Clarity & Communication**: Is the response clear, concise, and easy to understand?
- **Depth of Knowledge**: Does the answer demonstrate strong domain expertise or strategic understanding?
- **Logical Structure & Flow**: Is the response well-organized, with coherent flow and logical sequencing?
- **Role Alignment & Tone**: Does the tone and content reflect the expectations and seniority of the given role?

Provide a **numerical score in range of 0-10**, along with a **brief justification** for the score.

#### Strengths

Highlight what the candidate did well in their response, with specific references to:

- Communication
- Content quality
- Domain insight
- Strategic or technical depth
- Professional tone or examples used

#### Areas for Improvement

Identify shortcomings or missed opportunities, such as:

- Gaps in explanation or logic
- Missing examples or lack of specificity
- Technical or strategic misunderstandings
- Unstructured or vague language

#### Suggestions

Provide **actionable, role-specific advice** to improve future answers. Include suggestions on:

- Structuring answers
- Including metrics, examples, or frameworks
- Adjusting tone for seniority
- Deepening technical or business relevance

#### Ideal Model Answer (Benchmark)

Craft a **high-quality, well-structured answer** to the same question, tailored to the expectations of the **{role}**. This model answer should:

- Fully address the question with depth and clarity
- Include relevant terminology or frameworks
- Show domain expertise
- Use real-world examples or metrics (where applicable)
- Reflect a confident, professional tone
"""
}

generate_overall_analysis = {
    "user_message": """
You are an AI assistant assigned to provide a comprehensive analysis of a candidate's interview performance based on their responses to multiple questions.

Following are the analysis of the candidate's responses for each question your task is to provide an overall analysis of the candidate's performance based on the individual question analyses. Like how good he is overall in the interview, what are the areas where he is good, and what are the areas where he needs to improve, and what are the suggestions for improvement. 

<question_analysis>
{question_analysis}
</question_analysis>

Score it overall in the range of 0-10 and provide the reasoning behind the score for the following aspects:
- Overall Communication
- Overall Content Quality
- Overall Domain Insight

Score it overall in the range of 0-10 based on everthing and provide the reasoning behind the score for the following aspects, generate an overall score in the range of 0-10 and give score to the overall communication, content quality, domain insight, strategic depth, and professional tone. Also provide the reasoning behind the score. 

List all the Technical Skills and Soft Skills that the candidate has based on the questions asked and the responses given by the candidate on the skills that the questions are based on. and rate candidate on the scale of 0-10 for each skill based on the responses given by the candidate on the skills that the questions are based on.  

"""
}



generate_overall_analysis_2 = {
    "user_message": """
You are an AI assistant responsible for generating a **thorough overall analysis** of a candidate's interview performance. The candidate has answered multiple interview questions, and for each question, a detailed evaluation has already been provided.

### **Input**

Given a questions with analysed response containing a list of question-level evaluations, each with detailed scores and reasoning.
<question_analysis>
{question_analysis}
</question_analysis>

You are **not** responsible for evaluating the individual responses—that has already been done. Your role is to **aggregate and analyze the overall performance**.

- An **overall score** and reasoning for that specific question.
- Understand the evaluation of individual scores and reasoning across:
  - Communication
  - Content Quality
  - Domain Insight
  - Strategic Depth
  - Professional Tone

Your task is to synthesize these individual evaluations into a **comprehensive overall performance report**.

### **Your Deliverables**

#### 1. **Overall Summary Analysis**

Write a clear and concise summary of the candidate's interview performance covering:

- **Overall performance quality** (Was it good, average, poor).
- **Strength areas** - where the candidate performed well across questions (e.g., communication, ML understanding, tooling knowledge, etc.).
- **Improvement areas** - where the candidate consistently underperformed or showed gaps.
- **Actionable suggestions** - how the candidate can improve in their weak areas (e.g., studying SQL basics, practicing delivery, deepening domain knowledge).

#### 2. **Overall Scores (0-10)**

Provide overall scores (with reasoning) for the following aspects **across all questions**:

- **Overall Communication**
- **Overall Content Quality**
- **Overall Domain Insight**

#### 3. **Skill Evaluation**

From the responses and evaluations, extract all **Technical Skills** and **Soft Skills** the candidate demonstrated.

For each skill:
- Mention whether it's a **Technical** or **Soft Skill**.
- Assign a **score (0-10)** based on how well the candidate demonstrated this skill during the interview.
- Focus only on skills that were tested in the questions (e.g., SQL, Python, ML pipelines, communication, etc.).

"""
}
