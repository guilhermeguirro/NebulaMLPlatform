# Deploying NebulaML Platform to Azure

This guide provides instructions for deploying the NebulaML Platform to Azure using either ARM templates or Terraform.

## Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Docker](https://docs.docker.com/get-docker/)
- [Terraform](https://www.terraform.io/downloads.html) (only if using Terraform deployment)

## Using the Deployment Script

The easiest way to deploy is using our deployment script:

1. Make the script executable:
   ```bash
   chmod +x ./azure/deploy.sh
   ```

2. Run the script:
   ```bash
   ./azure/deploy.sh
   ```

3. The script will:
   - Create a resource group
   - Deploy an Azure Container Registry
   - Build and push the Docker image
   - Deploy a Container Apps environment with the NebulaML API

4. After deployment completes, the script will output the URL of your API.

## Using Terraform

Alternatively, you can use Terraform:

1. Initialize Terraform:
   ```bash
   cd terraform
   terraform init
   ```

2. Check the plan:
   ```bash
   terraform plan
   ```

3. Apply the configuration:
   ```bash
   terraform apply
   ```

4. After deployment, get the API URL:
   ```bash
   terraform output api_url
   ```

## Manual Deployment

If you prefer to deploy manually:

1. Create a resource group:
   ```bash
   az group create --name nebulaml-rg --location eastus
   ```

2. Deploy the container registry:
   ```bash
   az deployment group create \
     --resource-group nebulaml-rg \
     --template-file ./azure/acr-template.json \
     --parameters registryName=nebulamlregistry
   ```

3. Build and push the image:
   ```bash
   # Login to ACR
   az acr login --name nebulamlregistry

   # Build and push
   docker build -t nebulamlregistry.azurecr.io/nebulaml-api:latest .
   docker push nebulamlregistry.azurecr.io/nebulaml-api:latest
   ```

4. Deploy the Container App:
   ```bash
   # Get ACR credentials
   ACR_SERVER=$(az acr show --name nebulamlregistry --resource-group nebulaml-rg --query loginServer -o tsv)
   ACR_USERNAME=$(az acr credential show --name nebulamlregistry --resource-group nebulaml-rg --query username -o tsv)
   ACR_PASSWORD=$(az acr credential show --name nebulamlregistry --resource-group nebulaml-rg --query "passwords[0].value" -o tsv)

   # Deploy
   az deployment group create \
     --resource-group nebulaml-rg \
     --template-file ./azure/aca-template.json \
     --parameters \
       environment_name=nebulaml-env \
       containerRegistryServer="$ACR_SERVER" \
       containerRegistryUsername="$ACR_USERNAME" \
       containerRegistryPassword="$ACR_PASSWORD"
   ```

## Accessing Your Deployment

Once deployed, you can access:

- API: The URL will be output after deployment
- API Documentation: `<your-api-url>/docs`
- Health Check: `<your-api-url>/health`

## Cleaning Up

To remove all resources:

- Using Azure CLI:
  ```bash
  az group delete --name nebulaml-rg
  ```

- Using Terraform:
  ```bash
  terraform destroy
  ```

## Continuous Deployment with GitHub Actions

This project includes GitHub Actions workflows for continuous deployment to Azure:

### Prerequisites

1. Create an Azure Service Principal:
   ```bash
   az ad sp create-for-rbac --name "nebulaml-github-actions" \
                           --role contributor \
                           --scopes /subscriptions/<subscription-id> \
                           --sdk-auth
   ```

2. Add the service principal credentials to your GitHub repository:
   - Go to your repository's **Settings** > **Secrets and variables** > **Actions**
   - Create a new repository secret named `AZURE_CREDENTIALS`
   - Paste the entire JSON output from the previous command

### Available Workflows

1. **ARM Template Deployment** (.github/workflows/deploy-azure.yml):
   - Triggers on push to main branch or manual dispatch
   - Uses the ARM templates in the azure directory
   - Automatically builds and pushes the Docker image

2. **Terraform Deployment** (.github/workflows/deploy-azure-terraform.yml):
   - Triggers on push to main branch (when terraform directory changes) or manual dispatch
   - Uses the Terraform configuration in the terraform directory
   - Sets up remote state in Azure Storage
   - Builds and pushes the Docker image

To run a workflow manually:
1. Go to the **Actions** tab in your GitHub repository
2. Select the desired workflow
3. Click **Run workflow**
4. Select the branch to deploy
5. Click **Run workflow** 