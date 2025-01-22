# Use inputs to get data from any action in your workflow and use it in your code instead of having to use the HubSpot API.
import requests
import os
import json
from hubspot import HubSpot

new_stage_id = {
  '0': '1', # IT
  '5370445': '5370446', # PT  
  '3636100': '12289400', # PL
  '6055533': '18538414', # FR
  '10269822': '29856908', # UK
  '72187614': '173144812', # ES
  '11377503': '33961887', # SCA
  '127897585': '256122604', # DACH
  '237646037': '401290228', # BE
  '239129274': '402809056' # NL
}


# HubSpot API key
api_key = os.getenv('secret_name')

headers = {
  'Authorization': f'Bearer {api_key}',
  'Content-Type': 'application/json'
}

def get_associated_open_tickets(contact_id, ticket_id, ticket_category, ticket_pipeline):
    """
    Retrieves all open tickets associated with a given contact ID based on the 'is_ticket_open_' property.

    :param contact_id: The HubSpot contact ID.
    :return: List of open tickets with their details.
    """
    # HubSpot Associations API Endpoint
    associations_url = f"https://api.hubapi.com/crm/v4/objects/contacts/{contact_id}/associations/tickets"

    # Fetch associated tickets
    response = requests.get(associations_url, headers=headers, params={'limit': 100})

    if response.status_code != 200:
        raise Exception(f"Error fetching associations: {response.text}")

    associations_data = response.json()
    print(associations_data)

    ticket_ids = [assoc['toObjectId'] for assoc in associations_data.get('results', [])]
    print(ticket_ids)

    if not ticket_ids:
        return []

    # Batch fetch ticket details
    tickets_url = "https://api.hubapi.com/crm/v3/objects/tickets/batch/read"
    tickets_payload = {
        "inputs": [{"id": tid} for tid in ticket_ids],
        "properties": ["is_ticket_open_",
                       "hs_ticket_category",
                       "content",
                       "hs_pipeline"
                      ]
    }

    tickets_response = requests.post(tickets_url, headers=headers, json=tickets_payload)

    if tickets_response.status_code != 200:
        raise Exception(f"Error fetching tickets: {tickets_response.text}")

    tickets_data = tickets_response.json()

    open_tickets = []

    # Define what constitutes an "open" ticket based on the 'is_ticket_open_' property
    ticket_open_property = 'is_ticket_open_'  # Custom property name
    open_value = '1'  # Value indicating the ticket is open

    for ticket in tickets_data.get('results', []):
        properties = ticket.get('properties', {})
        print(properties)
        is_open = properties.get(ticket_open_property, '')
        original_ticket_id = properties.get('hs_object_id', '')
        original_ticket_category = properties.get('hs_ticket_category', '')
        original_ticket_pipeline = properties.get('hs_pipeline', '')
        if original_ticket_id != ticket_id and is_open == open_value and original_ticket_category == ticket_category and original_ticket_pipeline == ticket_pipeline:
            open_tickets.append({
                'original_ticket_id': ticket.get('id'),
                'original_ticket_description': properties.get('content', ''),
                'is_open': is_open,
                'created_at': properties.get('createdate', 'N/A')
            })
    return open_tickets

