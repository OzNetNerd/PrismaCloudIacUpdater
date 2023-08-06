from typing import List, Union
from dataclasses import dataclass, field
from typing import Dict, Any
import requests
from libs.client import PrismaCloudClient


@dataclass
class CloudAccountDetails:
    name: str
    cloudType: str
    accountType: str
    enabled: bool
    lastModifiedTs: int
    lastModifiedBy: str
    storageScanEnabled: bool
    protectionMode: str
    ingestionMode: str
    groups: List[str]
    status: str
    numberOfChildAccounts: int
    accountId: str
    addedOn: int
    groupIds: List[str]
    deploymentType: str
    cloudAccountOwner: str = ""
    cloudAccountOwnerCount: int = 0


@dataclass
class AlibabaCloudAccountTyes:
    Accounts: Union[List, List[CloudAccountDetails]] = field(default_factory=list)


@dataclass
class AwsAccountTyes:
    Accounts: Union[List, List[CloudAccountDetails]] = field(default_factory=list)
    Organizations: Union[List, List[CloudAccountDetails]] = field(default_factory=list)


@dataclass
class AzureAccountTyes:
    Accounts: Union[List, List[CloudAccountDetails]] = field(default_factory=list)
    Tenants: Union[List, List[CloudAccountDetails]] = field(default_factory=list)


@dataclass
class GcpAccountTyes:
    Accounts: Union[List, List[CloudAccountDetails]] = field(default_factory=list)
    Organizations: Union[List, List[CloudAccountDetails]] = field(default_factory=list)
    MasterServiceAccounts: Union[List, List[CloudAccountDetails]] = field(
        default_factory=list
    )


@dataclass
class OciAccountTyes:
    Accounts: Union[List, List[CloudAccountDetails]] = field(default_factory=list)
    Tenants: Union[List, List[CloudAccountDetails]] = field(default_factory=list)


@dataclass
class OnboardedAccounts:
    pc_client: PrismaCloudClient

    def __post_init__(self):

        self.AlibabaCloud = AlibabaCloudAccountTyes()
        self.Aws = AwsAccountTyes()
        self.Azure = AzureAccountTyes()
        self.Gcp = GcpAccountTyes()
        self.Oci = OciAccountTyes()

        _unstructured_cloud_accounts = self._get_unstructured_cloud_accounts()
        self._get_cloud_accounts(_unstructured_cloud_accounts)

    def _get_unstructured_cloud_accounts(self) -> Dict[str, Any]:
        url = f"{self.pc_client.auth_details.base_api_url}/cloud"
        payload = {}
        response = requests.request(
            "GET", url, headers=self.pc_client.auth_details.headers, data=payload
        )
        unstructured_cloud_accounts = response.json()

        return unstructured_cloud_accounts

    def _get_cloud_accounts(self, unstructured_cloud_accounts: Dict[str, Any]) -> None:
        for cloud_account in unstructured_cloud_accounts:
            cloud_account_details_object = self._get_cloud_account_details_object(
                cloud_account
            )
            cloud_type = cloud_account_details_object.cloudType.capitalize()
            get_account_type = cloud_account_details_object.accountType

            if get_account_type == "masterServiceAccount":
                account_type = "MasterServiceAccounts"
            else:
                account_type = f"{get_account_type.capitalize()}s"

            if cloud_type == "Alibaba_cloud":
                cloud_object_name = "AlibabaCloud"

            else:
                cloud_object_name = cloud_account_details_object.cloudType.capitalize()

            cloud_object = getattr(self, cloud_object_name)
            getattr(cloud_object, account_type).append(cloud_account_details_object)

        return

    def _get_cloud_account_details_object(self, cloud_account) -> CloudAccountDetails:
        cloud_account_details_object = CloudAccountDetails(**cloud_account)

        return cloud_account_details_object
