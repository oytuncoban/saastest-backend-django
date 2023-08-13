import csv
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.core import serializers
import datetime

from app.utils import (
    check_api_key,
    check_auth,
    data_json,
    generate_api_key,
    is_authenticated,
    run_discrete_test,
    test_json,
    test_json_brief,
    user_json,
)
from .models import *
from .test_scripts import *
import json
import bcrypt
import random
import string
from django.shortcuts import HttpResponse
from .models import ApiKey
from django.http import JsonResponse


# /api/v1/users
@csrf_exempt
def Users(request):
    if request.user.is_superuser == False:
        return HttpResponse("UnAuthorized", status=401)
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
    if request.user.is_superuser == False:
        return HttpResponse("UnAuthorized", status=401)
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
    if is_authenticated(request) == False:
        return HttpResponse("UnAuthorized", status=401)
    if request.method == "GET":
        try:
            # get tests by user_id
            tests = Test.objects.filter(user=request.user)
            tests = [test_json_brief(test) for test in tests]
        except:
            return HttpResponse("ErrorWhileGetTests", status=500)
        return JsonResponse({'tests': tests}, status=200)
    elif request.method == "POST":
        try:
            raw = json.loads(request.body)
            name = str(raw["name"])
            type = str(raw["type"])
            alpha = str(raw["alpha"])
        except:
            return HttpResponse("requestIsInvalid", status=400)

        try:
            user = User.objects.get(id=request.user.id)
        except:
            return HttpResponse("UserNotFound", status=404)
        try:
            Test(user=user, name=name, type=type, alpha=alpha).save()
        except Exception as e:
            print(e)
            return HttpResponse("ErrorWhileCreateObject", status=500)
    return HttpResponse("200", status=200)


# /api/v1/tests/<int:test_id>
@csrf_exempt
def GetTestById(request, test_id):
    if is_authenticated(request) == False:
        return HttpResponse("UnAuthorized", status=401)
    if request.method == "GET":
        try:
            test = Test.objects.get(id=test_id)
            # check if user is authorized to see this test
            if test.user != request.user:
                return HttpResponse("UnAuthorized", status=401)

            if  test.discretemetricdata_set.count() <= 0:
                return JsonResponse(test_json(test), status=200)

            test_result = None
            if test.type == "discrete" :
                test_data = list([data_json(data) for data in test.discretemetricdata_set.all()])
                test_result = run_discrete_test(test_data, test.alpha)
                test_response = test_json(test, test_data, test_result)
            else:
                # Handle contionus here
                test_response = test_json(test)

        except Exception as error:
            print(error)
            return HttpResponse("TestNotFound", status=404)
        return JsonResponse(test_response, status=200)
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
    if is_authenticated(request):
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


# /api/v1/create_api_key
def CreateApiKey(request):
    if not request.user.is_authenticated:
        return HttpResponse("UnAuthorized", status=401)
    if request.method == "POST":
        prefix, new_token = generate_api_key()

        # Save the generated token to the database
        api_key = ApiKey(key=new_token, prefix=prefix)
        api_key.save()

        return HttpResponse("API Key generated successfully!")

    return HttpResponse("Invalid request method")


# /api/v1/delete_api_key/<str:prefix>
def DeleteApiKey(request, prefix):
    if not request.user.is_authenticated:
        return HttpResponse("UnAuthorized", status=401)
    if request.method == "DELETE":
        try:
            api_key = ApiKey.objects.get(prefix=prefix)
        except:
            return HttpResponse("ApiKeyNotFound", status=404)
        api_key.delete()
        return HttpResponse("200", status=200)
    else:
        return HttpResponse("requestIsInvalid", status=400)


# /api/v1/auth/register
@csrf_exempt
def Register(request):
    if request.method == "POST":
        try:
            raw = json.loads(request.body)
            username = str(raw["username"])
            email = str(raw["email"])
            name = str(raw["name"])
            surname = str(raw["surname"])
            password = str(raw["password"])
        except:
            return HttpResponse("requestIsInvalid", status=400)

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name,
                last_name=surname,
                password=password,
            )
            return HttpResponse(JsonResponse(user_json(user)), status=200)
        except Exception as e:
            print(e)
            return HttpResponse("ErrorWhileCreateObject", status=500)
    return HttpResponse("200", status=200)


# /api/v1/auth/login
@csrf_exempt
def Login(request):
    if request.method != "POST":
        return HttpResponse("requestIsInvalid", status=400)

    raw = json.loads(request.body)
    email = raw["email"]
    password = raw["password"]

    try:
        user = User.objects.get(email=email)
    except Exception as e:
        print(e)
        return HttpResponse("UserNotFound", status=404)

    user_auth = authenticate(request, username=user.username, password=password)
    if user_auth is not None:
        login(request, user)
        return JsonResponse(user_json(user), status=200)
    else:
        return HttpResponse("Incorrect Credentials!", status=401)


