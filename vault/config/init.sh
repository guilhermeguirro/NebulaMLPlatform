#!/bin/bash

# Wait for Vault to be ready
until curl -fs http://vault:8200/v1/sys/health > /dev/null; do
    echo "Waiting for Vault to start..."
    sleep 1
done

# Initialize Vault
vault operator init -key-shares=1 -key-threshold=1 -format=json > /vault/config/init.json

# Unseal Vault
vault operator unseal $(cat /vault/config/init.json | jq -r .unseal_keys_b64[0])

# Enable KV secrets engine
vault secrets enable -path=data kv-v2

# Enable database secrets engine
vault secrets enable -path=database database

# Create policies
vault policy write neutronpay-transactions - <<EOF
path "data/transactions/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "data/credentials/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "data/audit/*" {
  capabilities = ["read", "list"]
}

path "database/creds/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
EOF

# Create a token for the transactions service
vault token create -policy=neutronpay-transactions -format=json > /vault/config/service-token.json

# Enable audit logging
vault audit enable file file_path=/vault/logs/audit.log

# Configure database connection
vault write database/config/postgres \
    plugin_name=postgresql-database-plugin \
    connection_url="postgresql://postgres:postgres@postgres:5432/neutronpay?sslmode=disable" \
    allowed_roles="neutronpay-role"

# Create database role
vault write database/roles/neutronpay-role \
    db_name=postgres \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';" \
    revocation_statements="DROP ROLE IF EXISTS \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"

echo "Vault initialization complete!" 