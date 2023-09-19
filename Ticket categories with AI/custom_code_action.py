import os
import requests
import logging
from typing import Dict, Any

isError = ''
log_buffer = []

# Initialize the logger
logging.basicConfig(level=logging.INFO)

# Fetch environment variable once
secret_value = os.getenv('OpenAI', None)
if secret_value is None:
    logging.error("OpenAI environment variable not set.")
    isError = 'Yes'
    exit(1)
    
# Static content
CATEGORIES = """Categories:

1. Invoice, installment and payment (payment)
2. KYC documentation (documentation)
3. Sales (sales)
4. Technical problems during purchase (technical)
5. Order status (order_status)
"""

INSTRUCTIONS = """Instructions: Carefully select ONLY ONE category from the list above and return ONLY the keyword found in the square brackets next to the category name."""

def call_openai_api(ticket_name: str, ticket_description: str) -> str:
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {'Authorization': f'Bearer {secret_value}'}
    params = {
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": f"""Objective: Your task is to categorize each customer support ticket based on the description provided by the customer. Tickets may come in various languages.
            	Our company provides services in XYZ. Mind that in case technical vocabulary is used.
                
                {CATEGORIES}
                {INSTRUCTIONS}
                
                Ticket name:
                {ticket_name}
                
                Ticket description:
                {ticket_description}
                
                Output:
                """,
        }],
        "max_tokens": 256,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=params)
    
    if response.status_code != 200:
        custom_log(f"API call failed with status code {response.status_code}", "ERROR")

        return {
          'prompt_output':'',
          'isError':'Yes'
        }
    
    return {
      'prompt_output': response.json()['choices'][0]['message']['content'].strip(),
      'isError':'No'
    }
  

def custom_log(msg, level="INFO"):
    log_message = f"{level}: {msg}"
    log_buffer.append(log_message)
    logging.getLogger().log(logging._nameToLevel[level], msg)

def main(event: Dict[str, Any]) -> Dict[str, Any]:
    ticket_description = event["inputFields"]["ticket_description"]
    ticket_name = event["inputFields"]["ticket_name"]
    
    api_output = call_openai_api(ticket_name, ticket_description)
    print(api_output)
    prompt_output = api_output['prompt_output']
    isError = api_output['isError']
    custom_log(f"API output: {prompt_output}")
    
    # Get the logs as a string
    log_contents = "\n".join(log_buffer)
    
    return {
        "outputFields": {
            "category_output": prompt_output,
            "isError": isError,
            "log_contents": log_contents
        }
    }
