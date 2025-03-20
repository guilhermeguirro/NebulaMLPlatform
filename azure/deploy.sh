#!/bin/bash
set -e

# Configuration - Customize these values
RESOURCE_GROUP="nebulaml-rg"
LOCATION="eastus"
REGISTRY_NAME="nebulamlregistry"
ENVIRONMENT_NAME="nebulaml-env"
API_IMAGE_TAG="latest"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${YELLOW}Azure CLI not found. Please install it first.${NC}"
    echo "You can install it using: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi

# Check if logged in to Azure
echo -e "${YELLOW}Checking Azure login status...${NC}"
az account show &> /dev/null || { 
    echo -e "${YELLOW}You are not logged in to Azure. Please log in.${NC}"
    az login 
}

# Create resource group
echo -e "${YELLOW}Creating resource group $RESOURCE_GROUP in $LOCATION...${NC}"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

# Deploy Azure Container Registry
echo -e "${YELLOW}Deploying Azure Container Registry...${NC}"
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "./azure/acr-template.json" \
    --parameters registryName="$REGISTRY_NAME" registryLocation="$LOCATION"

# Get ACR credentials
echo -e "${YELLOW}Getting ACR credentials...${NC}"
ACR_SERVER=$(az acr show --name "$REGISTRY_NAME" --resource-group "$RESOURCE_GROUP" --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name "$REGISTRY_NAME" --resource-group "$RESOURCE_GROUP" --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$REGISTRY_NAME" --resource-group "$RESOURCE_GROUP" --query "passwords[0].value" -o tsv)

# Login to ACR
echo -e "${YELLOW}Logging in to ACR...${NC}"
az acr login --name "$REGISTRY_NAME"

# Build and push API image
echo -e "${YELLOW}Building and pushing API image...${NC}"
docker build -t "$ACR_SERVER/nebulaml-api:$API_IMAGE_TAG" -f Dockerfile .
docker push "$ACR_SERVER/nebulaml-api:$API_IMAGE_TAG"

# Deploy Container Apps environment and API
echo -e "${YELLOW}Deploying Container Apps environment and API...${NC}"
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "./azure/aca-template.json" \
    --parameters \
        environment_name="$ENVIRONMENT_NAME" \
        location="$LOCATION" \
        containerRegistryServer="$ACR_SERVER" \
        containerRegistryUsername="$ACR_USERNAME" \
        containerRegistryPassword="$ACR_PASSWORD" \
        apiImageTag="$API_IMAGE_TAG"

# Get the API URL
API_URL=$(az deployment group show \
    --resource-group "$RESOURCE_GROUP" \
    --name "aca-template" \
    --query "properties.outputs.apiUrl.value" \
    -o tsv)

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}API URL: $API_URL${NC}"
echo -e "${YELLOW}Note: It may take a few minutes for the API to be fully deployed and accessible.${NC}" 