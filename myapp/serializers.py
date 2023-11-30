from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username","email","password"]
        
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

class CustomerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sendbirdId = serializers.CharField()
   

class TicketSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project = serializers.IntegerField()
    channelName = serializers.CharField()
    customer = CustomerSerializer() 
    

    

class UserLoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        return data 