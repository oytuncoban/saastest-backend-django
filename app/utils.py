import random
import string
import uuid

import pandas as pd

from app.models import ApiKey
from app.test_scripts import chi_square_test, fisher_pval


def generate_api_key():
    # Generate a random prefix of 7 characters
    prefix = "".join(random.choices(string.ascii_letters, k=7))

    # Generate a UUID as the main part of the key
    key = str(uuid.uuid4())

    # Combine prefix and key
    token = f"{prefix}.{key}"

    return (
        prefix,
        token,
    )  # We return both the prefix and the token for easier assignment in the model


def is_authenticated(request):
    api_key = request.headers.get("X-Api-Key")
    is_api_key_valid = check_api_key(api_key)
    is_authenticated = check_auth(request.user.is_authenticated, is_api_key_valid)
    return is_authenticated


def check_api_key(api_key):
    # Get the API key from the request
    if api_key is None:
        return False
    else:
        # Split the API key into prefix and key
        prefix, key = api_key.split(".")

        # Check if the prefix exists in the database
        try:
            api_key = ApiKey.objects.get(prefix=prefix)
        except:
            return False

        # Check if the key matches
        if api_key.key == key:
            return True
        else:
            return False


def check_auth(is_user_authenticated, is_api_key_valid):
    if is_user_authenticated or is_api_key_valid:
        return True
    else:
        return False


def user_json(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }


def test_json(test, test_data = [], test_result = {}):
    return {
        "id": test.id,
        "name": test.name,
        "user": user_json(test.user),
        "type": test.type,
        "alpha": test.alpha,
        "data": test_data,
        "testResults": test_result,
    }

def test_json_brief(test):
    return {
        "id": test.id,
        "name": test.name,
        "user": user_json(test.user),
        "type": test.type,
        "alpha": test.alpha,
    }
    
def data_json(data):
    return {
        "id": data.id,
        "testId": data.test.id,
        "variant": data.variant,
        "metric": data.metric,
        "dateTime": data.date,
    }

def run_discrete_test(test_data, alpha: float):
    df = pd.DataFrame(test_data)  # Convert to dataframe
    contingency_table = pd.crosstab(
        df["variant"], df["metric"]
    )  # Create contingency table
    all_cells_greater_than_5 = (
        (contingency_table > 5).all().all()
    )  # Check if all cells are greater than 5
    if all_cells_greater_than_5:
        p_val = chi_square_test(contingency_table)
    else:
        p_val = fisher_pval(contingency_table)

    conversion_rates = contingency_table[1] / contingency_table.sum(axis=1)
    n_A = contingency_table.sum(axis=1)['A']
    n_B = contingency_table.sum(axis=1)['B']
    variance_a = (
        conversion_rates["A"]
        * (1 - conversion_rates["A"])
    )
    variance_b = (
        conversion_rates["B"]
        * (1 - conversion_rates["B"])
    )
    sample_size = len(test_data)
    response_data = {
        "A": {
            "variance": variance_a * 100,
            "conversionRate": conversion_rates["A"] * 100,
        },
        "B": {
            "variance": variance_b * 100,
            "conversionRate": conversion_rates["B"] * 100,
        },
        "alpha": alpha,
        "significance": p_val,
        "sampleSize": sample_size,
        "mean": df["metric"].mean(),
        "median": df["metric"].median(),
    }

    return response_data
