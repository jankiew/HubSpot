def main(event):
  # Use inputs to get data from any action in your workflow and use it in your code instead of having to use the HubSpot API.
  company_id = event["inputFields"]["company_id"]
  
  import requests
  import os
  from hubspot import HubSpot
  
  status = "No issues"
  status_details = None
  
  # HubSpot API endpoint to retrieve company contacts
  #v2 api
  company_endpoint = f"https://api.hubapi.com/companies/v2/companies/{company_id}/contacts"
   
  # HubSpot API key
  api_key = os.getenv('YOUR_SECRET_KEY_NAME')
  
  #company Lifecycle Stage
  company_lcs = event["inputFields"]["lifecyclestage"]
  print(f'COMPANY LIFECYCLE STAGE: {company_lcs}')
  
  # Set the headers for the API request
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  # v2 api
  # Set the parameters for the API request
  params = {
    "filterGroups": [
      {
        "filters": [
          {
            "propertyName": "lifecyclestage",
            "operator": "EQ",
            "value": company_lcs
          }
        ]
      }
    ]
  }
  
  # Send GET request to retrieve contacts
  #v2 api
  try:
    response = requests.get(company_endpoint, headers=headers, params=params)
  except:
    status = "Failed"
    status_details = "failed to get contacts associated to a company"
    raise
    return {
      "outputFields": {
        "status": status,
        "status_details": status_details
      }
    }
    
    
  if response.status_code == 200:
    # Get the contacts from the response
    contacts = response.json().get("contacts", [])
    
    # Create a dictionary to store the desired properties for each contact
    contact_data = []
    
    # get contact's lifecycle stage
    for contact in contacts:
      try:
        contact_id = contact['identities'][0]['vid']
        contact_email = contact['identities'][0]['identity'][0]['value']
        contact_create_date = contact['identities'][0]['identity'][0]['timestamp']
        
      except:
        status = "Failed"
        status_details = "failed to get specific contact details"
        return {
          "outputFields": {
            "status": status,
            "status_details": status_details
          }
        }
        
      contact_lifecycle_stage = None
      
      contact_endpoint = f"https://api.hubapi.com/contacts/v1/contact/vid/{contact_id}/profile"
      
      try:
        contact_response = requests.get(contact_endpoint, headers=headers)
      except:
        print(f"Failed to retrieve contact response for {contact_id}. Status code: {contact_response.status_code}")
        raise
      
      if contact_response.status_code == 200:
        try:
          # Get the contact properties from the contact_response
          properties = contact_response.json().get("properties", {})
          # Fetch the lifecycle stage property value
          contact_lifecycle_stage = properties.get("lifecyclestage", {}).get("value")
        except:
          status = "Failed"
          status_details = "failed to get lifecycle stage of a specific contact"
          return {
            "outputFields": {
            "status": status,
            "status_details": status_details
            }
          }
          
      else:
        print(f"Failed to retrieve contact properties. Status code: {contact_response.status_code}")
      
      contact_info = {
        "contact_id": contact_id,
        "contact_email": contact_email,
        "create_date": contact_create_date,
        "lifecycle_stage": contact_lifecycle_stage,
      }
      
      contact_data.append(contact_info)

    print(f"ASSOCIATED CONTACTS: {contact_data}")  
    
  else:
    print(f"Failed to retrieve contacts. Status code: {response.status_code}")
    contacts = 'none'
    contact_data = None
    
    status = "Failed"
    status_details = "failed to get contacts associated to a company"
  
  
  # get the oldest primary contact with matching lifecycle stage
  try:
    oldest_primary_contact = min(
      (contact for contact in contact_data if contact["lifecycle_stage"] == company_lcs),
      key=lambda x: x["create_date"]
    )
    print(f"OLDEST PRIMARY CONTACT: {oldest_primary_contact}")
  
  
    #update the oldest matching contact with Yes in "Opt-in LCS Funnel Analytics" property 
    contact_update_endpoint = f"https://api.hubapi.com/contacts/v1/contact/vid/{oldest_primary_contact['contact_id']}/profile"
  
    # Set the payload for updating the property
    data = {
      "properties": [
        {
          "property": 'opt_in_lcs_funnel_analytics',
          "value": 'Yes'
        }
      ]
    }
  
    # Send the POST request to update the contact's property
    try:
      response = requests.post(contact_update_endpoint, headers=headers, json=data)
    
      if response.status_code == 204:
        print(f"Contact property updated successfully for {oldest_primary_contact['contact_email']}, id: {oldest_primary_contact['contact_id']}.")
      else:
        print(f"Failed to update contact property. Status code: {response.status_code}")
    except:
      status = "Failed"
      status_details = "failed to update the oldest primary contact"
      return {
        "outputFields": {
          "status": status,
          "status_details": status_details
        }
      }
      
  except:
    status = "Failed"
    status_details = "failed to get the oldest primary contact"
    return {
      "outputFields": {
        "status": status,
        "status_details": status_details
      }
    }
  
  # Return the output data that can be used in later actions in your workflow.
  return {
    "outputFields": {
      "status": status,
      "status_details": status_details
    }
  }
