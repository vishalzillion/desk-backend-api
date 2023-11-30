import requests
import os
from dotenv import load_dotenv

load_dotenv()

sendbird_app_id = os.getenv("SENDBIRD_APP_ID")
sendbird_api_key = os.getenv("SENDBIRD_API_KEY")
desk_api = os.getenv("DESK_API")

ticket_id = 803866
agent_id = 872

headers = {
    'Content-Type': 'application/json',
    'SENDBIRDDESKAPITOKEN': desk_api,
     # Use 'Api-Token' for Sendbird Desk API
}

data = {
    "assignee_id": agent_id
}

sendbird_api_endpoint = f'https://desk-api-{sendbird_app_id}.sendbird.com/platform/v1/tickets/'

# Construct the complete URL by appending ticket_id to the base URL
sendbird_api_url = sendbird_api_endpoint + str(ticket_id)

# Make a PATCH request to update the ticket with the assigned agent
response = requests.patch(sendbird_api_url, json=data, headers=headers)

print(response.json())
