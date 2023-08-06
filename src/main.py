import os
import requests

from libs.client import get_prisma_cloud_client
from libs.accounts import OnboardedAccounts
from libs.features import PrismaCloudFeatures
from libs.iac import create_iac_files


from urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def main():
    pc_client = get_prisma_cloud_client()
    Features = PrismaCloudFeatures(pc_client)

    # Obtain the list of features which are supported for the account type you want to update
    features = list(Features.AzureFeatures.Account)

    # Remove the features you don't want to enable
    features.remove("Remediation")

    # Obtain all of your onboarded accounts
    Onboarded = OnboardedAccounts(pc_client)

    # Obtain the specific cloud & account type you're looking for:
    azure_accounts = Onboarded.Azure.Tenants

    # Specify the output directory
    current_dir = os.path.abspath(os.getcwd())
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    output_dir = os.sep.join([parent_dir, "iac"])
    os.makedirs(output_dir, exist_ok=True)

    # Generate the IAC files
    create_iac_files(pc_client, azure_accounts, features, output_dir)


if __name__ == "__main__":
    main()
