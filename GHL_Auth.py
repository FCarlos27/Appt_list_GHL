import requests
from urllib.parse import urlparse, parse_qs


client_id = "6822b3c1eb2278eef4c7ccdf-mampa1se"
client_secret = "ea8debfc-1dea-42f5-a048-7a339cf8358a"
Auth_page_url = "https://marketplace.gohighlevel.com/oauth/chooselocation?response_type=code&redirect_uri=https%3A%2F%2Fwww.google.com%2F%3Fhl%3Des&client_id=6822b3c1eb2278eef4c7ccdf-mampa1se&scope=calendars.readonly+calendars%2Fevents.readonly+contacts.readonly"


def get_code(url_code):
    import requests
    from urllib.parse import urlparse, parse_qs

    # Make a GET request 
    response = requests.get(url_code, allow_redirects=True)

    # Extract the final redirected URL
    final_url = response.url
    parsed_url = urlparse(final_url)
    query_params = parse_qs(parsed_url.query)

    # Get the authorization code
    auth_code = query_params.get("code", ["No code found"])[0]

    return auth_code

def get_access_token(auth_code = "", r_token = ""):
    url = "https://services.leadconnectorhq.com/oauth/token"

    # Prepare the payload for the GET request
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": auth_code,
        "refresh_token": r_token,  # No refresh token needed for first authentication
        "user_type": "Location",
        "redirect_uri": "https://www.google.com/?hl="
    }


    if r_token: # If refresh token is passed, grant_type has to be changed
        payload["grant_type"] = "refresh_token"

    # Set the headers for the request (Specified in the GHL API documentation)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        json_data = response.json()  # Corrected the JSON extraction
        token = json_data.get("access_token", "") # We get the access token from the response
        refresh_token = json_data.get("refresh_token", "")  # We get the refresh token from the response

        return token, refresh_token  # Return tokens to be stored
    else:
        print("Error:", response.status_code, response.text)
        return None, None  # Return None if request fails

def store_tokens(t, r_t):
    # Function to store tokens in a file
    if not t and not r_t:
        print("Tokens are None!")
        return 
    # Open the file in write mode and store the tokens
    with open("my_tokens.txt","w") as file:
        file.writelines([f"Token: {t}\n", f"Refresh_token: {r_t}\n"])

# Only used once to get the tokens, not necessary after the first time
if __name__  == "__main__":
    store_tokens(*get_access_token(get_code("https://www.google.com/?hl=es&code=4f0dce934ab776a6842cacbf2bfc8200e8c00162")))

