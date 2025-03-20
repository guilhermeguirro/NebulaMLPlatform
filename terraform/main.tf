provider "azurerm" {
  features {}
}

# Variables
variable "resource_group_name" {
  description = "Name of the resource group"
  default     = "nebulaml-rg"
}

variable "location" {
  description = "Azure region"
  default     = "eastus"
}

variable "acr_name" {
  description = "Name of the Azure Container Registry"
  default     = "nebulamlregistry"
}

variable "environment_name" {
  description = "Name of the Container Apps environment"
  default     = "nebulaml-env"
}

variable "api_image_tag" {
  description = "API image tag"
  default     = "latest"
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "law" {
  name                = "logs-${var.environment_name}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Container Registry
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

# Container Apps Environment
resource "azurerm_container_app_environment" "env" {
  name                       = var.environment_name
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
}

# API Container App
resource "azurerm_container_app" "api" {
  name                         = "nebulaml-api"
  resource_group_name          = azurerm_resource_group.rg.name
  container_app_environment_id = azurerm_container_app_environment.env.id
  revision_mode                = "Single"

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "registry-password"
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.acr.admin_password
  }

  template {
    container {
      name   = "nebulaml-api"
      image  = "${azurerm_container_registry.acr.login_server}/nebulaml-api:${var.api_image_tag}"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "API_HOST"
        value = "0.0.0.0"
      }

      env {
        name  = "API_PORT"
        value = "8000"
      }

      env {
        name  = "API_WORKERS"
        value = "2"
      }

      env {
        name  = "API_RELOAD"
        value = "false"
      }

      env {
        name  = "API_LOG_LEVEL"
        value = "INFO"
      }
    }

    min_replicas = 1
    max_replicas = 5
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
}

# Output
output "api_url" {
  value = "https://${azurerm_container_app.api.ingress[0].fqdn}"
} 