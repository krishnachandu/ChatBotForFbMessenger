# MyFirstChatBot/fb_MyFirstChatBot/urls.py
from django.conf.urls import include, url
from .views import MyFirstChatBotView

from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
                  url(r'^66d2/?$', MyFirstChatBotView.as_view(),name='MyFirstChatBotView')
               ]