Commands executed:
```
  az group create --name rg-jbrooker --location "westus2"
  az storage account create --name jbrooker
  az functionapp create --name timecard-jbrooker --resource-group rg-jbrooker --storage-account jbrooker --consumption-plan-location "westus2" --runtime "python" --runtime-version "3.9" --os-type Linux
  ```