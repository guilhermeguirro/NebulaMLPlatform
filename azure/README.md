# Deploying NebulaML Platform to Azure

This guide provides instructions for deploying the NebulaML Platform to Azure using GitHub Actions.

## Prerequisites

- GitHub repository with the NebulaML Platform code
- Azure subscription
- Azure service principal with required permissions

## Setup

1. Create an Azure Service Principal:
   ```bash
   az ad sp create-for-rbac --name "NebulaMLPlatform" --role contributor --scopes /subscriptions/<subscription-id> --sdk-auth
   ```

2. Add the following secrets to your GitHub repository (Settings → Secrets and Variables → Actions):
   - `AZURE_CLIENT_ID`: The client ID from the service principal
   - `AZURE_TENANT_ID`: The tenant ID from the service principal
   - `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID

## Deployment

The deployment is automated using GitHub Actions and will be triggered by:
1. Pushing changes to the main branch that affect:
   - `azure/**`
   - `Dockerfile`
   - `app/**`
   - `services/**`
   - `.github/workflows/deploy-azure.yml`
2. Manual trigger through GitHub Actions UI

## Resources Created

The deployment will create the following Azure resources:
1. Resource Group
2. Azure Key Vault
3. Azure Container Registry
4. Azure Container Apps Environment
5. Application Insights
6. Log Analytics Workspace

## Environment Variables

The deployment uses the following environment variables:
- `RESOURCE_GROUP`: nebulaml-platform-rg
- `LOCATION`: eastus
- `REGISTRY_NAME`: nebulamlplatform
- `ENVIRONMENT_NAME`: nebulaml-env
- `KEY_VAULT_NAME`: nebulaml-platform-kv

## Monitoring

The deployment includes:
- Application Insights integration
- Log Analytics workspace
- Container Apps monitoring

## Security

- Secrets are stored in Azure Key Vault
- Service principal has minimal required permissions
- Container registry access is secured
- HTTPS endpoints are automatically configured 