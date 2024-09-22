# helloapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('emotion/', views.emotion, name='emotion'),
]
