from dataclasses import dataclass, field
import requests
from libs.client import PrismaCloudClient


"""
account, organization - cloud_type: aws
account, organization, masterServiceAccount - cloud_type: gcp
account, tenant - cloud_type: azure
"""


@dataclass
class AwsFeatures:
    Account: list = field(default_factory=list)
    Organization: list = field(default_factory=list)


@dataclass
class AzureFeatures:
    Account: list = field(default_factory=list)
    Tenant: list = field(default_factory=list)


@dataclass
class GcpFeatures:
    Account: list = field(default_factory=list)
    Organization: list = field(default_factory=list)
    MasterServiceAccount: list = field(default_factory=list)


@dataclass
class PrismaCloudFeatures:
    def __init__(self, pc_client: PrismaCloudClient):
        self.pc_client = pc_client
        self.AwsFeatures = AwsFeatures()
        self.AzureFeatures = AzureFeatures()
        self.GcpFeatures = GcpFeatures()

        self.account_type_map = {
            "aws": {
                "account_types": ["Account", "Organization"],
                "feature_class": self.AwsFeatures,
            },
            "azure": {
                "account_types": ["Account", "Tenant"],
                "feature_class": self.AzureFeatures,
            },
            "gcp": {
                "account_types": ["Account", "Organization", "MasterServiceAccount"],
                "feature_class": self.GcpFeatures,
            },
        }

        for cloud_type, settings in self.account_type_map.items():
            self._get_cloud_features(cloud_type, settings)

    def _get_cloud_features(self, cloud_type, settings):
        for account_type in settings["account_types"]:
            # print(cloud_type, account_type)
            payload = {
                "deploymentType": cloud_type.lower(),
                "accountType": account_type.lower(),
            }
            url = f"{self.pc_client.auth_details.base_api_url}/cas/v1/features/cloud/{cloud_type}"
            response = requests.request(
                "POST", url, headers=self.pc_client.auth_details.headers, json=payload
            ).json()

            try:
                supported_features = sorted(response["supportedFeatures"])

            except KeyError:
                continue

            cloud_feature_object = self.account_type_map[cloud_type]["feature_class"]
            setattr(cloud_feature_object, account_type, supported_features)

        return
