storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_cert_file = "/vault/config/client.crt"
  tls_key_file  = "/vault/config/client.key"
  tls_client_ca_file = "/vault/config/ca.crt"
  tls_require_and_verify_client_cert = true
}

api_addr = "http://vault:8200"

ui = true

default_lease_ttl = "1h"
max_lease_ttl = "24h"

audit_device "file" {
  path = "/vault/logs/audit.log"
  format = "json"
}

seal "transit" {
  address = "http://vault:8200"
  token = "dev-only-token"
  disable_renewal = "false"
}

telemetry {
  disable_hostname = true
  prometheus_retention_time = "24h"
} 