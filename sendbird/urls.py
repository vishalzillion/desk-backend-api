"""
URL configuration for sendbird project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import *
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('admin/', admin.site.urls),
    path("signup/",UserSignupView.as_view(), name="signup"),
    path('create-ticket/', CreateTicketView.as_view(), name='create_ticket'),
    path('tickets/', TicketListView.as_view(), name='ticket-list'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('', UserLoginView.as_view(), name='user_login'),
    path('list-agents/', ListAgentsView.as_view(), name='list_agents'),
    path('tickets/<int:ticket_id>/chat_messages/', TicketChatMessagesView.as_view(), name='ticket_chat_messages'),
]
