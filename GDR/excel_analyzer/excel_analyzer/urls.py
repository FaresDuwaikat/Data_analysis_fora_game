"""excel_analyzer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from analysis.views import (
    landing_page,
    voice_game_percentage,
    match_type_analysis,
    voice_chat_frequency,
    most_regular_matchtype,
    voice_chat_streak,
    match_completion_rate,
    queue_waiting_time,
    queue_cancellation_analysis,
)

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('admin/', admin.site.urls),
    path('question1/', voice_game_percentage, name='voice_game_percentage'),
    path('question2/', match_type_analysis, name='match_type_analysis'),
    path('question3/', voice_chat_frequency, name='voice_chat_frequency'),
    path('question4/', most_regular_matchtype, name='most_regular_matchtype'),
    path('question5/', voice_chat_streak, name='voice_chat_streak'),
    path('question6/', match_completion_rate, name='match_completion_rate'),
    path('question7/', queue_waiting_time, name='queue_waiting_time'),
    path('question8/', queue_cancellation_analysis, name='queue_cancellation_analysis'),
]
