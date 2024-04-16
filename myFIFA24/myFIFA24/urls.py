"""
URL configuration for myFIFA24 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from app import views
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path('', views.players_view, name='players'),
    path('players/', views.players_view, name='players'),
    path('player/<str:guid>/', views.player_view, name='player'),
    path('leagues/', views.leagues_view, name='leagues'),
    path('league/<str:guid>/', views.league_view, name='league'),
    path('team/<str:guid>/', views.team_view, name='team'),
    path('squad/', views.squad_view, name='squad'),

]