# GitHub Actions for NebulaML Platform Azure Deployment

This directory contains GitHub Actions workflows to automate the deployment of NebulaML Platform to Azure.

## Setting Up Azure Credentials

To deploy to Azure using GitHub Actions, you need to create a service principal and add its credentials to your GitHub repository secrets.

### 1. Create an Azure Service Principal

Run the following command using the Azure CLI:

```bash
az ad sp create-for-rbac --name "nebulaml-github-actions" \
                         --role contributor \
                         --scopes /subscriptions/<subscription-id> \
                         --sdk-auth
```

Replace `<subscription-id>` with your Azure subscription ID.

The command will output a JSON object like this:

```json
{
  "clientId": "<GUID>",
  "clientSecret": "<GUID>",
  "subscriptionId": "<GUID>",
  "tenantId": "<GUID>",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

### 2. Add the Service Principal to GitHub Secrets

1. In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**
2. Click on **New repository secret**
3. Name: `AZURE_CREDENTIALS`
4. Value: Paste the entire JSON output from the previous step
5. Click **Add secret**

## Customizing the Workflow

You can customize the deployment by modifying the environment variables in the workflow file:

- `RESOURCE_GROUP`: Name of the Azure resource group
- `LOCATION`: Azure region for deployment
- `REGISTRY_NAME`: Name of the Azure Container Registry
- `ENVIRONMENT_NAME`: Name of the Container Apps environment
- `API_IMAGE_TAG`: Tag for the Docker image (defaults to the GitHub commit SHA)

## Running the Workflow

The workflow will run automatically when you push to the `main` branch. You can also run it manually:

1. Go to the **Actions** tab in your GitHub repository
2. Select the **Deploy NebulaML to Azure** workflow
3. Click **Run workflow**
4. Choose the branch you want to deploy
5. Click **Run workflow** again

## Workflow Steps

The workflow performs the following steps:

1. Checks out the repository code
2. Logs in to Azure using the service principal credentials
3. Creates an Azure resource group
4. Deploys an Azure Container Registry using ARM templates
5. Builds and pushes the Docker image to the registry
6. Deploys the NebulaML API using Azure Container Apps
7. Outputs the URL of the deployed API 