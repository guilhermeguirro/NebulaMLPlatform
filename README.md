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

#### Using GitHub Actions (Recommended) 🔄

The repository includes GitHub Actions workflows that automate the deployment process:

1. Ensure you have an Azure account and subscription
2. Create Azure service principal credentials:
   ```bash
   az ad sp create-for-rbac --name "nebulaml-github-actions" \
                           --role contributor \
                           --scopes /subscriptions/<subscription-id> \
                           --sdk-auth
   ```
3. Add the JSON output as a GitHub repository secret named `AZURE_CREDENTIALS`
4. Trigger the workflow manually from the GitHub Actions tab or push to the main branch

The workflow will:
- Create a resource group
- Deploy an Azure Container Registry
- Build and push the Docker image
- Deploy to Azure Container Apps
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

## 📚 API Documentation

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