# Entra Verified ID — Product Reference

## Overview

Microsoft Entra Verified ID is a managed verifiable credentials service built on open standards (W3C Verifiable Credentials, DID). It enables organizations to issue and verify digital credentials that users store in a digital wallet (Microsoft Authenticator). Issuance creates a cryptographically signed credential (e.g., proof of employment, verified email). Presentation (verification) allows relying parties to request and validate credentials without contacting the issuer. The trust system is anchored by decentralized identifiers (DIDs) published to a trust registry.

Use Entra Verified ID when the POC requires decentralized identity, digital credential issuance, credential-based verification for onboarding or access, or integration with partner trust frameworks.

## Configuration Objects

| Object | Description | Parent/Dependency |
|---|---|---|
| **Authority** | The organization's verified ID configuration including DID, key vault, and linked domain. One authority per tenant. This is the issuer identity. | Key Vault, custom domain |
| **Credential Contract** | Defines a specific credential type: its display properties (name, logo, colors), claims (attributes included), and rules (how claims are collected during issuance). | Authority |
| **Issuance Request** | A request to issue a credential to a user. Specifies the contract, target user, claim values, and callback URL. Created by the issuing application. | Credential Contract |
| **Presentation Request** | A request for a user to present (prove) a credential. Specifies accepted credential types, required claims, and trust issuers. Created by the verifying application. | Credential Contract (of accepted type) |
| **Linked Domain** | A custom domain verified via DID configuration that establishes trust between the organization's DID and its domain name (e.g., contoso.com). Users see the verified domain when credentials are issued. | Authority, DNS configuration |
| **Key Vault** | Azure Key Vault instance that stores the signing keys for the authority's DID. Required for credential signing operations. | Azure subscription |

## Graph API Endpoints

### Authority

| Operation | Endpoint | API Version |
|---|---|---|
| List authorities | `GET /verifiableCredentials/authorities` | beta |
| Get authority | `GET /verifiableCredentials/authorities/{id}` | beta |
| Create authority | `POST /verifiableCredentials/authorities` | beta |
| Generate DID | `POST /verifiableCredentials/authorities/{id}/generateDid` | beta |
| Generate well-known DID configuration | `POST /verifiableCredentials/authorities/{id}/generateWellknownDidConfiguration` | beta |

### Contracts (Credential Types)

| Operation | Endpoint | API Version |
|---|---|---|
| List contracts | `GET /verifiableCredentials/authorities/{authorityId}/contracts` | beta |
| Get contract | `GET /verifiableCredentials/authorities/{authorityId}/contracts/{id}` | beta |
| Create contract | `POST /verifiableCredentials/authorities/{authorityId}/contracts` | beta |
| Update contract | `PATCH /verifiableCredentials/authorities/{authorityId}/contracts/{id}` | beta |

### Issuance and Presentation (Request Service API)

> [!NOTE]
> Issuance and presentation use the Request Service REST API, not the Graph API. The service endpoint is `https://verifiedid.did.msidentity.com/v1.0/verifiableCredentials/`.

| Operation | Endpoint | Notes |
|---|---|---|
| Create issuance request | `POST /v1.0/verifiableCredentials/createIssuanceRequest` | Request Service API |
| Create presentation request | `POST /v1.0/verifiableCredentials/createPresentationRequest` | Request Service API |
| Check request status | `GET /v1.0/verifiableCredentials/presentationRequests/{id}` | Request Service API |

### Verified ID Service Configuration (via Graph)

| Operation | Endpoint | API Version |
|---|---|---|
| Get service configuration | `GET /verifiableCredentials/configuration` | beta |

## Common Read Queries

**Check if Verified ID is configured in the tenant:**
```
GET /beta/verifiableCredentials/authorities
  → If empty array, Verified ID has not been set up
  → If populated, check: didMethod, linkedDomainUrls, keyVaultUrl
```

