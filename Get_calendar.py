import requests, os, re, Get_gist
from GHL_Auth import get_access_token
from datetime import timedelta, date, datetime, time
from dotenv import load_dotenv

# Id used for https requests, you can find it in your location's calendar URL
load_dotenv()  # Load environment variables from .env file
calendar_id = os.getenv("CALENDAR_ID")
location_id = os.getenv("LOCATION_ID")

def menu():
    # Function to display the main menu and handle user input
    print("Welcome to the CarGet Motors Appointments Calendar!")
    print("Options:")
    print("========================================")
    print("1. View today's appointments")
    print("2. View tomorrow's appointments")
    print("3. View appointments for a specific date")
    print("4. Exit")

    auth_token = tokens()[0]  # Get the access token from the gist file

    while True:
        try:
            option = int(input("Select an option (1-4): "))  
            break  # Exit loop once input is valid
        except ValueError:
            print("Invalid input! Please enter a number.")

    if option == 1:
        print("Fetching today's appointments...\n")
        start_time, end_time = set_start_and_end_time(option)
        json_file = get_calendar_events(start_time, end_time, auth_token)  # Get today's appointments
        create_list(json_file, option)  # Create the list of appointments
        os.system("pause")  # Pause the program to view today's appointments
        os.system("cls")  # Clear the console for the next menu

    elif option == 2:
        print("Fetching tomorrow's appointments...\n")
        start_time, end_time = set_start_and_end_time(option)
        create_list(get_calendar_events(*set_start_and_end_time(option), auth_token), option)
        os.system("pause")  
        os.system("cls")

    elif option == 3:
        # Fetch appointments for a specific date
        curr_year = datetime.now().year # Get the current year
        date_input = f"{curr_year}-{input(f'Enter the date (MM-DD): {curr_year}-')}" # Format the date input as YYYY-MM-DD
        print(f"Fetching appointments for {date_input}...\n")
        try: 
            # Validate the date format
            datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")
            os.system("pause")
            os.system("cls")
            return

        start_time, end_time = set_start_and_end_time(option, date_input)
        json_file = get_calendar_events(start_time, end_time, auth_token) 
        create_list(json_file, option, date_input)
        os.system("pause")  
        os.system("cls")

    elif option == 4:
        print("Exiting the program.")
        exit()

    else:
        print("Invalid option. Please select a valid option (1-4).")
        os.system("pause")
        os.system("cls")  

def set_start_and_end_time(option, date_input = ''):
    # Function to set the start and end time based on the selected option, obligatory parameter for GHL API request
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

def tokens():
    # Function to get tokens from the Gist file
    json_file = Get_gist.get_json_gist()  # Get the gist file content
    return Get_gist.retrieve_tks_json(json_file)  # Retrieve tokens from the gist file


def get_calendar_events(start_time, end_time, token):
    # Function to get calendar events from the GHL API
    url = "https://services.leadconnectorhq.com/calendars/events"

    querystring = {"locationId": f"{location_id}", "calendarId" : f"{calendar_id}","startTime": f"{start_time}", "endTime" : f"{end_time}"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-04-15",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 401: # If token is expired 
        r_token = tokens()[1] # Get the refresh token from the gist file
        new_tkn, new_r_tkn = get_access_token(r_token = r_token)  # Refresh the token
        if new_tkn is None and new_r_tkn is None:
            print("Failed to refresh the token. Please check your credentials.") # Check r_token in gist file
            return None
        Get_gist.update_tks_in_gist(new_tkn, new_r_tkn) # Update the gist file with the new tokens
        return get_calendar_events(start_time, end_time, new_tkn)  # Pass the new token

    return response.json() # GHL retrieves the events in JSON format

def create_list(json_file, option, date_input = ""):
    # Function to create a list of appointments from the JSON file
    pattern = r"\*?\*?NEW APPOINTMENT\*?\*?|\*?RESCHEDULE\*?|\*(BOOKED FOR)\s+\w+(\s+AT\s+)(\d+)\.(\d+)"
    replacement = lambda match: (
    f"*BOOKED FOR TODAY{match.group(2)}{match.group(3)}:{match.group(4)}"
    if match.group(1) else ""  # Remove "NEW APPOINTMENT" & "RESCHEDULE"
)

    if option == 1:
        print("*CarGet Motors Appointments for Today*\n")
    elif option == 2:
        print("*CarGet Motors Appointments for Today*\n") # We use "today" here since this list is used as reference for tomorrow's appointments
    else:
        print(f"*CarGet Motors Appointments for {date_input}*\n")
    
    i = 0
    for event in json_file["events"]:
        if event["appointmentStatus"] in ["confirmed"]:
            i += 1
            description = re.sub(pattern, replacement, event["notes"]).strip()
            print(f"{i}.", description, "\n")

        elif event["appointmentStatus"] == "showed" and option == 1:
            i += 1
            description = re.sub(pattern, replacement, event["notes"]).strip()
            print(f"{i}.", description, "\n")
            print("Status: Showed\n")
            
    if i == 0:
        print("No appointments found for this date.")

while True:
    menu()


 
