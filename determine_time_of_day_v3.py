# version using public api to check current time and day of week in a given market
# includes a fallback solution in case the primary api returns error

import requests
from datetime import datetime

def get_local_time(market):
    # Determine timezone URL based on market
    # fallback solution credits: https://github.com/davidayalas/current-time?tab=readme-ov-file
    
    if market in ['gb', 'pt']:
        primary_url = "https://timeapi.io/api/Time/current/zone?timeZone=Europe/London"
        fallback_url = "https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=Europe/London"
    else:
        primary_url = "https://timeapi.io/api/Time/current/zone?timeZone=Europe/Berlin"
        fallback_url = "https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=Europe/Berlin"
    
    try:
        # Try the primary API (TimeAPI)
        response = requests.get(primary_url, timeout=5)  # Added a timeout to prevent long waits
        response.raise_for_status()
        local_time = response.json()
        
        # Return the local time only if the expected keys are present
        if 'hour' in local_time and 'dayOfWeek' in local_time:
            return local_time, "TimeAPI"

    except requests.exceptions.RequestException as e:
        print(f"Primary API failed: {e}")
    
    try:
        # Fallback if the primary API fails
        response = requests.get(fallback_url, timeout=5)
        response.raise_for_status()
        local_time = response.json()
        # Transform the response to match the structure of TimeAPI
        return {
          "hour": local_time["hour"],
          "dayOfWeek": local_time["dayOfWeek"]  # Full day name (e.g., Monday)
        }, "davidayalas"

    except requests.exceptions.RequestException as e:
        print(f"Fallback API failed: {e}")
        
    # If both APIs fail, return an error message
    return {"error": "Unable to fetch local time from both APIs"}, "None"


def main(event):
    try:
        market = event["inputFields"].get("markets", None)
    except KeyError:
        market = None

    print(f"Market: {market}")

    # Get the current local time and the API service used
    local_time, api_service_used = get_local_time(market)
    print(f"Local Time: {local_time}, API Service Used: {api_service_used}")

    if "error" in local_time:
        # If no time data is available, set default fallback values
        hour_of_inquiry = 'unknown'
        day_of_inquiry = 'unknown'
        lead_priority = 2  # Default to low priority if no time info is available
    else:
        current_hour = local_time.get("hour")
        day_of_inquiry = local_time.get("dayOfWeek")

        # Determine if the inquiry is during working hours
        if current_hour < 9 or current_hour >= 18:
            hour_of_inquiry = 'outside_working_hours'
        elif 9 <= current_hour < 18:
            hour_of_inquiry = 'working_hours'
        else:
            hour_of_inquiry = 'outside_working_hours'

        # Determine lead priority
        if day_of_inquiry in ["Saturday", "Sunday"]:
            lead_priority = 2
        elif hour_of_inquiry == 'outside_working_hours':
            lead_priority = 2
        else:
            lead_priority = 1

    print(f"Hour of Inquiry: {hour_of_inquiry}, Day of Inquiry: {day_of_inquiry}, Lead Priority: {lead_priority}, API Service Used: {api_service_used}")
    
    return {
        "outputFields": {
            "hour_of_inquiry": hour_of_inquiry,
            "day_of_inquiry": day_of_inquiry,
            "lead_priority": lead_priority,
            "api_service_used": api_service_used
        }
    }
