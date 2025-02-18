# the objective of the script is to asssociate lead with a most recent deal created on a contact,
# when a lead is moved to Qualified by automation
# 1. get last deal from the associated contact
# 2. associate lead with a deal 

# Use inputs to get data from any action in your workflow and use it in your code instead of having to use the HubSpot API.
from datetime import datetime
import requests
import os
import json
from hubspot import HubSpot

# HubSpot API key
api_key = os.getenv('OPS_HubSpot_Workflow_app')

headers = {
  'Authorization': f'Bearer {api_key}',
  'Content-Type': 'application/json'
}

def get_last_deal(contact_id):
    """
    Retrieves last deal associated with a given contact ID

    :param contact_id: The HubSpot contact ID.
    :return: Dictionary with last deal associated to a contact, including its details.
    """
    # HubSpot Associations API Endpoint
    associations_url = f"https://api.hubapi.com/crm/v4/objects/contacts/{contact_id}/associations/deals"

    # Fetch associated deals
    response = requests.get(associations_url, headers=headers, params={'limit': 100})

    if response.status_code != 200:
        raise Exception(f"Error fetching associations: {response.text}")

    associations_data = response.json()
    print(associations_data)

    deal_ids = [assoc['toObjectId'] for assoc in associations_data.get('results', [])]
    print(deal_ids)

    if not deal_ids:
        return []

    # Batch fetch deal details
    deal_url = "https://api.hubapi.com/crm/v3/objects/deals/batch/read"
    deals_payload = {
        "inputs": [{"id": tid} for tid in deal_ids],
        "properties": ["hubspot_owner_id"
                      ]
    }

    deals_response = requests.post(deal_url, headers=headers, json=deals_payload)

    if deals_response.status_code != 200:
        raise Exception(f"Error fetching deals: {deals_response.text}")

    deals_data = deals_response.json()
    last_deal = dict()

    # Sort deals by created date in descending order (most recent first)
    sorted_deals = sorted(deals_data.get('results', []), key=lambda x: x['properties'].get('createdate', 0), reverse=True)

    if sorted_deals:
        # Select the most recent deal
        most_recent_deal = sorted_deals[0]
        properties = most_recent_deal.get('properties', {})

        # Populate the last_deal dictionary with required information
        last_deal = {
            'deal_id': properties.get('hs_object_id', ''),
            'deal_owner': properties.get('hubspot_owner_id', ''),
            'created_at': properties.get('createdate', 'N/A')
        }
    else:
        last_deal = {}

    return last_deal


def associate_lead_to_deal(lead_id, deal_id):
  """
    Creates a association between lead and deal records.

    :param lead_id: The HubSpot record ID of a lead record.
    :param deal_id: The HubSpot record ID of a deal record.
    :return: raises exception if failure.
  """  
  endpoint_url = f"https://api.hubapi.com/crm/v4/objects/0-136/{lead_id}/associations/default/0-3/{deal_id}"
  
  # Send POST request to create association
  response = requests.put(endpoint_url, headers=headers)
   
  if response.status_code == 201:
    print("Association created successfully.")
    association_creation_status = 'success'
    
  else:
    print(f"Association creation error. {response.status_code} {response.text}")
    association_creation_status = "error"
  
  return association_creation_status

def main(event):
  lead_id = event["inputFields"]["lead_id"]
  contact_id = event["inputFields"]["contact_id"]
  print(contact_id)
    
  last_deal = get_last_deal(contact_id)
  print(last_deal)
  
  if len(last_deal) > 0:
    deal_id = last_deal['deal_id']

    create_association = associate_lead_to_deal(lead_id, deal_id)
  
  else:
    print("No deal to associate")
    create_association = "none"
      
  # Return the output data that can be used in later actions in your workflow.
  return {
    "outputFields": {
      "lead_id": lead_id,
      "contact_id": contact_id,
      "last_deal": last_deal,
      "create_association": create_association
    }
  }
