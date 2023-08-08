from django.urls import path
from .views import *

app_name="app"

urlpatterns = [
    path("api/v1/add_row_continuous",AddRowContinuous,name='AddRowContinuous'),
    path("api/v1/add_row_discrete",AddRowDiscrete,name='AddRowDiscrete'),
    path("login",Login,name='Login'),
    path("logout",Logout,name='Logout'),
]
