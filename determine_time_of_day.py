# determine if it's AM/PM. Use that to set a specific delay in a workflow depending if the action takes place AM/PM. Eg. if the workflow is triggered PM, and you want to create a tasks AM next day   

import datetime as dt

time_offset = 1

def main(event):
  current_time = dt.datetime.now() + dt.timedelta(hours=time_offset)
  current_time = current_time.time()
  if current_time < dt.time(12,00):
    time_of_inquiry = 'AM'
  else:
    time_of_inquiry = 'PM'
  print(time_of_inquiry)
  # Return the output data that can be used in later actions in your workflow.
  return {
    "outputFields": {
      "time_of_inquiry": time_of_inquiry
    }
  }
