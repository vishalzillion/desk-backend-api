from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
import requests
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate 
from rest_framework import status ,permissions
from .sendbirdapi import *
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from .models import Customer,SendbirdTicket
from rest_framework.decorators import authentication_classes

import os
from dotenv import load_dotenv

load_dotenv()


sendbird_app_id = os.getenv("SENDBIRD_APP_ID")
sendbird_api_key = os.getenv("SENDBIRD_API_KEY")
desk_api = os.getenv("DESK_API")


@authentication_classes([])
class UserSignupView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                sendbird_user_id = create_sendbird_user(user.username)
                if sendbird_user_id:
                    sendbird_customer_response = create_sendbird_customer(user.username)
                    if sendbird_customer_response:
                        sendbird_customer_id = sendbird_customer_response.get("id")
                        if sendbird_customer_id:
                            customer = Customer.objects.create(user=user, sendbird_customer_id=sendbird_customer_id)
                            token, created = Token.objects.get_or_create(user=user)
                            serializer.data.pop("password")
                            return Response({'token': token.key, 'detail': serializer.data}, status=status.HTTP_201_CREATED)
                        
                    return Response({'error': 'Failed to create Sendbird customer'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                   
                return Response({'error': 'Failed to create Sendbird user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        user = request.user
        if user.is_authenticated:
         
            Token.objects.get(user=user).delete()
            logout(request)
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        
        return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

@authentication_classes([])
class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
        
            if user:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': "Token" + token.key})
            
            return Response({'message': 'Unable to log in with provided credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TicketListView(APIView):
    
    def get(self, request):
        headers = {
            'Content-Type': 'application/json',
            'SENDBIRDDESKAPITOKEN': desk_api,

           
        }
        base_url = f"https://desk-api-{sendbird_app_id}.sendbird.com/platform/v1/tickets"
        
        response = requests.get(base_url,headers=headers)
        
        if response.status_code == 200:
            tickets_data = response.json().get('results', [])
            serializer = TicketSerializer(tickets_data, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Failed to fetch tickets'}, status=response.status_code)
        

class CreateTicketView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        user = request.user
        username = user.username
        channel_name = request.data.get("channel_name")
        message_content = request.data.get("message_content")
        ticket_id = request.data.get("ticket_id")  

        sendbird_user_id = user.username
        
    
        customer = Customer.objects.get(user=user)
        sendbird_customer_id = customer.sendbird_customer_id

        if ticket_id:
            specific_ticket = SendbirdTicket.objects.filter(sendbird_customer=customer, ticket_id=ticket_id).first()
            if specific_ticket:
                if not message_content:
                    return Response({'error': 'message_content is required for sending message to ticket'}, status=status.HTTP_400_BAD_REQUEST)
                channel_url = specific_ticket.channel_url
                message_sent = send_message_to_channel(channel_url, username, message_content)
                if message_sent:
                    return Response({'success': 'Message sent to specific ticket'}, status=status.HTTP_201_CREATED)
                
                return Response({'error': 'Failed to send message to specific ticket'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({'error': 'Ticket not found for this customer'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if not channel_name:
                return Response({'error': 'channel_name is required for creating a ticket'}, status=status.HTTP_400_BAD_REQUEST)
            ticket_created = create_sendbird_ticket(sendbird_customer_id, channel_name)
            serializer = TicketSerializer(ticket_created)
            ticket_id = ticket_created.get("id")
            channel_url = ticket_created.get("channelUrl")

            if ticket_id and channel_url:
                SendbirdTicket.objects.create(sendbird_customer=customer, ticket_id=ticket_id, channel_url=channel_url)
                message_sent = send_message_to_channel(channel_url, username, message_content)
                if message_sent:
                    return Response({'success': 'Message sent to specific ticket',"data":ticket_created}, status=status.HTTP_201_CREATED)
                
                return Response({'error': 'Failed to send message to specific ticket'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
            
            return Response({'error': 'Failed to create ticket or obtain channel URL'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            





class ListAgentsView(APIView):
    def get(self, request):

        headers = {
            'Content-Type': 'application/json',
            'SENDBIRDDESKAPITOKEN': desk_api,

           
        }

        params = {
            "limit": 10,  # Adjust the limit as needed
            "offset": 0,  # Adjust the offset as needed for pagination
        }
        base_url = f"https://desk-api-{sendbird_app_id}.sendbird.com/platform/v1/agents"
        try:
            response = requests.get(
                base_url,
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                agent_data = response.json()
                return Response(agent_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to fetch agents'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class TicketChatMessagesView(APIView):
    def get(self, request, ticket_id):
        base_url = f"https://desk-api-{sendbird_app_id}.sendbird.com/platform/v1/tickets/{ticket_id}/chat_messages"
        # Replace {your_application_id} with your actual Sendbird Application ID

        headers = {
            'SENDBIRDDESKAPITOKEN': desk_api,
            'Content-Type': 'application/json'
        }

        params = {
            'limit': request.GET.get('limit', 50),  
            'offset': request.GET.get('offset', 0)  
        }

        try:
            response = requests.get(base_url, headers=headers, params=params)
            if response.status_code == 200:
                chat_messages = response.json()
                return Response(chat_messages)
            else:
                return Response({'error': 'Failed to fetch chat messages'}, status=response.status_code)
        except requests.RequestException as e:
            return Response({'error': f'RequestException: {e}'}, status=500)
