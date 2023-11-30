import requests
import os
from dotenv import load_dotenv

load_dotenv()


sendbird_app_id = os.getenv("SENDBIRD_APP_ID")
sendbird_api_key = os.getenv("SENDBIRD_API_KEY")
desk_api = os.getenv("DESK_API")




def create_sendbird_user(username):
    try:
        sendbird_api_endpoint = f'https://api-{sendbird_app_id}.sendbird.com/v3/users'

        headers = {
            'Content-Type': 'application/json',
            'Api-Token': sendbird_api_key,
        }

        user_exists_response = requests.get(sendbird_api_endpoint, headers=headers, params={'user_ids': username})

        if user_exists_response.status_code == 200:
            users_data = user_exists_response.json().get('users')
            if users_data and len(users_data) > 0:
                # User already exists, return the existing user_id
                return users_data[0]['user_id']
            else:
                # User doesn't exist, proceed to create the user
                return _create_sendbird_user(sendbird_api_endpoint, headers, username)

        else:
            error_message = user_exists_response.json().get('message', 'Failed to check Sendbird user existence')
            return {'error': error_message}

    except requests.RequestException as e:
        return {'error': f'Request Exception: {e}'}
    except Exception as e:
        return {'error': f'Error creating/fetching Sendbird user: {e}'}

def _create_sendbird_user(sendbird_api_endpoint, headers, username):
    try:
        payload = {
            'user_id': username,
            'nickname': username,
            'profile_url': 'https://templates.joomla-monster.com/joomla30/jm-news-portal/components/com_djclassifieds/assets/images/default_profile.png'
        }

        # Attempt to create the user in Sendbird
        creation_response = requests.post(sendbird_api_endpoint, json=payload, headers=headers)

        return creation_response

    except requests.RequestException as e:
        return {'error': f'Request Exception: {e}'}
    except Exception as e:
        return {'error': f'Error creating Sendbird user: {e}'}
    


# Function to send a message to a channel using Sendbird Platform API
def send_message_to_channel(channel_url, username, message_content):
    try:
        sendbird_api_endpoint = f'https://api-{sendbird_app_id}.sendbird.com/v3/group_channels/{channel_url}/messages'
        headers = {
            'Content-Type': 'application/json',
            'Api-Token': sendbird_api_key,
        }

        payload = {
            "message_type": "MESG",
            "user_id": username,
            "message": message_content,
        }

        response = requests.post(sendbird_api_endpoint, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for status codes >= 400

        message_data = response.json()
        return message_data

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        print(f'Response content: {response.content}')  # Log the response content
        return None
    
    except Exception as e:
        return None


def create_sendbird_customer(sendbird_user_id):
    try:
        sendbird_api_endpoint = f'https://desk-api-{sendbird_app_id}.sendbird.com/platform/v1/customers'
        headers = {
            'Content-Type': 'application/json',
            'SENDBIRDDESKAPITOKEN': desk_api,
        }
        
        payload = {
            'sendbirdId': sendbird_user_id,
        }

        response = requests.post(sendbird_api_endpoint, json=payload, headers=headers)
        response.raise_for_status()  
        
        print(response.json())
        return response.json()
    
    # except requests.exceptions.HTTPError as http_err:
    #     return False
    
    except Exception as e:
        print(f'Error creating Sendbird customer: {e}')
        return False


def create_sendbird_ticket(customer_id,channel_name):
    try:
        sendbird_api_endpoint = f'https://desk-api-{sendbird_app_id}.sendbird.com/platform/v1/tickets'
        headers = {
            'Content-Type': 'application/json',
            'SENDBIRDDESKAPITOKEN': desk_api,
        }

        payload = {
            "channelName": channel_name,
            "customerId": customer_id,
            "groupKey": "cs-team",
        }

        response = requests.post(sendbird_api_endpoint, json=payload, headers=headers)
        response.raise_for_status() 

        ticket_data = response.json()
        print(ticket_data)
        return ticket_data
        
    except requests.exceptions.HTTPError as http_err:
        return None
    
    except Exception as e:
        return None

