# Entra Internet Access — Product Reference

## Overview

Microsoft Entra Internet Access is a Security Service Edge (SSE) solution that secures access to all internet destinations, including SaaS applications. It provides web content filtering, TLS inspection, and Universal Tenant Restrictions through the Global Secure Access service. Internet-bound traffic from the GSA Client is routed through the Microsoft Entra cloud edge where security policies are enforced before traffic reaches the destination.

Use Entra Internet Access when the POC requires web content filtering, protection against malicious sites, data exfiltration prevention via tenant restrictions, or HTTPS traffic inspection.

## Configuration Objects

| Object | Description | Parent/Dependency |
|---|---|---|
| **Web Content Filtering Policy** | Defines rules that block or allow internet traffic based on web content categories (e.g., Gambling, Social Networking, Malware) or specific FQDNs. | None (standalone, linked to a security profile) |
| **Filtering Rule** | Individual rule within a filtering policy that specifies an action (block/allow) for a category group, category, or FQDN list. | Web Content Filtering Policy |
| **Security Profile (Filtering Profile)** | Groups one or more filtering policies together with a priority order. Linked to users via Conditional Access session controls. | Filtering Policies |
| **FQDN Filtering Policy** | Filtering policy that targets specific fully qualified domain names rather than categories. Used for granular allow/block lists. | None (linked to a security profile) |
| **TLS Inspection** | Enables decryption of HTTPS traffic for deep inspection. Requires deployment of a GSA root certificate to client devices. | Internet Access profile enabled |
| **Content Policy** | Filters network file content by MIME type. Supports basic block/allow actions or advanced "Scan with Purview" for DLP integration with sensitivity labels and sensitive info types. Only supports files over HTTP/1.1 (not text). | TLS Inspection enabled |
| **Source Traffic Type Filtering (Preview)** | Scopes web content filtering rules to specific traffic origins: Agent (AI agents, Copilot), Browser, Application, or Unknown. Requires GSA Client (not supported on remote networks). Combined with HTTP method filtering for granular AI governance. | Web Content Filtering Policy, GSA Client |
| **HTTP Method Request Filtering (Preview)** | Blocks or allows specific HTTP methods (GET, POST, PUT, PATCH, DELETE) in web content filtering rules. Enables least-privilege access by restricting write operations while permitting reads. Requires TLS inspection for HTTPS traffic. | TLS Inspection, Web Content Filtering Policy |
| **Explicit Forward Proxy (Preview)** | PAC file-based proxy for clientless internet access. Uses Entra ID authentication, supports smart/IP/header session affinity, and Continuous Access Evaluation. Security profiles assigned via CA policies targeting the `GSA-ExplicitForwardProxy` workload identity. Not included in "All internet resources with Global Secure Access" target. | Internet Access profile enabled, Named locations |
| **Baseline Security Profile** | Tenant-wide security profile at priority 65,000 that applies to all traffic (client and remote network) without requiring Conditional Access. Ideal for securing remote network/branch office traffic. User-specific CA-linked profiles override at higher priority. | Internet Access profile enabled |
| **Universal Tenant Restrictions (UTR)** | Prevents users from authenticating to unauthorized external tenants. Works by injecting tenant restriction headers into authentication traffic. | Cross-Tenant Access Settings |
| **Universal Continuous Access Evaluation (CAE)** | Extends CAE to any application accessed through Global Secure Access without requiring app-level CAE support. Revokes and revalidates network access in near real-time when Entra ID detects identity changes (account disabled, password reset, MFA enabled, tokens revoked, high risk). Optional Strict Enforcement mode prevents token theft/replay. | Global Secure Access enabled |

## Graph API Endpoints

### Filtering Policies

| Operation | Endpoint | API Version |
|---|---|---|
| List filtering policies | `GET /networkAccess/filteringPolicies` | beta |
| Get filtering policy | `GET /networkAccess/filteringPolicies/{id}` | beta |
| Create filtering policy | `POST /networkAccess/filteringPolicies` | beta |
| Update filtering policy | `PATCH /networkAccess/filteringPolicies/{id}` | beta |
| List policy rules | `GET /networkAccess/filteringPolicies/{id}/policyRules` | beta |

### Security Profiles (Filtering Profiles)

| Operation | Endpoint | API Version |
|---|---|---|
| List filtering profiles | `GET /networkAccess/filteringProfiles` | beta |
| Get filtering profile | `GET /networkAccess/filteringProfiles/{id}` | beta |
| Create filtering profile | `POST /networkAccess/filteringProfiles` | beta |
| Update filtering profile | `PATCH /networkAccess/filteringProfiles/{id}` | beta |
| List linked policies in profile | `GET /networkAccess/filteringProfiles/{id}/policies` | beta |

### Web Categories

| Operation | Endpoint | API Version |
|---|---|---|
| List available web categories | `GET /networkAccess/filteringPolicies/microsoftGraphNetworkAccessFilteringPolicyWebContentCategories` | beta |

### Cross-Tenant Access (for UTR)

| Operation | Endpoint | API Version |
|---|---|---|
| Get default cross-tenant policy | `GET /policies/crossTenantAccessPolicy/default` | v1.0 |
| List partner configurations | `GET /policies/crossTenantAccessPolicy/partners` | v1.0 |
| Create partner configuration | `POST /policies/crossTenantAccessPolicy/partners` | v1.0 |

