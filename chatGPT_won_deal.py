import os
import requests
import re

def main(event): 
  secret_value = os.environ['OpenAI_Kuba']  
  url = 'https://api.openai.com/v1/completions'
  
  headers = {'Authorization': f'Bearer {secret_value}'}
  
  deal_name = event["inputFields"]["dealname"]
  deal_amount = event["inputFields"]["amount"]
  
  params = {
    "model": "text-davinci-003",
    "prompt": f"Celebrate and congratulate a closed won deal in the form of a poem. Keep it two-three sentences. Make it in funny style, use a sitcom analogy. Deal name is exactly {deal_name} and deal amount is ${deal_amount}",
    "max_tokens": 256,
    "temperature": 0.7
  }
  
  response = requests.post(url, headers=headers, json=params)
  prompt_output = response.json()['choices'][0]['text']
  
  print(response.json())
  
  # Return the output data that can be used in later actions in your workflow.
  return {
    "outputFields": {
      "prompt_output": prompt_output
    }
  }
