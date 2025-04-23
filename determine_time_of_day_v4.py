# version using public api to check current time and day of week in a given market
# includes a fallback solution in case the primary api returns error

import requests
from datetime import datetime, timezone, timedelta

def get_local_time(market):
    # Determine timezone URL based on market
    # fallback solution credits: https://github.com/davidayalas/current-time?tab=readme-ov-file
    
    if market in ['gb', 'pt']:
        primary_url = "https://timeapi.io/api/Time/current/zone?timeZone=Europe/London"
        fallback_url = "https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=Europe/London"
    else:
        primary_url = "https://timeapi.io/api/Time/current/zone?timeZone=Europe/Berlin"
        fallback_url = "https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=Europe/Berlin"

    # 1) Primary TimeAPI
    try:
        # Try the primary API (TimeAPI)
        response = requests.get(primary_url, timeout=15)  # Added a timeout to prevent long waits
        response.raise_for_status()
        local_time = response.json()
        print(response.json())
        
        # Return the local time only if the expected keys are present
        if 'hour' in local_time and 'dayOfWeek' in local_time:
            return local_time, "TimeAPI"

    except requests.exceptions.RequestException as e:
        print(f"Primary API failed: {e}")
    
    # 2) Secondary Google Apps Script
    try:
        # Fallback if the primary API fails
        response = requests.get(fallback_url, timeout=15)
        response.raise_for_status()
        local_time = response.json()
        print(local_time)
        # Transform the response to match the structure of TimeAPI
        return {
          "hour": local_time["hours"],
          "dayOfWeek": local_time["dayofweekName"]  # Full day name (e.g., Monday)
        }, "davidayalas"

    except requests.exceptions.RequestException as e:
        print(f"Fallback API failed: {e}")
   
    # 3) Built-in datetime fallback to CET (UTC+1)
    try:
        cet = timezone(timedelta(hours=1))
        now_cet = datetime.now(cet)
        return {
            "hour": now_cet.hour,
            "dayOfWeek": now_cet.strftime("%A")
        }, "datetime"
    except Exception as e:
        print(f"Datetime fallback failed: {e}")
        
    # If both APIs fail, return an error message
    return {"error": "Unable to fetch local time from any method"}, "None"


def main(event):
    try:
        market = event["inputFields"].get("markets", None)
    except KeyError:
        market = None
    
    try:
        HV_eligible = event["inputFields"].get("HV_eligible", None)
    except KeyError:
        HV_eligible = None
    
    try:
        utm_source = event["inputFields"].get("utm_source", None)
    except KeyError:
        utm_source = None

    try:
        utm_campaign = event["inputFields"].get("utm_campaign", None)
    except KeyError:
        utm_campaign = None

    try:
        lead_scoring_system_level_2 = event["inputFields"].get("lead_scoring_system_level_2", None)
    except KeyError:
        lead_scoring_system_level_2 = None
        

    print(f"Market: {market}")

    # set priority based on lead source/scoring
    if utm_campaign == "personal_referral" or lead_scoring_system_level_2 == 3 or HV_eligible == True:
      lead_source_priority = 1
    elif lead_scoring_system_level_2 == 2:
      lead_source_priority = 2
    else:
      lead_source_priority = 1 

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

    print(f"Hour of Inquiry: {hour_of_inquiry}, Day of Inquiry: {day_of_inquiry}, Lead Priority: {lead_priority}, API Service Used: {api_service_used}, lead_source_priority: {lead_source_priority}, utm_source: {utm_source}, HV_eligible: {HV_eligible}")
    
    return {
        "outputFields": {
            "hour_of_inquiry": hour_of_inquiry,
            "day_of_inquiry": day_of_inquiry,
            "lead_priority": lead_priority,
            "api_service_used": api_service_used,
          	"lead_source_priority": lead_source_priority,
          	"utm_source": utm_source,
            "HV_eligible": HV_eligible
        }
    }