def update_source_ticket_stage_and_description(original_ticket_id, ticket_id, original_ticket_description, ticket_description, ticket_pipeline):
    """
    Updates ticket status to New and appends the description of a duplicate ticket to the original ticket in a specified format.

    :param original_ticket_id: The ID of the original (master) ticket.
    :param ticket_id: The ID of the duplicate (child) ticket.
    :param original_ticket_description: The current description of the original ticket.
    :param ticket_description: The description of the duplicate ticket to be appended.
    :param ticket_pipeline: The id of the ticket pipeline.
    :return: Dictionary indicating success or error message.
    """
    # Validate input parameters
    if not all([original_ticket_id, ticket_id, original_ticket_description, ticket_description, ticket_pipeline]):
        print("All input parameters must be provided.")
        return {
            'status': 'error',
            'message': 'All input parameters must be provided.'
        }
    
    if original_ticket_id == ticket_id:
        print("original_ticket_id and ticket_id cannot be the same.")
        return {
            'status': 'error',
            'message': 'original_ticket_id and ticket_id cannot be the same.'
        }

    # Construct the new description in the specified format
    new_description = (
        "(Duplicate ticket merged)\n\n"
        "NEW TICKET\n"
        f"{ticket_description}\n\n"
        "ORIGINAL TICKET DESCRIPTION\n"
        f"{original_ticket_description}"
    )

    # Prepare the payload for the PATCH request
    payload = {
        "properties": {
            "content": new_description,
            "hs_pipeline_stage": new_stage_id[ticket_pipeline]
        }
    }

    # Define the API endpoint for updating the ticket
    update_url = f"https://api.hubapi.com/crm/v3/objects/tickets/{original_ticket_id}"

    try:
        # Make the PATCH request to update the original ticket's description
        response = requests.patch(update_url, headers=headers, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Successfully updated description and stage for ticket {original_ticket_id}.")
            return {
                'status': 'success',
                'message': f"Ticket {original_ticket_id} description and stage updated successfully."
            }
        else:
            # Log the error details
            print(
                f"Failed to update original ticket {original_ticket_id}. "
                f"Status Code: {response.status_code}, Response: {response.text}"
            )
            return {
                'status': 'error',
                'message': f"Failed to update original ticket {original_ticket_id}. "
                           f"Status Code: {response.status_code}, Response: {response.text}"
            }

    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        print("An exception occurred while updating the original ticket.")
        return {
            'status': 'error',
            'message': f"An exception occurred: {str(e)}"
        }

def merge_tickets(ticket_id, original_ticket_id):
    """
    Merges a child ticket into a master ticket using HubSpot's Merge Tickets API.

    :param ticket_id: The ID of the ticket to be merged (child ticket).
    :param original_ticket_id: The ID of the master ticket.
    :return: Dictionary indicating success or error message.
    """

    # Define the Merge Tickets API endpoint
    merge_url = "https://api.hubapi.com/crm/v3/objects/tickets/merge"

    # Prepare the payload as per HubSpot's API requirements
    payload = {
        "primaryObjectId": original_ticket_id,
        "objectIdToMerge": ticket_id
    }

    try:
      # Make the POST request to merge the tickets
      response = requests.post(merge_url, headers=headers, json=payload)
      print(response)
      
      # Check if the request was successful
      if response.status_code in [200, 202]:
        print(f"Successfully merged ticket {ticket_id} into {original_ticket_id}.")
        return {
          'status': 'success',
          'message': f"Ticket {ticket_id} has been successfully merged into {original_ticket_id}."
        }
      else:
        # Log the error details
        print(f"Failed to merge tickets. Status Code: {response.status_code}, Response: {response.text}")
        return {
          'status': 'error',
          'message': f"Failed to merge tickets. Status Code: {response.status_code}, Response: {response.text}"
        }

    except requests.exceptions.RequestException as e:
      # Handle any exceptions during the request
      print("An exception occurred while attempting to merge tickets.")
      return {
        'status': 'error',
        'message': f"An exception occurred: {str(e)}"
      }
  
  
def main(event):
  
  contact_id = event["inputFields"]["contact_id"]
  ticket_id = event["inputFields"]["ticket_id"]
  ticket_pipeline = event["inputFields"]["ticket_pipeline"]
  ticket_category = event["inputFields"]["ticket_category"]
  ticket_description = event["inputFields"]["ticket_description"]
  print(contact_id)
  
  merge_status = "not applicable"
  
  open_tickets = get_associated_open_tickets(contact_id, ticket_id, ticket_category, ticket_pipeline)
  print(open_tickets)
  
  if len(open_tickets) == 0:
    is_duplicate = 'no'
  else:
    is_duplicate = 'yes'
    original_ticket_id = open_tickets[0]['original_ticket_id']
    original_ticket_description = open_tickets[0]['original_ticket_description']
    
    update_source_ticket = update_source_ticket_stage_and_description(original_ticket_id, ticket_id, original_ticket_description, ticket_description,ticket_pipeline)
    print(update_source_ticket)

    if update_source_ticket['status'] == 'success':
        merged_tickets = merge_tickets(ticket_id, open_tickets[0]['original_ticket_id'])
        merge_status = merged_tickets['status']
        print(merged_tickets)
		
  
  # Return the output data that can be used in later actions in your workflow.
  return {
    "outputFields": {
      "contact_id": contact_id,
      "open_tickets": open_tickets,
      "is_duplicate": is_duplicate,
      "merge_status": merge_status 
    }
  }
