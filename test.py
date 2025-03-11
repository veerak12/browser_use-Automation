import asyncio
import os
import yaml
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from browser_use import Agent, BrowserConfig
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContextConfig

# Load environment variables
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError('GEMINI_API_KEY is not set')

# Initialize LLM with Gemini
llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', api_key=SecretStr(api_key))

# Configure browser
browser = Browser(
    config=BrowserConfig( 
        chrome_instance_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False,
    )
)

async def run_test_case(test_case):
    """Runs a test case using an agent and returns the result status."""
    agent = Agent(
        task=test_case['steps'],
        llm=llm,
        max_actions_per_step=4,
        browser=browser,
    )
    
    result = await agent.run(max_steps=30)

    # Extract last action result safely
    try:
        last_action = result.get_last()
        return "PASSED" if last_action and last_action.status == "success" else "FAILED"
    except AttributeError:
        return "FAILED"

async def main():
    test_cases_dir = 'test_cases'  # Directory where YAML test cases are stored
    yaml_files = [f for f in os.listdir(test_cases_dir) if f.endswith('.yaml')]
    
    test_results = []  # List to store results

    for yaml_file in yaml_files:
        yaml_path = os.path.join(test_cases_dir, yaml_file)
        
        # Read YAML file
        with open(yaml_path, 'r') as file:
            test_case = yaml.safe_load(file)
        
        print(f"Running test case: {test_case['title']}")

        # Execute test case and get result
        result_status = await run_test_case(test_case)
        
        # Store results for Excel
        test_results.append({
            "Test Case ID": test_case["id"],
            "Title": test_case["title"],
            "Status": result_status
        })

        print(f"Test case {test_case['id']} {result_status}")
        print("-" * 80)

    # Save results to Excel
    df = pd.DataFrame(test_results)
    df.to_excel("test_results.xlsx", index=False)
    print("Test results saved to test_results.xlsx")

async def close_browser():
    """Closes the browser safely after execution."""
    try:
        print("Closing browser...")
        await browser.close()
        print("Browser closed successfully.")
    except Exception as e:
        print(f"Error closing browser: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    finally:
        asyncio.run(close_browser())  # Ensures browser closes properly



# import asyncio
# import os
# import yaml
# import pandas as pd
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# from pydantic import SecretStr
# from browser_use import Agent, BrowserConfig
# from browser_use.browser.browser import Browser
# from browser_use.browser.context import BrowserContextConfig

# # Load environment variables
# load_dotenv()
# api_key = os.getenv('GEMINI_API_KEY')
# if not api_key:
#     raise ValueError('GEMINI_API_KEY is not set')

# # Initialize LLM with Gemini
# llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', api_key=SecretStr(api_key))

# # Configure browser
# browser = Browser(
#     config=BrowserConfig( 
#         chrome_instance_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#         headless=False,
#         # new_context_config=BrowserContextConfig(
#         #     viewport_expansion=0,
#         # )
#     )
# )

# async def run_test_case(test_case):
#     """Runs a test case using an agent and returns the result status."""
#     agent = Agent(
#         task=test_case['steps'],
#         llm=llm,
#         max_actions_per_step=4,
#         browser=browser,
#     )
    
#     result = await agent.run(max_steps=30)

#     # Extract last action result safely
#     try:
#         last_action = result.get_last()
#         return "PASSED" if last_action and last_action.status == "success" else "FAILED"
#     except AttributeError:
#         return "FAILED"

# async def main():
#     test_cases_dir = 'test_cases'  # Directory where YAML test cases are stored
#     yaml_files = [f for f in os.listdir(test_cases_dir) if f.endswith('.yaml')]
    
#     test_results = []  # List to store results

#     for yaml_file in yaml_files:
#         yaml_path = os.path.join(test_cases_dir, yaml_file)
        
#         # Read YAML file
#         with open(yaml_path, 'r') as file:
#             test_case = yaml.safe_load(file)
        
#         print(f"Running test case: {test_case['title']}")
        
#         # Execute test case and get result
#         result_status = await run_test_case(test_case)
        
#         # Store results for Excel
#         test_results.append({
#             "Test Case ID": test_case["id"],
#             "Title": test_case["title"],
#             "Status": result_status
#         })

#         print(f"Test case {test_case['id']} {result_status}")
#         print("-" * 80)

#     # Save results to Excel
#     df = pd.DataFrame(test_results)
#     df.to_excel("test_results.xlsx", index=False)
#     print("Test results saved to test_results.xlsx")

# if __name__ == '__main__':
#     try:
#         asyncio.run(main())
#     finally:
#         if 'browser' in locals():
#             try:
#                 loop = asyncio.get_running_loop()
#                 if loop.is_running():
#                     asyncio.create_task(browser.close())
#                 else:
#                     asyncio.run(browser.close())
#             except RuntimeError:
#                 pass  # Avoid errors if event loop is closed
