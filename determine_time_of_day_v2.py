import datetime as dt

time_offset = 2

def main(event):
    current_time = dt.datetime.utcnow() + dt.timedelta(hours=time_offset)
    current_time = current_time.time()
    
    if current_time < dt.time(9, 00) or current_time >= dt.time(18, 00):
        hour_of_inquiry = 'outside_working_hours'
    elif current_time < dt.time(18, 00):
        hour_of_inquiry = 'working_hours'
    else:
        hour_of_inquiry = 'outside_working_hours'
    
    '''
    if current_time < dt.time(9, 00):
        hour_of_inquiry = 'midnight_to_9AM'
    elif current_time < dt.time(12, 00):
        hour_of_inquiry = '9AM_to_12PM'
    elif current_time < dt.time(18, 00):
        hour_of_inquiry = '12PM_to_6PM'
    else:
        hour_of_inquiry = '6PM_to_midnight'
    '''
    
    current_date = dt.datetime.today().weekday()
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_of_inquiry = days_of_week[current_date]
    
    print(hour_of_inquiry, day_of_inquiry)
    
    return {
        "outputFields": {
            "hour_of_inquiry": hour_of_inquiry,
            "day_of_inquiry": day_of_inquiry
        }
    }
