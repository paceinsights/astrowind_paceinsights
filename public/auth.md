# auth.md

Welcome! Pace Insights supports automated registration and authentication for AI agents, allowing machines to securely access our services, API catalog, and intelligence systems.

## Agent Audience

This service is designed to be accessed by autonomous AI agents, developer tools, and search crawlers who want to:

1. Discover our consultancy capabilities and client case studies
2. Programmatically fetch our API catalog (`/.well-known/api-catalog`)
3. Connect to our web tools and MCP servers

## Automated Registration & Provisioning

AI agents can register themselves anonymously or using a verified email address to obtain API credentials.

### Endpoint: `POST /api/agent/register`

To register, send a POST request with your agent identity metadata:

```json
{
  "agent_name": "MyAutonomousAgent/1.0",
  "identity_type": "anonymous",
  "contact_email": "agent@example.com"
}
```

### Response

The endpoint will return an API credential structure:

```json
{
  "client_id": "agent_client_123456789",
  "api_key": "pi_agent_live_abcdefghijklmnopqrstuvwxyz",
  "expires_at": "2027-06-04T00:00:00Z"
}
```

## Credential Usage

All authenticated API requests from agents must include the `Authorization` header with the Bearer token:

```http
Authorization: Bearer pi_agent_live_abcdefghijklmnopqrstuvwxyz
```

## OAuth Discovery and Resources

- **Authorization Server:** `https://paceinsights.com/.well-known/oauth-authorization-server`
- **OIDC Configuration:** `https://paceinsights.com/.well-known/openid-configuration`
- **Protected Resource Metadata:** `https://paceinsights.com/.well-known/oauth-protected-resource`
