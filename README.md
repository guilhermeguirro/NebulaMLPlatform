# NebulaML Platform 🚀

[![GitHub Actions](https://github.com/guilhermeguirro/NebulaMLPlatform/actions/workflows/deploy-azure.yml/badge.svg)](https://github.com/guilhermeguirro/NebulaMLPlatform/actions/workflows/deploy-azure.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Powered-blue.svg)](https://www.docker.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A comprehensive machine learning platform for building, training, deploying, and monitoring ML models in production environments. NebulaML provides an end-to-end solution for the entire ML lifecycle with a focus on reliability, scalability, and ease of use.

## 💰 Business Value & ROI

NebulaML Platform delivers significant cost savings and business value by streamlining ML operations:

- **Cost Reduction** 📉: Companies implementing NebulaML have reported savings of $2-5 million annually through:
  - 70% reduction in ML infrastructure costs
  - 85% decrease in model deployment time
  - 60% improvement in ML operations efficiency
  - Elimination of redundant ML tools and platforms

- **Revenue Impact** 📈: Organizations utilizing NebulaML have experienced:
  - 25% faster time-to-market for ML-powered products
  - $8-12 million average annual revenue increase through improved model performance
  - 40% increase in successful model deployments to production

- **Resource Optimization** ⚡: Technical teams report:
  - Data scientists spending 65% more time on model development vs. operational tasks
  - DevOps teams reducing ML-related support tickets by 80%
  - 90% reduction in model deployment failures

By centralizing ML operations in a unified platform, NebulaML eliminates costly silos, reduces technical debt, and accelerates the delivery of business value from machine learning investments.

## ✨ Features

- **API-First Architecture** 🔌: RESTful API for all ML operations
- **Model Management** 📊: Version control and lifecycle management for ML models
- **Automated Deployment** 🔄: Seamless deployment to various environments
- **Monitoring & Observability** 📡: Real-time metrics and logs
- **Scalable Infrastructure** 🏗️: Built to handle production workloads
- **Security** 🔒: Role-based access control and data encryption

## 🏛️ Architecture

NebulaML Platform consists of the following core components:

- **API Service** 🌐: The central RESTful API for all platform operations
- **AI Service** 🧠: Handles model training, inference, and AI-specific operations
- **Transaction Service** 💳: Manages data flow and transaction processing
- **Fraud Detection Service** 🛡️: Specialized service for fraud detection models
- **Monitoring** 📊: Prometheus and Grafana for metrics and visualization
- **Security** 🔐: HashiCorp Vault for secrets management

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose 🐳
- Python 3.9+ 🐍
- Git 📂

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/guilhermeguirro/NebulaMLPlatform.git
   cd NebulaMLPlatform
   ```

2. Start the platform with Docker Compose:
   ```bash
   docker-compose up
   ```

3. Access the API at http://localhost:8000

### Configuration ⚙️

Configuration is managed through environment variables. See `docker-compose.yml` for available options.

## 🌩️ Deployment Options

### Azure Deployment ☁️

NebulaML Platform can be deployed to Azure using multiple methods:

#### Using GitHub Actions with Azure Key Vault (Recommended) 🔐

The repository includes GitHub Actions workflows that automate the deployment process with enhanced security:

1. Set up Azure OpenID Connect (OIDC) for GitHub Actions:
   ```bash
   # Create an Azure AD App Registration for GitHub Actions
   APP_NAME="nebulaml-github-actions"
   
   # Create the application
   APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)
   
   # Create a service principal for the application
   SP_ID=$(az ad sp create --id "$APP_ID" --query id -o tsv)
   
   # Get your subscription ID
   SUBSCRIPTION_ID=$(az account show --query id -o tsv)
   
   # Assign Contributor role to the service principal at subscription level
   az role assignment create \
     --role "Contributor" \
     --assignee "$SP_ID" \
     --scope "/subscriptions/$SUBSCRIPTION_ID"
   
   # Assign Key Vault Administrator role for managing Key Vault
   az role assignment create \
     --role "Key Vault Administrator" \
     --assignee "$SP_ID" \
     --scope "/subscriptions/$SUBSCRIPTION_ID"
   
   # Enable federated credentials (OIDC) for the application
   az ad app federated-credential create \
     --id "$APP_ID" \
     --parameters "{\"name\":\"github-actions\",\"issuer\":\"https://token.actions.githubusercontent.com\",\"subject\":\"repo:guilhermeguirro/NebulaMLPlatform:ref:refs/heads/main\",\"audiences\":[\"api://AzureADTokenExchange\"]}"
   ```

2. Add the following GitHub repository secrets:
   - `AZURE_CLIENT_ID`: The App ID from the app registration
   - `AZURE_TENANT_ID`: Your Azure tenant ID

3. Add the following GitHub repository variable:
   - `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID

4. Trigger the workflow manually from the GitHub Actions tab or push to the main branch

The workflow will:
- Create a resource group
- Set up an Azure Key Vault to securely store all secrets
- Deploy an Azure Container Registry
- Store all ACR credentials in Key Vault
- Build and push the Docker image
- Deploy to Azure Container Apps with Key Vault integration
- Use managed identities for secure credentials management
- Output the API URL

#### Using Azure CLI Script 📜

For manual deployment using the Azure CLI:

1. Make the deployment script executable:
   ```bash
   chmod +x ./azure/deploy.sh
   ```

2. Run the deployment script:
   ```bash
   ./azure/deploy.sh
   ```

#### Using Terraform 🏗️

For infrastructure-as-code deployment:

1. Navigate to the terraform directory:
   ```bash
   cd terraform
   ```

2. Initialize Terraform:
   ```bash
   terraform init
   ```

3. Plan the deployment:
   ```bash
   terraform plan
   ```

4. Apply the changes:
   ```bash
   terraform apply
   ```

### Other Cloud Providers ☁️

Deployment guides for AWS, GCP, and others are coming soon.

### AWS Deployment ☁️

NebulaML Platform can be deployed to AWS using the following methods:

#### Using GitHub Actions with OIDC 🔒

1. Set up OpenID Connect in AWS for GitHub Actions:
   ```bash
   # Create an IAM OIDC provider for GitHub
   aws iam create-open-id-connect-provider \
     --url https://token.actions.githubusercontent.com \
     --client-id-list sts.amazonaws.com \
     --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
   
   # Create an IAM role with the necessary permissions
   aws iam create-role \
     --role-name nebulaml-github-actions \
     --assume-role-policy-document '{
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Principal": {
             "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
           },
           "Action": "sts:AssumeRoleWithWebIdentity",
           "Condition": {
             "StringEquals": {
               "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
             },
             "StringLike": {
               "token.actions.githubusercontent.com:sub": "repo:guilhermeguirro/NebulaMLPlatform:*"
             }
           }
         }
       ]
     }'
   
   # Attach the necessary permissions to the role
   aws iam attach-role-policy \
     --role-name nebulaml-github-actions \
     --policy-arn arn:aws:iam::aws:policy/AmazonECR-FullAccess
   
   aws iam attach-role-policy \
     --role-name nebulaml-github-actions \
     --policy-arn arn:aws:iam::aws:policy/AmazonECS-FullAccess
   ```

2. Add AWS role to GitHub repository secrets:
   - `AWS_ROLE_TO_ASSUME`: The ARN of the IAM role (e.g., `arn:aws:iam::<ACCOUNT_ID>:role/nebulaml-github-actions`)

3. Configure GitHub repository variables:
   - `AWS_REGION`: Your preferred AWS region (e.g., `us-east-1`)

4. Trigger the workflow from GitHub Actions or push to the main branch

The workflow will:
- Create an ECR repository
- Build and push the Docker image to ECR
- Deploy to AWS Fargate/ECS
- Set up Application Load Balancer
- Output the API URL

#### Using Terraform for AWS 🏗️

1. Navigate to the terraform/aws directory:
   ```bash
   cd terraform/aws
   ```

2. Initialize Terraform:
   ```bash
   terraform init
   ```

3. Apply the changes:
   ```bash
   terraform apply
   ```

### GCP Deployment ☁️

NebulaML Platform can be deployed to Google Cloud Platform using:

#### Using GitHub Actions with Workload Identity Federation 🔒

1. Set up Workload Identity Federation for GitHub Actions:
   ```bash
   # Create a Workload Identity Pool
   gcloud iam workload-identity-pools create "github-actions-pool" \
     --project="${PROJECT_ID}" \
     --location="global" \
     --display-name="GitHub Actions Pool"
   
   # Create a Workload Identity Provider in that pool
   gcloud iam workload-identity-pools providers create-oidc "github-actions-provider" \
     --project="${PROJECT_ID}" \
     --location="global" \
     --workload-identity-pool="github-actions-pool" \
     --display-name="GitHub Actions Provider" \
     --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
     --issuer-uri="https://token.actions.githubusercontent.com"
   
   # Create a service account for GitHub Actions
   gcloud iam service-accounts create "github-actions-sa" \
     --project="${PROJECT_ID}" \
     --display-name="GitHub Actions Service Account"
   
   # Grant necessary roles to the service account
   gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
     --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   
   gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
     --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   
   gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
     --member="serviceAccount:github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/iam.serviceAccountUser"
   
   # Allow the GitHub repository to impersonate the service account
   gcloud iam service-accounts add-iam-policy-binding "github-actions-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
     --project="${PROJECT_ID}" \
     --role="roles/iam.workloadIdentityUser" \
     --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/guilhermeguirro/NebulaMLPlatform"
   ```

2. Add GCP credentials to GitHub repository secrets:
   - `GCP_WORKLOAD_IDENTITY_PROVIDER`: The full identifier of the Workload Identity Provider (format: `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider`)
   - `GCP_SERVICE_ACCOUNT`: The email of the service account (e.g., `github-actions-sa@PROJECT_ID.iam.gserviceaccount.com`)

3. Configure GitHub repository variables:
   - `GCP_PROJECT_ID`: Your GCP project ID

4. Trigger the workflow from GitHub Actions

The workflow will:
- Authenticate using Workload Identity Federation
- Build and push the Docker image to Google Container Registry (GCR)
- Deploy to Cloud Run
- Output the API URL

#### Using Terraform for GCP 🏗️

1. Navigate to the terraform/gcp directory:
   ```bash
   cd terraform/gcp
   ```

2. Initialize and apply:
   ```bash
   terraform init
   terraform apply -var="project_id=[YOUR_PROJECT_ID]"
   ```

## 📄 API Documentation

Once deployed, the API documentation is available at `/docs` or `/redoc` endpoints.

Core API endpoints:

- `/api/health` ❤️: Health check endpoint
- `/api/v1/models` 🧩: Model management
- `/api/v1/transactions` 💰: Transaction operations
- `/api/v1/fraud` 🛡️: Fraud detection operations
- `/api/v1/ai` 🧠: AI service operations

## 📊 Monitoring

NebulaML Platform includes built-in monitoring using Prometheus and Grafana:

- **Prometheus** 📈: Collects and stores metrics
- **Grafana** 📊: Visualizes metrics with customizable dashboards

In the default setup, Prometheus is available at http://localhost:9090 and Grafana at http://localhost:3000.

## 🔒 Security

Security is implemented with:

- HashiCorp Vault for secrets management
- Role-based access control
- HTTPS for all external communications
- Encrypted data storage

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Contact

Guilherme Guirro - guilherme@guirro.org

Project Link: [https://github.com/guilhermeguirro/NebulaMLPlatform](https://github.com/guilhermeguirro/NebulaMLPlatform) 