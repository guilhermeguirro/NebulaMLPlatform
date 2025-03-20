#!/bin/bash

# Exit on error
set -e

# Check if required environment variables are set
if [ -z "$HCP_VAULT_URL" ] || [ -z "$HCP_VAULT_TOKEN" ]; then
    echo "Error: HCP_VAULT_URL and HCP_VAULT_TOKEN must be set"
    exit 1
fi

# Set Vault address and token
export VAULT_ADDR=$HCP_VAULT_URL
export VAULT_TOKEN=$HCP_VAULT_TOKEN

# Create namespace for NebulaML
echo "Creating NebulaML namespace..."
vault namespace create nebulaml

# Set namespace for subsequent commands
export VAULT_NAMESPACE=nebulaml

# Enable KV secrets engine
echo "Enabling KV secrets engine..."
vault secrets enable -path=nebulaml kv-v2

# Enable database secrets engine
echo "Enabling database secrets engine..."
vault secrets enable database

# Configure PostgreSQL connection
echo "Configuring PostgreSQL connection..."
vault write database/config/postgresql \
    plugin_name=postgresql-database-plugin \
    connection_url="postgresql://{{username}}:{{password}}@postgres:5432/nebulaml?sslmode=disable" \
    allowed_roles="nebulaml-role"

# Create database role
echo "Creating database role..."
vault write database/roles/nebulaml-role \
    db_name=postgresql \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';" \
    revocation_statements="DROP ROLE IF EXISTS \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"

# Create policies
echo "Creating Vault policies..."

# Policy for ML model secrets
cat << EOF > nebulaml-model-policy.hcl
path "nebulaml/data/models/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "nebulaml/metadata/models/*" {
  capabilities = ["list"]
}
EOF

# Policy for database credentials
cat << EOF > nebulaml-database-policy.hcl
path "database/creds/nebulaml-role" {
  capabilities = ["read"]
}
EOF

# Write policies to Vault
echo "Writing policies to Vault..."
vault policy write nebulaml-model nebulaml-model-policy.hcl
vault policy write nebulaml-database nebulaml-database-policy.hcl

# Create token role
echo "Creating token role..."
vault write auth/token/roles/nebulaml \
    allowed_policies="nebulaml-model,nebulaml-database" \
    token_period="24h" \
    token_max_ttl="48h"

# Enable audit logging
echo "Enabling audit logging..."
vault audit enable file file_path=/vault/logs/audit.log

# Create initial secret for testing
echo "Creating initial test secret..."
vault kv put nebulaml/models/test \
    model_name="test-model" \
    version="1.0.0" \
    framework="pytorch" \
    parameters="{}"

echo "Vault setup completed successfully!"
echo "You can now use the following token role to generate tokens: nebulaml" 