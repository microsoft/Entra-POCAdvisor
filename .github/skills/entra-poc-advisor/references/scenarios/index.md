# Scenario Directory

This file serves as the index and schema definition for all pre-defined POC scenarios.

## Scenario Schema

Each scenario section in a reference file follows this structure:

```markdown
## Scenario: {scenario-id}

**Name:** {display name}
**Description:** {what the scenario demonstrates}
**Products:** {required Entra Suite products}
**Complexity:** {low | medium | high}
**Estimated Time:** {duration}

### Prerequisites
- **Licenses:** {required licenses}
- **Roles:** {required admin roles}
- **Infrastructure:** {required infrastructure}

### Architecture
{Mermaid diagram}

### Configuration Steps
1. **{Step Title}**
   - Component: {Entra component}
   - Portal Path: {navigation path in admin center}
   - Graph API: {method} {endpoint}
   - Body: {request body if applicable}
   - Validation: {method} {endpoint} -> {expected result}

### Validation Steps
1. **{Step Title}**
   - Type: {manual | automated}
   - Description: {what to verify}
```

## Scenario Index

### Private Access Scenarios

| ID | Name | File | Complexity | Time |
|---|---|---|---|---|
| private-access-quick-access | Quick Access | `private-access.md` | Medium | 45 min |
| private-access-per-app | Per-App Access | `private-access.md` | High | 90 min |
| private-access-private-dns | Private DNS | `private-access.md` | High | 60 min |

### Internet Access Scenarios

| ID | Name | File | Complexity | Time |
|---|---|---|---|---|
| internet-access-wcf | Web Content Filtering | `internet-access.md` | Medium | 30 min |
| internet-access-security-profiles | Security Profiles | `internet-access.md` | Medium | 45 min |
| internet-access-tls-inspection | TLS Inspection | `internet-access.md` | High | 60 min |
| internet-access-utr | Universal Tenant Restrictions | `internet-access.md` | Medium | 30 min |

### Global Secure Access Scenarios

| ID | Name | File | Complexity | Time |
|---|---|---|---|---|
| gsa-traffic-profiles | Traffic Forwarding Profiles | `global-secure-access.md` | Low | 20 min |
| gsa-client-deployment | GSA Client Deployment | `global-secure-access.md` | Medium | 30 min |
| gsa-ca-integration | Conditional Access Integration | `global-secure-access.md` | Medium | 45 min |

### Identity Scenarios

| ID | Name | File | Complexity | Time |
|---|---|---|---|---|
| identity-ca-baseline | Conditional Access Baseline | `identity.md` | Medium | 45 min |
| identity-id-protection | ID Protection | `identity.md` | Medium | 30 min |

### Governance Scenarios

| ID | Name | File | Complexity | Time |
|---|---|---|---|---|
| governance-access-reviews | Access Reviews | `governance.md` | Medium | 45 min |
| governance-entitlement-mgmt | Entitlement Management | `governance.md` | High | 60 min |

## Custom Scenarios

Administrators can describe custom scenarios in natural language. When this happens:

1. Use this schema definition to structure the custom scenario
2. Analyze requirements against the product references in `references/products/`
3. Identify the closest pre-defined scenario(s) as a starting point
4. Construct a custom scenario following the same structure
5. Clearly mark it as custom and note any assumptions made
