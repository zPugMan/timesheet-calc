# Azure Setup

## Initial Creation
Commands executed:
```
az login
az group create --name rg-jbrooker --location "westus2"
az storage account create --name jbrooker
az functionapp create --name timecard-jbrooker --resource-group rg-jbrooker --storage-account jbrooker --consumption-plan-location "westus2" --runtime "python" --runtime-version "3.9" --os-type Linux
```

The above creates the objects to support the Azure function.

### Azure Vault
To setup secrets using Azure Vault services:
* Create a dedicated Managed Identity
* Create a vault
* Add 2 access policies for the vault
  * Full permissions to get & create keys and secrets
  * Secret "GET" permission only, which is assigned to the Managed Identity previously created
* Modify the Azure Function created to explicitly add a user-assigned identity. This is the Managed Identity previously created that has "GET" permissions to the vault.

Once the secrets are defined, they can be surfaced as environment variables.

### Github Action
Deployment from Github to Azure relies on a secret unique to the Azure function.

To retrieve the secret for deployment:
* Navigate to the Azure Function App
* Under Overview, retrieve the _Get Publish Profile_. This is an XML file that is then referenced by Github.
* Open the downloaded file and copy the contents.

To set the secret for deployment workflow actions:
* In the Github repository, navigate to: Security / Secrets and variables / Actions
* Set the repository secret: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` to the value copied earlier