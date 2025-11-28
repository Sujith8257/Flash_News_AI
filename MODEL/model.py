import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY missing. Add it to a .env file or the environment."
    )

shared_llm = LLM(
    model="gemini-2.0-flash",  # Using Gemini 2.0 Flash model
    api_key=gemini_api_key,
    temperature=0.7,
    timeout=120,
    max_tokens=4000,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
)

# Define three agents with distinct responsibilities
news_researcher = Agent(
    role="Global Events Research Analyst",
    goal="Gather the most significant recent events around the world and rank them by their global importance and impact. Then select the top five events and research each thoroughly using trusted international news sources. Include only original images related to the events from credible sources (no AI-generated images).",
    backstory="You are a professional, precise global news analyst with deep expertise in current affairs. You systematically identify and evaluate worldwide events by their significance and impact, then compile detailed, authoritative reports on the top stories. You source all information and images from reliable international outlets, ensuring included images are original and relevant. Your tone is expert, objective, and well-informed.",
    llm=shared_llm
)

fact_checker = Agent(
    role="Fact Checker",
    goal="Verify accuracy of claims and flag inconsistencies",
    backstory="Thorough reviewer who cross-checks every statement.",
    llm=shared_llm,
)

copywriter = Agent(
    role="Copywriter",
    goal="Produce a short Flash News brief in a lively tone",
    backstory="Seasoned writer specializing in concise news summaries.",
    llm=shared_llm,
)

# Tasks each agent should perform
research_task = Task(
    description="List 3–5 major AI news items with source URLs.",
    expected_output="Bullet list of 3–5 AI headlines with one-sentence summaries and source URLs.",
    agent=news_researcher
)

validate_task = Task(
    description="Confirm each news item is accurate; mark any uncertainty.",
    expected_output="Table or list showing each headline with a status of VERIFIED/FLAGGED and any notes.",
    agent=fact_checker
)

write_task = Task(
    description="Draft a 150-word Flash News article combining the verified items.",
    expected_output="One cohesive ~150-word Flash News article written in an energetic tone.",
    agent=copywriter,
    async_execution=False  # ensure it runs after validation completes
)

# Assemble the crew and execute
crew = Crew(
    agents=[news_researcher, fact_checker, copywriter],
    tasks=[research_task, validate_task, write_task],
)

result = crew.kickoff()
print(result)
