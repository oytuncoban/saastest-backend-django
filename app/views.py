import csv
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.core import serializers

from app.utils import check_api_key, check_auth, generate_api_key, is_authenticated
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
    if is_authenticated(request) == False:
        return HttpResponse("UnAuthorized", status=401)
    if request.method == "GET":
        try:
            # get tests by user_id
            tests = Test.objects.filter(user=request.user)
            tests = serializers.serialize("json", tests)
        except:
            return HttpResponse("ErrorWhileGetTests", status=500)
        return HttpResponse(tests, status=200)
    elif request.method == "POST":
        try:
            raw = json.loads(request.body)
            userId = int(raw["user_id"])
            name = str(raw["name"])
            type = str(raw["type"])
            alpha = str(raw["alpha"])
        except:
            return HttpResponse("requestIsInvalid", status=400)

        try:
            user = User.objects.get(id=userId)
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
    if(is_authenticated(request) == False):
        return HttpResponse("UnAuthorized", status=401)
    if request.method == "GET":
        try:
            test = Test.objects.get(id=test_id)
            # check if user is authorized to see this test
            if test.user != request.user:
                return HttpResponse("UnAuthorized", status=401)
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



# /api/v1/create_api_key
def CreateApiKey(request):
    if not request.user.is_authenticated:
        return HttpResponse("UnAuthorized", status=401)
    if request.method == "POST":
        prefix, new_token= generate_api_key()

        # Save the generated token to the database
        api_key = ApiKey(key=new_token, prefix=prefix)
        api_key.save()

        return HttpResponse("API Key generated successfully!")

    return HttpResponse("Invalid request method")


# /api/v1/delete_api_key/<str:prefix>
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



# /api/v1/login
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


# /api/v1/logout
@csrf_exempt
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponse("logged out", status=200)

    return HttpResponse("logged out", status=200)

# /api/v1/run_test_discrete
@csrf_exempt
def RunTestDiscrete(request):
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
                testdata = list(test.discretemetricdata_set.sort_by("dateTime").all()) # Get data sorted by date
                df= pd.DataFrame.from_records(testdata) # Convert to dataframe
                contingency_table = pd.crosstab(df['variant'], df['metric']) # Create contingency table
                all_cells_greater_than_5 = (contingency_table > 5).all().all() # Check if all cells are greater than 5
                if all_cells_greater_than_5:
                    p_val=chi_square_test(contingency_table)
                else:
                    p_val=fisher_pval(contingency_table)


                sample_size =testdata.count()
                conversion_rates = contingency_table[1] / contingency_table.sum(axis=1) * 100
                response_data = {
                    'data':testdata,
                    'p_val':p_val,
                    'sample_size':sample_size,
                    'conv_rate_a':conversion_rates['A'],
                    'conv_rate_b':conversion_rates['B'],
                    'mean':df['metric'].mean(),
                    'median':df['metric'].median(),
                }
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
                testdata = list(test.continuousmetricdata_set.sort_by("dateTime").all()) # Get data sorted by date
                df= pd.DataFrame.from_records(testdata) # Convert to dataframe
                group_a = df[df['variant'] == 'A']['metric'].dropna()
                group_b = df[df['variant'] == 'B']['metric'].dropna()
                if is_normal(df,group_a,alpha=alpha) and is_normal(df,group_b,alpha=alpha):
                    p_val = perform_welch_t_test(df)
                else:
                    p_val = perform_mann_whitney_u_test(df)
                sample_size =testdata.count()
                response_data = {
                    'data':testdata,
                    'p_val':p_val,
                    'sample_size':sample_size,
                    'mean':df['metric'].mean(),
                    'median':df['metric'].median(),
                }
            except Exception as e:
                print(e)
                return HttpResponse("ErrorWhileCreateObject", status=500)
            return JsonResponse(response_data, status=200)
        else:
            return HttpResponse("requestIsInvalid", status=400)
    return HttpResponse("UnAuthorized", status=401)


# /api/v1/add_continous_bulk
@csrf_exempt
def AddContinousBulk(request):
    # Check for authentication
    if not is_authenticated(request):
        return HttpResponse("UnAuthorized", status=401)


    # Check if a file is uploaded
    if 'file' not in request.FILES:
        return HttpResponse("No file uploaded!", status=400)


    if request.method == "POST" or request.method == "PATCH":
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        data_list = [ContinuousMetricData(test_id=row['test_id'], variant=row['variant'], metric=row['metric']) for row in reader]
        ContinuousMetricData.objects.bulk_create(data_list)

        return JsonResponse({"message": "Data added successfully."}, status=201)
    # return internal server error HttpResponse
    return HttpResponse("Internal Server Error", status=500)

# /api/v1/add_discrete_bulk
@csrf_exempt
def AddDiscreteBulk(request):
    # Check for authentication
    if not is_authenticated(request):
        return HttpResponse("UnAuthorized", status=401)


    # Check if a file is uploaded
    if 'file' not in request.FILES:
        return HttpResponse("No file uploaded!", status=400)

    if request.method == "POST" or request.method == "PATCH":

        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        data_list = [DiscreteMetricData(test_id=row['test_id'], variant=row['variant'], metric=row['metric']) for row in reader]
        DiscreteMetricData.objects.bulk_create(data_list)

        return JsonResponse({"message": "Data added successfully."}, status=201)
    return HttpResponse("Internal Server Error", status=500)