**List credential contracts (credential types):**
```
GET /beta/verifiableCredentials/authorities/{authorityId}/contracts
  → Returns each credential type with: name, rules, display definitions
```

**Get authority details including linked domain:**
```
GET /beta/verifiableCredentials/authorities/{id}
  → Check: name, didMethod (e.g., "did:web"), linkedDomainUrls, keyVaultUrl
```

**Check a specific contract's claim definitions:**
```
GET /beta/verifiableCredentials/authorities/{authorityId}/contracts/{contractId}
  → rules.attestations defines how claims are sourced (idTokens, selfIssued, etc.)
  → display defines card appearance (title, description, logo, backgroundColor)
```

## Configuration Relationships

```
Verified ID
├── Authority
│   ├── DID (decentralized identifier, e.g., did:web:contoso.com)
│   ├── Key Vault (stores signing keys)
│   │   └── Azure subscription + Key Vault resource
│   ├── Linked Domain
│   │   └── DNS TXT record or .well-known/did-configuration.json
│   └── Credential Contracts
│       ├── Contract: "VerifiedEmployee"
│       │   ├── Display: card name, logo, colors
│       │   ├── Rules: attestations (claims from id_token, self-issued, etc.)
│       │   └── Claims: displayName, jobTitle, employeeId
│       └── Contract: "VerifiedMember"
│           ├── Display: card name, logo, colors
│           ├── Rules: attestations
│           └── Claims: membershipLevel, expirationDate
├── Issuance Flow
│   ├── Application calls Request Service API → createIssuanceRequest
│   ├── User scans QR code or deep link → Microsoft Authenticator
│   ├── Authenticator collects attestations (sign-in, self-attested, etc.)
│   ├── Service signs credential with authority's DID key
│   └── Credential stored in user's Authenticator wallet
└── Presentation (Verification) Flow
    ├── Relying party calls Request Service API → createPresentationRequest
    ├── User scans QR code → selects credential in Authenticator
    ├── Authenticator creates verifiable presentation (signed by user's DID)
    ├── Service validates signature, issuer DID, and credential status
    └── Relying party receives verified claims in callback
```

The authority is the foundation — it must be created with a valid Key Vault and linked domain before any contracts can be defined. Contracts define what credentials look like and what claims they contain. The issuance and presentation flows are application-driven (your app calls the Request Service API) and do not use the Graph API.

## Licensing

| License | Provides |
|---|---|
| **Microsoft Entra Suite** | Full Verified ID (includes Private Access, Internet Access, ID Protection, ID Governance) |
| **Microsoft Entra Verified ID** (included with any Entra ID P1/P2 for basic scenarios) | Basic issuance and presentation with Microsoft Authenticator. Face Check (premium verification) requires Entra Suite or Verified ID premium add-on. |

Verified ID basic features (issuance, presentation) are available at no additional cost with Entra ID P1 or P2. Premium features like Face Check require Entra Suite or a premium add-on.

## Required Admin Roles

| Role | Permissions |
|---|---|
| **Global Administrator** | Full access to Verified ID setup, authority, and contract management |
| **Authentication Policy Administrator** | Can manage Verified ID settings and credential policies |
| **Global Reader** | Read-only access for validation and gap analysis |

### Azure Resource Requirements

| Resource | Purpose |
|---|---|
| **Azure Key Vault** | Stores the DID signing keys. Must be in the same tenant. Requires Key Vault Crypto Officer role for the Verified ID service principal. |
| **Azure Subscription** | Required for the Key Vault resource. Any subscription tier works. |

> [!IMPORTANT]
> Verified ID requires an Azure Key Vault in the same tenant. If the POC tenant does not have an Azure subscription, one must be created first. This is an infrastructure prerequisite that must be validated before Verified ID configuration begins.

> [!NOTE]
> The linked domain verification process requires adding a `did-configuration.json` file to the `.well-known` path of the organization's domain. This proves domain ownership and ensures users see a verified domain name when receiving credentials.
