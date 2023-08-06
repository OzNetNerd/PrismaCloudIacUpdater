from dataclasses import dataclass
from typing import AnyStr, Union, Tuple
from collections import namedtuple
import os
import sys
import requests

AuthDetails = namedtuple("AuthDetails", ["base_api_url", "headers"])


@dataclass
class PrismaCloudClient:
    auth_details: AuthDetails


def _get_env_vars(env_var_key: AnyStr, custom_error_message: str) -> str:
    try:
        env_var = os.environ[env_var_key]

    except KeyError:
        sys.exit(
            f'Error: Please define the "{env_var_key}" environment variable. {custom_error_message}'
        )

    print(f"Successfully retrieved {env_var_key} environment variable")

    return env_var


def _get_base_api_url() -> str:
    env_var_key = "PRISMA_CLOUD_API_URL"
    custom_error_message = (
        "Please see https://prisma.pan.dev/api/cloud/api-urls/ for more information."
    )

    base_api_url = _get_env_vars(env_var_key, custom_error_message)

    return base_api_url


def _get_api_creds() -> Union[Tuple, str]:
    prisma_cloud_access_key = "PRISMA_CLOUD_ACCESS_KEY"
    prisma_cloud_secret_key = "PRISMA_CLOUD_SECRET_KEY"

    custom_error_message = "Please see https://docs.paloaltonetworks.com/prisma/prisma-cloud/prisma-cloud-admin-code-security/get-started/generate-access-keys for more information."

    api_creds = {
        "username": _get_env_vars(prisma_cloud_access_key, custom_error_message),
        "password": _get_env_vars(prisma_cloud_secret_key, custom_error_message),
    }

    return api_creds


def _get_auth_header(base_api_url: str, api_creds: dict) -> dict:
    login_url = f"{base_api_url}/login"

    get_response = requests.post(
        login_url,
        headers={"content-type": "application/json", "charset": "UTF-8"},
        json=api_creds,
        verify=False,
    )

    response = get_response.json()

    if get_response.status_code != 200:
        error_message = response["message"]
        sys.exit(
            f"Error: {error_message}. Please check your API credentials and ensure you're using the correct API URL: https://prisma.pan.dev/api/cloud/api-urls/"
        )

    api_token = response["token"]
    auth_header = {"x-redlock-auth": api_token}

    return auth_header


def get_prisma_cloud_client() -> AuthDetails:
    base_api_url = _get_base_api_url()
    api_creds = _get_api_creds()
    auth_header = _get_auth_header(base_api_url, api_creds)

    auth_details = AuthDetails(base_api_url, auth_header)
    pc_client = PrismaCloudClient(auth_details)

    return pc_client
