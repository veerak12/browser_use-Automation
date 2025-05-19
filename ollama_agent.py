import asyncio
import os
from langchain_ollama import ChatOllama
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv

load_dotenv()

# Initialize browser
browser = Browser(
    config=BrowserConfig(
        chrome_instance_path=os.getenv("CHROME_INSTANCE_PATH"),
        headless=False,
    )
)

# Initialize Ollama LLM
llm = ChatOllama(
    model='phi4-mini:latest', #qwen2.5:latest,gemma3:4b,llama3.2:1b,phi4-mini
    #num_ctx=4096,
    num_ctx=1024
)

async def run_test_case(test_case):
    agent = Agent(
        task=test_case["title"],
        llm=llm,
        browser=browser,
        max_actions_per_step=4,
    )

    try:
        # Iterate through the steps and execute them
        for step in test_case["steps"]:
            agent.task = step  # Update the agent's task with the current step
            await agent.run(max_steps=4)  # Execute the agent for the current step

        return {"test_case": test_case["id"], "result": "Passed", "notes": ""}
    except Exception as e:
        return {"test_case": test_case["id"], "result": "Failed", "notes": str(e)}
    finally:
        await browser.close()

async def execute_test_cases(test_cases):
    results = []
    for test_case in test_cases:
        result = await run_test_case(test_case)
        results.append(result)
    return results