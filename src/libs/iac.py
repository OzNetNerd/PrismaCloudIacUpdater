from typing import List
import os
from libs.client import PrismaCloudClient
from libs.accounts import CloudAccountDetails
import requests


def create_iac_files(
    pc_client: PrismaCloudClient, accounts: List[CloudAccountDetails], features: list, output_dir
) -> None:
    account_type = accounts[0].accountType
    cloud_type = accounts[0].cloudType
    api_endpoint = f"{cloud_type}_template"
    url = f"{pc_client.auth_details.base_api_url}/cas/v1/{api_endpoint}"

    for account in accounts:
        payload = {
            "accountType": account_type,
            "features": features,
        }

        if cloud_type == "aws":
            payload["accountId"] = account.accountId

        elif cloud_type == "azure":
            if account_type == "account":
                payload["subscriptionId"] = account.name

            elif account_type == "tenant":
                payload["tenantId"] = account.name

        response = requests.request(
            "POST", url, headers=pc_client.auth_details.headers, json=payload
        )

        filename = f'{output_dir}{os.sep}{cloud_type}-{account_type}-{account.accountId}.json'

        _write_iac_to_file(response.content, filename)

def _write_iac_to_file(iac, filename):
    print(f"Creating {filename}")
    with open(filename, "wb") as f:
        f.write(iac)