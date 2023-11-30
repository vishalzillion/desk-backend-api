from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sendbird_customer_id = models.CharField(max_length=100)  
    
    def __str__(self):
        return f"Customer: {self.user.username}"

class SendbirdTicket(models.Model):
    sendbird_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    ticket_id = models.CharField(max_length=100)
    channel_url = models.URLField(null=True)
    
    def __str__(self):
        return f"Sendbird Ticket ID: {self.ticket_id} for Customer: {self.sendbird_customer.user.username}"
