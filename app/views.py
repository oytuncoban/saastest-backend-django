from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.core import serializers
from .models import *
import json

# Create your views here.


# /api/v1/users
@csrf_exempt
def Users(request):
    if request.method == "GET":
        try:
            users = User.objects.all()
        except:
            return HttpResponse("ErrorWhileGetUsers", status=500)
        return HttpResponse(users, status=200)
    elif request.method == "POST":
        try:
            raw = json.loads(request.body)
            username = str(raw["username"])
            password = str(raw["password"])
        except:
            return HttpResponse("requestIsInvalid", status=400)

        try:
            User.objects.create_user(username=username, password=password)
        except Exception as e:
            print(e)
            return HttpResponse("ErrorWhileCreateObject", status=500)
    return HttpResponse("200", status=200)


# /api/v1/users/<int:user_id>
@csrf_exempt
def Users(request, user_id):
    if request.method == "GET":
        try:
            user = User.objects.get(id=user_id)
        except:
            return HttpResponse("UserNotFound", status=404)
        return HttpResponse(user.username, status=200)
    elif request.method == "DELETE":
        try:
            user = User.objects.get(id=user_id)
        except:
            return HttpResponse("UserNotFound", status=404)
        user.delete()
        return HttpResponse("200", status=200)
    else:
        return HttpResponse("requestIsInvalid", status=400)


# /api/v1/register
@csrf_exempt
def Register(request):
    if request.method == "POST":
        try:
            raw = json.loads(request.body)
            username = str(raw["username"])
            password = str(raw["password"])
        except:
            return HttpResponse("requestIsInvalid", status=400)

        try:
            User.objects.create_user(username=username, password=password)
        except Exception as e:
            print(e)
            return HttpResponse("ErrorWhileCreateObject", status=500)
    return HttpResponse("200", status=200)


# /api/v1/add_row_discrete
@csrf_exempt
def AddRowDiscrete(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                raw = json.loads(request.body)
                testId = int(raw["test_id"])
                variant = str(raw["variant"])
                metric = bytes(raw["metric"], "utf-8")
            except:
                return HttpResponse("requestIsInvalid", status=400)

            try:
                test = Test.objects.get(id=testId)
            except:
                return HttpResponse("TestNotFound", status=404)
            try:
                DiscreteMetricData(test=test, variant=variant, metric=metric).save()
            except Exception as e:
                print(e)
                return HttpResponse("ErrorWhileCreateObject", status=500)
            return HttpResponse("200", status=200)
        else:
            return HttpResponse("requestIsInvalid", status=400)
    return HttpResponse("UnAuthorized", status=401)


# /api/v1/tests
@csrf_exempt
def GetTests(request):
    if request.method == "GET":
        try:
            tests = serializers.serialize("json", Test.objects.all())
        except:
            return HttpResponse("ErrorWhileGetTests", status=500)
        return HttpResponse(tests, status=200)
    elif request.method == "POST":
        try:
            raw = json.loads(request.body)
            userId = int(raw["user_id"])
            name = str(raw["name"])
            type = str(raw["type"])
        except:
            return HttpResponse("requestIsInvalid", status=400)

        try:
            user = User.objects.get(id=userId)
        except:
            return HttpResponse("UserNotFound", status=404)
        try:
            Test(user=user, name=name, type=type).save()
        except Exception as e:
            print(e)
            return HttpResponse("ErrorWhileCreateObject", status=500)
    return HttpResponse("200", status=200)


# /api/v1/tests/<int:test_id>
@csrf_exempt
def GetTestById(request, test_id):
    if request.method == "GET":
        try:
            test = Test.objects.get(id=test_id)
            test = serializers.serialize("json", test)
        except:
            return HttpResponse("TestNotFound", status=404)
        return HttpResponse(test, status=200)
    elif request.method == "DELETE":
        try:
            test = Test.objects.get(id=test_id)
        except:
            return HttpResponse("TestNotFound", status=404)
        test.delete()
        return HttpResponse("200", status=200)
    else:
        return HttpResponse("requestIsInvalid", status=400)


# /api/v1/add_row_continuous
@csrf_exempt
def AddRowContinuous(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                raw = json.loads(request.body)
                testId = int(raw["test_id"])
                variant = str(raw["variant"])
                metric = float(raw["metric"])
            except:
                return HttpResponse("requestIsInvalid", status=400)

            try:
                test = Test.objects.get(id=testId)
            except:
                return HttpResponse("TestNotFound", status=404)
            try:
                ContinuousMetricData(test=test, variant=variant, metric=metric).save()
            except Exception as e:
                print(e)
                return HttpResponse("ErrorWhileCreateObject", status=500)
            return HttpResponse("200", status=200)
        else:
            return HttpResponse("requestIsInvalid", status=400)
    return HttpResponse("UnAuthorized", status=401)


@csrf_exempt
def Login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(request, username=username, password=password)
    if not request.user.is_authenticated:
        if user is not None:
            login(request, user)
            return HttpResponse("logged in", status=200)
        else:
            return HttpResponse("UserNotFound", status=401)
    return HttpResponse("logged in", status=200)


@csrf_exempt
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponse("logged out", status=200)

    return HttpResponse("logged out", status=200)
