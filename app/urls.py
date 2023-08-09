from django.urls import path
from .views import *

app_name = "app"

urlpatterns = [
    path("api/v1/register", Register, name="Register"),
    path("api/v1/login", Login, name="Login"),
    path("api/v1/logout", Logout, name="Logout"),
    path("api/v1/tests", GetTests, name="GetTests"),
    path("api/v1/tests/<test_id>", GetTestById, name="GetTestById"),
    path("api/v1/add_row_continuous", AddRowContinuous, name="AddRowContinuous"),
    path("api/v1/add_row_discrete", AddRowDiscrete, name="AddRowDiscrete"),
    path("api/v1/run_test_discrete", RunTestDiscrete, name="RunTestDiscrete"),
    path("api/v1/run_test_continuous", RunTestContinuous, name="RunTestContinuous"),
]

