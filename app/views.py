from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import *
import json

# Create your views here.

# /api/v1/add_row_discrete
@csrf_exempt
def AddRowDiscrete(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                raw       =   json.loads(request.body)
                testId    =   int(raw['test_id'])
                variant   =   str(raw['variant'])
                metric    =   bytes(raw['metric'],'utf-8')
            except:
                return HttpResponse("requestIsInvalid",status=400)

            try:
                test = Test.objects.get(id = testId)
            except:
                return HttpResponse("TestNotFound",status=404)
            try:
                DiscreteMetricData(test = test, variant = variant, metric = metric).save()
            except Exception as e:
                print(e)
                return HttpResponse("ErrorWhileCreateObject",status=500)
            return HttpResponse("200",status=200)
        else:
            return HttpResponse("requestIsInvalid",status=400)
    return HttpResponse("UnAuthorized",status=401)


# /api/v1/add_row_continuous
@csrf_exempt
def AddRowContinuous(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                raw       =   json.loads(request.body)
                testId    =   int(raw['test_id'])
                variant   =   str(raw['variant'])
                metric    =   float(raw['metric'])
            except:
                return HttpResponse("requestIsInvalid",status=400)

            try:
                test = Test.objects.get(id = testId)
            except:
                return HttpResponse("TestNotFound",status=404)
            try:
                ContinuousMetricData(test = test, variant = variant, metric = metric).save()
            except Exception as e:
                print(e)
                return HttpResponse("ErrorWhileCreateObject",status=500)
            return HttpResponse("200",status=200)
        else:
            return HttpResponse("requestIsInvalid",status=400)
    return HttpResponse("UnAuthorized",status=401)
    

@csrf_exempt
def Login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(request, username=username, password=password)
    if not request.user.is_authenticated:
        if user is not None:
            login(request, user)
            return HttpResponse("logged in",status=200)
        else:
            return HttpResponse("UserNotFound",status=401)
    return HttpResponse("logged in",status=200)
    

@csrf_exempt
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponse("logged out",status=200)

    return HttpResponse("logged out",status=200)

    