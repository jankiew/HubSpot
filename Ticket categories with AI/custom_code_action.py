import os
import requests
import re

def main(event): 
  secret_value = os.environ['OpenAI']  
  url = 'https://api.openai.com/v1/chat/completions'
  
  headers = {'Authorization': f'Bearer {secret_value}'}
  
  ticket_description = event["inputFields"]["ticket_description"]
  
  params = {
    "model": "gpt-3.5-turbo",
    "messages": [{
        "role": "user",
        "content": f"""We want to classify support tickets into relevant category. Your task is to classify the customer support ticket based on its description provided by the customer.
        
        	  Ticket description is: {ticket_description}. Please classify that to one of these categories.
    	
        	  1. Invoice, installment and payment (payment)
    		    2. KYC documentation (documentation)
    		    3. Sales (sales)
    		    4. Technical problems during purchase (technical)
    		    5. Order status (order_status)
            
            In the response return only one word that is the value in the brackets after a selected category name.
    	""",
      }
    ],    
    "max_tokens": 256,
    "temperature": 0.7
  }
  
  response = requests.post(url, headers=headers, json=params)
  prompt_output = response.json()['choices'][0]['message']['content'].strip()
  print(prompt_output)
  
  # Return the output data that can be used in later actions in your workflow.
  return {
    "outputFields": {
      "prompt_output": prompt_output
    }
  }
