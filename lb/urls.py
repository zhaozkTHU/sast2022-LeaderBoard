from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.hello),
    # TODO: Config URL Patterns
    path('leaderboard', views.leaderboard),
    path('history/<slug:user>', views.history),
    path('submit', views.submit),
    path('vote', views.vote)
]