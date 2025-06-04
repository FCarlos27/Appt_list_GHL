import requests
import os
import re
from GHL_Auth import get_access_token, store_tokens # Importing the function to get access token and store tokens
from datetime import timedelta, date, datetime, time

# Id used for https requests, you can find it in your location's calendar URL
calendar_id = "9XXgp3JWGzpmXXflbd1Y"
location_id = "kJ0VJIXGjDSOeoQs2Wox"

def menu():
    # Function to display the main menu and handle user input
    print("Welcome to the CarGet Motors Appointments Calendar!")
    print("Options:")
    print("========================================")
    print("1. View today's appointments")
    print("2. View tomorrow's appointments")
    print("3. View appointments for a specific date")
    print("4. Exit")

    option = input("Select an option(1-4): ")
    if option == "1":
        print("Fetching today's appointments...")
        create_list(get_calendar_events(*set_start_and_end_time(1), retrieve_tokens()[0]), 1)
        os.system("pause")  # Pause the program to view today's appointments
        os.system("cls")  # Clear the console for the next menu

    elif option == "2":
        print("Fetching tomorrow's appointments...")
        create_list(get_calendar_events(*set_start_and_end_time(2), retrieve_tokens()[0]), 2)
        os.system("pause")  
        os.system("cls")

    elif option == "3":
        # Fetch appointments for a specific date
        curr_year = datetime.now().year # Get the current year
        date_input = f"{curr_year}-{input(f'Enter the date (MM-DD): {curr_year}-')}" # Format the date input as YYYY-MM-DD
        print(f"Fetching appointments for {date_input}...")
        try: 
            # Validate the date format
            datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")
            os.system("pause")
            os.system("cls")
            return
        create_list(get_calendar_events(*set_start_and_end_time(3, date_input), retrieve_tokens()[0]), 3, date_input)
        os.system("pause")  
        os.system("cls")

    elif option == "4":
        print("Exiting the program.")
        exit()

    else:
        print("Invalid option. Please select a valid option (1-4).")
        os.system("pause")
        os.system("cls")  

def set_start_and_end_time(option, date_input = ""):
    # Function to set the start and end time based on the selected option, which is necessary parameter for the API request
    # The times used are based on the business hours of CarGet Motors

    if option == 1:
        # Set start_time for today at 10 AM
        today_start_time = (datetime.combine(date.today(), time(9)))
       
        # Set end_time for today at 8 PM
        today_end_time = today_start_time + timedelta(hours = 11)

        # Get start_time (timestamp) in milliseconds
        today_start_time = today_start_time.timestamp() * 1000

        # Get start_time (timestamp) in milliseconds
        today_end_time = today_end_time.timestamp() * 1000    

        # Return the start and end time for today
        return today_start_time, today_end_time
    
        
    elif option == 2:
        # Set start_time for tomorrow at 10 AM
        tomorrow_start_time = (datetime.combine(date.today() + timedelta(days = 1), time(9)))
    
        # set end_time for tomorrow at 8 PM
        tomorrow_end_time = tomorrow_start_time + timedelta(hours = 11)

        # Get start_time (timestamp) in milliseconds
        tomorrow_start_time = tomorrow_start_time.timestamp() * 1000

        # Get start_time (timestamp) in milliseconds
        tomorrow_end_time = tomorrow_end_time.timestamp() * 1000    

        # Return the start and end time for tomorrow
        return tomorrow_start_time, tomorrow_end_time

    elif option == 3:
        if date_input:
            try:
                # If a date is provided, parse it
                selected_date = datetime.strptime(date_input, "%Y-%m-%d").date()
                # Convert start_time and end_time to milliseconds
                start_time = int(datetime.combine(selected_date, time(9)).timestamp() * 1000)
                end_time = int(datetime.combine(selected_date, time(20)).timestamp() * 1000)

                # Return the provided start and end time
                return start_time, end_time
            except ValueError:
                raise ValueError("Invalid date format. Please use MM-DD format.")

def retrieve_tokens():
    # This functions is used daily since the token expires every 24 hours
    # Open the file, read the lines, and store them in a variable (text)
    with open('my_tokens.txt', 'r') as file:
        text = file.read()

    # Regular expression pattern to retrieve both token and refresh_token
    pattern = r"Token: ([^\n]+)\nRefresh_token: ([^\n]+)"

    # Check if there's a match between pattern and file content
    match = re.search(pattern, text)

    if match:
        token = match.group(1)  # Retrieves the Token value
        refresh_token = match.group(2)  # Retrieves the Refresh_token value
        return token, refresh_token
    else:
        print("No tokens found!")
        return "", ""  # Return None for both if not found


def get_calendar_events(start_time, end_time, token):
    # Function to get calendar events from the GHL API
    # This function it's named after the endpoint used in the GHL API documentation
    url = "https://services.leadconnectorhq.com/calendars/events"

    querystring = {"locationId": f"{location_id}", "calendarId" : f"{calendar_id}","startTime": f"{start_time}", "endTime" : f"{end_time}"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-04-15",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 401: # If token is expired 
        store_tokens(*get_access_token(r_token = retrieve_tokens()[1]))  
        new_token = retrieve_tokens()[0]  # Get the latest token after refreshing
        return get_calendar_events(start_time, end_time, new_token)  # Pass the new token

    return response.json() # GHL retrieves the events in JSON format


#  In the next function, we could get the info from every contact directly calling the API in the contacts endpoint
#  But the notes field contains the description of the contact's appointment
#  This is the standar way of the company to store the appointments, so we will use it

def create_list(json_file, option, date_input = ""):
    # Function to create a list of appointments from the JSON file
    pattern = r"\*?\*?NEW APPOINTMENT\*?\*?|\*?RESCHEDULE\*?|\*\s*BOOKED FOR (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Today)\s*(.*)" 
    # This pattern is used to remove the "NEW APPOINTMENT" and "RESCHEDULE" text from the notes field
    #  Since we don't want to show this text in the appointments list
    if option == 1:
        print("*CarGet Motors Appointments for Today*\n")
    elif option == 2:
        print("*CarGet Motors Appointments for Today*\n") # We use today here since this list is used as reference for tomorrow's appointments
    else:
        print(f"*CarGet Motors Appointments for {date_input}*\n")
    
    i = 0
    # the list is created by iterating through the events in the JSON file
    for event in json_file["events"]:
        if event["appointmentStatus"] == "confirmed" or event["appointmentStatus"] == "showed":
            i += 1 
            description = re.sub(pattern, "", event["notes"]).strip()
            print(f"{i}.", description, "\n")
            if event["appointmentStatus"] == "showed" and option == 1: # This "if" is for myself to keep track of every showed appointment
                print("Status: Showed\n")
            

    if i == 0:
        print("No appointments found for this date.")

while True:
    menu()
