# CREDITS:
# https://community.hubspot.com/t5/HubSpot-Ideas/Workflow-filtering-of-conversations-before-creating-a-ticket/idi-p/768825

# get conversation subjectline and check if it's a reply to an email with a subjectline from the EmailSubjectlines

import os
import requests
import logging
from typing import Dict, Any

isError = ''
log_buffer = []

# Initialize the logger
logging.basicConfig(level=logging.INFO)

# Fetch environment variable once
secret_value = os.getenv('YOUR_SECRET_KEY', None)
if secret_value is None:
    logging.error("API key variable not set.")
    isError = 'Yes'
    exit(1)

# Static content
EmailSubjectlines = [
  "list subjectlines here"
]


def call_conversations_api(threadID: str) -> str:
  url = 'https://api.hubapi.com/conversations/v3/conversations/threads/'
  headers = {'Authorization': f'Bearer {secret_value}'}
  base_url="https://api.hubapi.com/conversations/v3/conversations/threads/"
    
  #API Request Headers
  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + secret_value,
  }
  request_url = base_url+threadID+'/'+'messages'
  print(request_url)
  
  response = requests.get( request_url, headers=headers)
  print(response.status_code)

  Jresp = response.json()
  
  messageIndex=0
  while Jresp["results"][messageIndex]["type"] != "MESSAGE":
    messageIndex+=1
  print("index: ", messageIndex,Jresp["results"][messageIndex]["type"])
    
  try:
    title = Jresp["results"][messageIndex]["subject"]
    print("Title: ", type(title), len(title))
  except:
    title="No subject"
    
  
  return title
  

def custom_log(msg, level="INFO"):
    log_message = f"{level}: {msg}"
    log_buffer.append(log_message)
    logging.getLogger().log(logging._nameToLevel[level], msg)

def main(event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        threadID = event["inputFields"]["hs_thread_id"]
    except KeyError:
        # If "threadID" is not present in event["inputFields"], assign ''
        threadID = ''

    conversation_title = call_conversations_api(threadID)
    
    print(conversation_title)
    
    if any(conversation_title in s for s in EmailSubjectlines):
      is_email_response = "yes"
    else:
      is_email_response = "no"
    
    # Get the logs as a string
    log_contents = "\n".join(log_buffer)
    
    return {
        "outputFields": {
            "conversation_title": conversation_title,
          	"is_email_response": is_email_response,
            "isError": isError,
            "log_contents": log_contents
        }
    }
  
