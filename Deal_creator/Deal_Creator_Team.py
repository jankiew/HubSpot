import os
import requests

# Retrieve the HubSpot access token from environment variables.
access_token = os.getenv("RevOps")

# Set up headers for Bearer token authentication.
headers = {
  "Authorization": f"Bearer {access_token}",
  "Content-Type": "application/json"
}

def ensure_option_exists(primary_team_id, label=None):
  """
  Checks if an option with the primary_team_id as the internal name exists
  in the 'creator_s_team' property on deals. If it does not exist, add the option.
  
  If a label is not provided, it retrieves the team name from the
  /settings/v3/users/teams endpoint.
    
  Args:
    primary_team_id (str): The primary team ID (used as the option's internal value).
    label (str, optional): The label for the new option. If not provided, it will be
                           retrieved from the teams endpoint.
  """
  # If label is not provided, fetch the team name from the teams API.
  if label is None:
    teams_url = "https://api.hubapi.com/settings/v3/users/teams"
    teams_response = requests.get(teams_url, headers=headers)
    teams_response.raise_for_status()
    teams_data = teams_response.json()
    teams = teams_data.get("results", [])
    
    found_label = None
    for team in teams:
      if team.get("id") == primary_team_id:
        found_label = team.get("name")
        break
      
    if found_label:
      label = found_label
    else:
      label = primary_team_id  # Fallback if team is not found

  # Retrieve the property details for 'creator_s_team' on deals.
  property_url = "https://api.hubapi.com/crm/v3/properties/deals/creator_s_team"
  response = requests.get(property_url, headers=headers)
  response.raise_for_status()
  property_data = response.json()
  
  options = property_data.get("options", [])
  
  # Check if an option with the given primary_team_id already exists.
  for option in options:
    if option.get("value") == primary_team_id:
      print(f"Option with value '{primary_team_id}' already exists.")
      return  # Option exists, nothing to add.
  
  # Determine displayOrder for the new option (one more than the highest order).
  if options:
    max_order = max(option.get("displayOrder", 0) for option in options)
    new_display_order = max_order + 1
  else:
    new_display_order = 1
     
  new_option = {
    "label": label,
    "value": primary_team_id,
    "displayOrder": new_display_order,
    "hidden": False
  }
  
  print(new_option)
  
  # Append the new option to the existing options.
  updated_options = options.copy()
  updated_options.append(new_option)
  
  print(updated_options)
  
  # Update the property with the new options list.
  patch_payload = {
    "options": updated_options
  }
  
  
  try:
    patch_response = requests.patch(property_url, headers=headers, json=patch_payload)
    patch_response.raise_for_status()
    print(f"Added new option: {new_option}")
  except requests.HTTPError as e:
    print("Error updating property options:", e)
    print("Response content:", patch_response.text)
    raise



def update_deal_creator_team(deal_id, primary_team_id,deal_creator_id):
  """
  Updates the deal's 'creator_s_team' property with the given primary team ID
  using the Deals API.
    
  Args:
  deal_id (str): The HubSpot deal ID.
  primary_team_id (str): The primary team ID to set.
    
  Returns:
  	dict: The response JSON from the update request.
  """
  
  deal_update_url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
  update_payload = {
    "properties": {
      "creator_s_team": primary_team_id,
      "deal_creator": deal_creator_id
    }
  }
  response = requests.patch(deal_update_url, headers=headers, json=update_payload)
  response.raise_for_status()  # Raises an error if the update fails.
  return response.json()



def main(event):
  # Use inputs to get data from any action in your workflow and use it in your code instead of having to use the HubSpot API.
  deal_creator_id = event["inputFields"]["hs_created_by_user_id"]
  deal_id = event["inputFields"]["hs_deal_id"]
  
  # Return the output data that can be used in later actions in your workflow.
  
  # Construct the URL for the User Provisioning API endpoint.
  url = f"https://api.hubapi.com/settings/v3/users/{deal_creator_id}"
  
  # Make the GET request to retrieve the user details.
  response = requests.get(url, headers=headers)
  response.raise_for_status()  # Raises an error for a bad status.
  user_data = response.json()
  
  primary_team_id = user_data.get("primaryTeamId", None)
  
  print(user_data)
  
  print(primary_team_id)

  # Ensure that the option for this primary_team_id exists in the 'creator_s_team' property.
  ensure_option_exists(primary_team_id)
  
  # Update the deal property 'creator_s_team' with the primary team ID.
  update_result = update_deal_creator_team(deal_id, primary_team_id,deal_creator_id)
  print("Deal update result:", update_result)
  

  return {
    "outputFields": {
      "deal_creator_id": deal_creator_id,
      "primary_team_id": primary_team_id
    }
  }
