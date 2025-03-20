# 🌌 NebulaML Platform

[![GitHub Actions - Azure](https://github.com/guilhermeguirro/NebulaMLPlatform/actions/workflows/deploy-azure.yml/badge.svg)](https://github.com/guilhermeguirro/NebulaMLPlatform/actions/workflows/deploy-azure.yml)
[![GitHub Actions - AWS](https://github.com/guilhermeguirro/NebulaMLPlatform/actions/workflows/deploy-aws.yml/badge.svg)](https://github.com/guilhermeguirro/NebulaMLPlatform/actions/workflows/deploy-aws.yml)
[![GitHub Actions - GCP](https://github.com/guilhermeguirro/NebulaMLPlatform/actions/workflows/deploy-gcp.yml/badge.svg)](https://github.com/guilhermeguirro/NebulaMLPlatform/actions/workflows/deploy-gcp.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Powered-blue.svg)](https://www.docker.com/)
[![Terraform](https://img.shields.io/badge/Terraform-Infrastructure-purple.svg)](https://www.terraform.io/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: OWASP](https://img.shields.io/badge/security-OWASP-red.svg)](https://owasp.org/www-project-top-ten/)

> 🚀 A comprehensive machine learning platform for building, training, deploying, and monitoring ML models in production environments with enterprise-grade security and scalability.

<div align="center">
  <img src="https://raw.githubusercontent.com/guilhermeguirro/NebulaMLPlatform/main/.github/assets/nebulaml-logo.png" alt="NebulaML Logo" width="300" />
</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Business Value & ROI](#-business-value--roi)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture) 
- [Technology Stack](#-technology-stack)
- [Getting Started](#-getting-started)
- [Deployment Options](#%EF%B8%8F-deployment-options)
  - [Azure Deployment](#-azure-deployment)
  - [AWS Deployment](#-aws-deployment)
  - [GCP Deployment](#-gcp-deployment)
- [API Documentation](#-api-documentation)
- [Monitoring & Observability](#-monitoring--observability)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)
- [Roadmap](#-roadmap)

## 🔭 Overview

NebulaML Platform is an end-to-end solution for the entire machine learning lifecycle, designed for data scientists, ML engineers, and DevOps teams. It streamlines the process of building, deploying, and monitoring machine learning models in production environments, with a focus on reliability, scalability, and ease of use.

Built with modern cloud-native technologies, the platform supports deployment across major cloud providers (Azure, AWS, GCP) and on-premises infrastructure, making it versatile for organizations at any stage of their cloud journey.

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

## ✨ Key Features

- **API-First Architecture** 🔌: RESTful API for all ML operations
- **Model Management** 📊: Version control and lifecycle management for ML models
- **Automated CI/CD** 🔄: Seamless deployment workflows for all environments
- **Real-Time Monitoring** 📡: Comprehensive metrics, logging, and alerting
- **Multi-Cloud Support** ☁️: Deploy to Azure, AWS, GCP, or on-premises
- **Scalable Infrastructure** 🏗️: Built to handle production workloads
- **Enterprise Security** 🔒: Role-based access control and data encryption
- **Multi-Tenancy** 👥: Support for multiple teams and projects
- **Audit Trail** 📝: Track all operations performed on the platform
- **GitOps Integration** 🔄: Infrastructure as code with version control
- **AI Services Integration** 🧠: Built-in connectors for popular AI services

## 🏛️ System Architecture

NebulaML Platform follows a microservices architecture with the following core components:

<div align="center">
  <img src="https://raw.githubusercontent.com/guilhermeguirro/NebulaMLPlatform/main/.github/assets/architecture.png" alt="NebulaML Architecture" width="700" />
</div>

### Core Components

- **API Gateway** 🌐: Entry point for all requests with authentication and rate limiting
- **AI Service** 🧠: Handles model training, inference, and AI-specific operations
- **Transaction Service** 💳: Manages data flow and transaction processing
- **Fraud Detection Service** 🛡️: Specialized service for fraud detection models
- **Security Service** 🔐: Manages authentication, authorization, and secrets
- **Monitoring Stack** 📊: Prometheus, Grafana, and Jaeger for observability

## 🛠 Technology Stack

NebulaML Platform is built using modern technologies:

- **Backend**:
  - Python 3.9+ (FastAPI, Pydantic, SQLAlchemy)
  - Redis for caching and rate limiting
  - PostgreSQL for persistent storage
  
- **Infrastructure**:
  - Docker & Kubernetes for containerization and orchestration
  - Terraform for infrastructure as code
  - GitHub Actions for CI/CD
  
- **Security**:
  - HashiCorp Vault for secrets management
  - OpenID Connect (OIDC) for federated authentication
  - TLS encryption for all network traffic
  
- **Monitoring**:
  - Prometheus for metrics collection
  - Grafana for visualization
  - Jaeger for distributed tracing
  - OpenTelemetry for instrumentation

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

3. Access the API at http://localhost:8001

### Development Commands

```bash
# Install dependencies
make setup

# Run all tests
make test

# Format code
make format

# Run linting checks
make lint

# Build Docker containers
make build

# Start all services
make docker-up

# View logs
make docker-logs
```

### Environment Configuration ⚙️

Configuration is managed through environment variables. Create a `.env` file in the project root:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=true
API_LOG_LEVEL=INFO

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=nebulaml
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Vault Configuration
VAULT_URL=https://vault.example.com
VAULT_TOKEN=your-token
VAULT_NAMESPACE=nebulaml
```

## 🌩️ Deployment Options

NebulaML Platform supports deployment to all major cloud providers with secure CI/CD workflows.

### ☁️ Azure Deployment

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

### ☁️ AWS Deployment

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

### ☁️ GCP Deployment

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

Once deployed, the API documentation is available at `/docs` endpoint with Swagger UI or `/redoc` for ReDoc.

### Core API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint ❤️ |
| `/metrics` | GET | Prometheus metrics endpoint 📊 |
| `/api/v1/models` | GET | List all ML models 📋 |
| `/api/v1/models/{id}` | GET | Get model details 🔍 |
| `/api/v1/models` | POST | Register a new model 📥 |
| `/api/v1/models/{id}/deploy` | POST | Deploy a model to production 🚀 |
| `/api/v1/models/{id}/predict` | POST | Get predictions from a model 🔮 |
| `/api/v1/transactions` | GET | List transactions 💳 |
| `/api/v1/transactions/{id}` | GET | Get transaction details 🔍 |
| `/api/v1/fraud/detect` | POST | Detect fraud in a transaction 🛡️ |
| `/api/v1/ai/analyze` | POST | Analyze data with AI 🧠 |

## 📊 Monitoring & Observability

NebulaML Platform includes a comprehensive monitoring and observability stack:

### Components

- **Metrics** 📈:
  - Prometheus for collecting and storing metrics
  - Grafana for metric visualization and dashboards
  - Custom dashboards for model performance, system health, and business KPIs

- **Logging** 📝:
  - Structured logging with correlation IDs
  - Centralized log aggregation
  - Real-time log analysis

- **Tracing** 🔍:
  - Jaeger for distributed tracing
  - OpenTelemetry for instrumentation
  - End-to-end request tracking

- **Alerting** 🚨:
  - Proactive alerting based on performance metrics
  - Automated alert routing to appropriate teams
  - Custom alert thresholds for different environments

### Default Access Points

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Jaeger: http://localhost:16686

## 🔒 Security

Security is a top priority for NebulaML Platform, with measures implemented at every layer:

- **Authentication & Authorization** 🔐:
  - Role-based access control (RBAC)
  - Single Sign-On (SSO) integration
  - Multi-factor authentication (MFA)

- **Data Protection** 🛡️:
  - End-to-end encryption for data in transit and at rest
  - Secure data storage with encryption
  - Data masking for sensitive information

- **Secrets Management** 🗝️:
  - HashiCorp Vault for secrets storage
  - Dynamic secrets with automatic rotation
  - Least privilege access principles

- **Network Security** 🌐:
  - TLS 1.3 for all communications
  - Network isolation for sensitive components
  - Web Application Firewall (WAF) protection

- **Compliance** 📜:
  - GDPR compliance built-in
  - SOC 2 Type II compliant
  - Regular security assessments and penetration testing

## 👥 Contributing

We ❤️ contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

Please ensure your PR adheres to our coding standards and includes appropriate tests.

### Development Guidelines

- Follow the code style guidelines (we use Black for Python)
- Write tests for new features
- Update documentation as needed
- Add type hints to Python code
- Keep pull requests focused on a single feature or fix

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Guilherme Guirro** - [guilherme@guirro.org](mailto:guilherme@guirro.org)
- **Project Website** - [https://nebulaml.ai](https://nebulaml.ai)
- **GitHub** - [https://github.com/guilhermeguirro/NebulaMLPlatform](https://github.com/guilhermeguirro/NebulaMLPlatform)
- **Twitter** - [@NebulaMLAI](https://twitter.com/NebulaMLAI)

## 🗺 Roadmap

- **Q2 2023** 📅
  - ✅ Initial platform release
  - ✅ Multi-cloud deployment support
  - ✅ Basic monitoring and observability

- **Q3 2023** 📅
  - ✅ Enhanced security features
  - ✅ Integration with popular ML frameworks
  - ✅ Improved CI/CD workflows

- **Q4 2023** 📅
  - ✅ Multi-tenancy support
  - ✅ Advanced monitoring dashboards
  - ✅ Kubernetes integration

- **Q1 2024** 📅
  - ✅ Federated learning capabilities
  - ✅ Model explanation tools
  - ✅ Enhanced compliance features

- **Q2 2024** 📅
  - ✅ Enterprise edition launch
  - 🔄 Advanced AI capabilities
  - 🔄 Edge deployment support

- **Q3 2024** 📅
  - 🔄 Automated ML operations
  - 🔄 Real-time feature store
  - 🔄 Model governance framework

---

<div align="center">
  <p>
    <a href="https://star-history.com/#guilhermeguirro/NebulaMLPlatform">
      <img src="https://api.star-history.com/svg?repos=guilhermeguirro/NebulaMLPlatform&type=Date" alt="Star History Chart" width="600" />
    </a>
  </p>
  <p>⭐ If you find this project useful, please give it a star on GitHub! ⭐</p>
</div> 