# /api/v1/auth/me
def Me(request):
    if request.method != "GET":
        return HttpResponse("Invalid Request", status=405)
    if request.user.is_authenticated != True:
        return HttpResponse("UnAuthorized", status=401)
    try:
        user = User.objects.get(username=request.user.username)
        user = user_json(user)
        return JsonResponse(user, status=200)
    except:
        return HttpResponse("UserNotFound", status=404)


# /api/v1/logout
@csrf_exempt
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponse("Succesfully logged out.", status=200)
    else:
        return HttpResponse("Problem", status=400)


# /api/v1/run_test_discrete
@csrf_exempt
def RunTestDiscrete(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                print(json.loads(request.body))
                raw = json.loads(request.body)
                testId = int(raw["test_id"])
                alpha = float(raw["alpha"])
            except:
                return HttpResponse("requestIsInvalid", status=400)

            try:
                test = Test.objects.get(id=testId)
            except:
                return HttpResponse("TestNotFound", status=404)

            try:
                response_data = run_discrete_test(test)
            except Exception as e:
                print(e)
                return HttpResponse("ErrorWhileCreateObject", status=500)
            return JsonResponse(response_data, status=200)
        else:
            return HttpResponse("requestIsInvalid", status=400)
    return HttpResponse("UnAuthorized", status=401)


# /api/v1/run_test_continuous
@csrf_exempt
def RunTestContinuous(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                raw = json.loads(request.body)
                testId = int(raw["test_id"])
                alpha = int(raw["alpha"])
            except:
                return HttpResponse("requestIsInvalid", status=400)

            try:
                test = Test.objects.get(id=testId)
            except:
                return HttpResponse("TestNotFound", status=404)

            try:
                testdata = list(
                    test.continuousmetricdata_set.sort_by("dateTime").all()
                )  # Get data sorted by date
                df = pd.DataFrame.from_records(testdata)  # Convert to dataframe
                group_a = df[df["variant"] == "A"]["metric"].dropna()
                group_b = df[df["variant"] == "B"]["metric"].dropna()
                t_score = None
                if is_normal(df, group_a, alpha=alpha) and is_normal(
                    df, group_b, alpha=alpha
                ):
                    if check_variances(group_a, group_b):
                        t_score, p_val = perform_t_test(group_a, group_b)
                    else:
                        t_score, p_val = perform_welch_t_test(df)
                else:
                    p_val = perform_mann_whitney_u_test(group_a, group_b)
                    mean_a = np.mean(rankdata(group_a))
                    mean_b = np.mean(rankdata(group_b))
                sample_size = testdata.count()
                response_data = {
                    "data": testdata,
                    "p_val": p_val,
                    "t_score": t_score,  # Only for t-test
                    "sample_size": sample_size,
                    "mean": df["metric"].mean(),
                    "median": df["metric"].median(),
                }
            except Exception as e:
                print(e)
                return HttpResponse("ErrorWhileCreateObject", status=500)
            return JsonResponse(response_data, status=200)
        else:
            return HttpResponse("requestIsInvalid", status=400)
    return HttpResponse("UnAuthorized", status=401)


# /api/v1/tests/<test_id:int>/add_bulk
@csrf_exempt
def AddBulkCSV(request, test_id):
    if request.method not in ["POST","PATCH"]:
        return HttpResponse("Method not Allowed", status=405)

    # Check for authentication
    if not is_authenticated(request):
        return HttpResponse("UnAuthorized", status=401)

    # Check if a file is uploaded
    if "file" not in request.FILES:
        return HttpResponse("No file uploaded!", status=400)

    try:
        test = Test.objects.get(id=test_id)
    except:
        return HttpResponse("TestNotFound", status=404)
    
    if(test.user != request.user):
        return HttpResponse("UnAuthorized", status=401)

    file = request.FILES["file"]
    lines = file.read().splitlines()
    reader = csv.DictReader(line.decode("utf-8") for line in lines)

    if test.type == "discrete":
        data_list = [
            DiscreteMetricData(
                test_id=test.id,
                variant=row["variant"],
                metric=row["metric"],
                date=row["date"],
            )
            for row in reader
        ]

        try:
            DiscreteMetricData.objects.bulk_create(data_list)
        except Exception as e:
            print(e)
            return HttpResponse("ErrorWhileCreateObject", status=500)
    else:
        data_list = [
            ContinuousMetricData(
                test_id=test.id,
                variant=row["variant"],
                metric=row["metric"],
                date=row["date"],
            )
            for row in reader
        ]
        try:
            ContinuousMetricData.objects.bulk_create(data_list)
        except Exception as e:
            print(e)
            return HttpResponse("ErrorWhileCreateObject", status=500)

    return JsonResponse(
        {"message": "Data added successfully.", "status": True}, status=201
    )