### Content Policies

| Operation | Endpoint | API Version |
|---|---|---|
| List content policies | `GET /networkAccess/filteringPolicies` (filter by type) | beta |
| Create content policy | `POST /networkAccess/filteringPolicies` | beta |

### Explicit Forward Proxy

| Operation | Endpoint | API Version |
|---|---|---|
| Get EFP session settings | `GET /networkAccess/settings/forwardProxy` | beta |
| Enable/disable EFP | `PATCH /networkAccess/settings/forwardProxy` | beta |

## Common Read Queries

**List all filtering policies and their rules:**
```
GET /beta/networkAccess/filteringPolicies?$expand=policyRules
```

**List all security profiles with linked policies:**
```
GET /beta/networkAccess/filteringProfiles?$expand=policies
```

**Verify Internet Access traffic profile is enabled:**
```
GET /beta/networkAccess/forwardingProfiles
  → Filter for profile with trafficForwardingType == "internet" and state == "enabled"
```

**Check baseline security profile and linked policies:**
```
GET /beta/networkAccess/filteringProfiles
  → Filter for profile with priority == 65000 (baseline profile)
  → Expand policies to see linked filtering/content policies
```

**Check cross-tenant access default policy (UTR baseline):**
```
GET /v1.0/policies/crossTenantAccessPolicy/default
  → Look for: tenantRestrictions configuration
```

**List approved partner tenants:**
```
GET /v1.0/policies/crossTenantAccessPolicy/partners
  → Each entry represents an external tenant with configured inbound/outbound rules
```

## Configuration Relationships

```
Traffic Forwarding Profile (Internet Access)
├── Security Profile (Filtering Profile) — linked via CA session control
│   ├── Web Content Filtering Policy (priority: 100)
│   │   ├── Rule: Block category "Gambling"
│   │   ├── Rule: Block category "Adult Content" [Source type: Agent] [HTTP method: POST, PUT]
│   │   └── Rule: Block category "Malware"
│   ├── FQDN Filtering Policy (priority: 200)
│   │   ├── Rule: Block "example-bad-site.com"
│   │   └── Rule: Allow "exception-site.com"
│   ├── Content Policy (priority: 300)
│   │   ├── Rule: Block PDF upload to chatgpt.com (MIME type)
│   │   └── Rule: Scan with Purview → DLP policy evaluation
│   └── Linked via Conditional Access session control
├── Baseline Security Profile (priority: 65000, tenant-wide)
│   ├── Applies to ALL traffic (client + remote network)
│   ├── No CA policy required
│   └── Linked filtering/content policies
├── Explicit Forward Proxy (Preview)
│   ├── PAC file endpoint for clientless devices
│   ├── Session management (smart/IP/header affinity)
│   ├── CA policy → GSA-ExplicitForwardProxy workload identity
│   └── Security profile assigned via CA session control
├── TLS Inspection
│   ├── Inspection policy (which traffic to decrypt)
│   ├── Bypass rules (banking, healthcare)
│   ├── Required for: HTTP method filtering, content policy, source type (HTTPS)
│   └── GSA Root Certificate (deployed to devices)
├── Universal Tenant Restrictions
│   ├── Cross-Tenant Access Policy (default: block)
│   └── Partner configurations (explicit allows)
└── Universal Continuous Access Evaluation
    ├── Near real-time revocation on identity changes
    ├── Signals: account disabled, password reset, MFA enabled, tokens revoked, high risk
    └── Optional Strict Enforcement mode (IP-bound tokens)
```

Policy evaluation logic:
- **Within same attribute:** OR logic (matching any selected value triggers)
- **Across attributes:** AND logic (all conditions must match)
- **Conflicting actions:** Most restrictive wins (block over allow)
- **Profile priority:** Lower number = higher priority; baseline (65000) is always last

Security profiles are linked to users through Conditional Access policies using session controls. Different CA policies can target different user groups, each linking to a different security profile. This enables role-based internet access policies.

Policy evaluation order within a security profile follows the priority value (lower number = higher priority). If multiple rules match, the first matching rule wins.

## Licensing

| License | Provides |
|---|---|
| **Microsoft Entra Suite** | Full Internet Access functionality (includes Private Access, ID Protection, ID Governance, Verified ID) |
| **Microsoft Entra Internet Access** (standalone) | Internet Access only |

Licenses must be assigned to users whose internet traffic is routed through GSA. The Microsoft 365 traffic profile does not require Internet Access licensing.

## Required Admin Roles

| Role | Permissions |
|---|---|
| **Global Administrator** | Full configuration access |
| **Security Administrator** | Can manage filtering policies, security profiles, Conditional Access, and TLS inspection |
| **Global Secure Access Administrator** | Can manage all GSA settings including Internet Access policies and profiles |
| **Conditional Access Administrator** | Can create CA policies that link security profiles (but cannot create the profiles themselves) |
| **Global Reader** | Read-only access for validation and gap analysis |

> [!IMPORTANT]
> TLS inspection requires deploying the GSA root certificate to all client devices. Without the certificate, HTTPS sites will show certificate errors. Plan certificate deployment via Intune, GPO, or manual installation before enabling TLS inspection.
