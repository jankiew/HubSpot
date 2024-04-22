def main(event):
  # Use inputs to get data from any action in your workflow and use it in your code instead of having to use the HubSpot API.
  import requests
  import os
  from hubspot import HubSpot
  
  # HubSpot API key
  api_key = os.getenv('API_key')
  
  ownerID = event["inputFields"]["ownerID"]
  
  owner_endpoint = f"https://api.hubapi.com/crm/v3/owners/{ownerID}?idProperty=id&archived=false"

  # Set the headers for the API request
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  # Send GET request to retrieve contacts
  response = requests.get(owner_endpoint, headers=headers)

  if response.json().get("status", []) == 'error':
    email = ""
  else:
    email = response.json().get("email", [])
  
  print(response.text)
  # Return the output data that can be used in later actions in your workflow.
  return {
    "outputFields": {
      "email": email
    }
  }
