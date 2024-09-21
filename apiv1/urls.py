# helloapp/urls.py
from django.urls import path
from .views import HelloWorldAPIView
from . import views

urlpatterns = [
    path('hello/', HelloWorldAPIView.as_view(), name='hello-world'),
    path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
]
