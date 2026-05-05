# Entra External Identities — Product Reference

## Overview

Microsoft Entra External ID manages identity and access for people outside your organization. It encompasses three models: **B2B Collaboration** (inviting partner/vendor users as guests into your workforce tenant), **B2B Direct Connect** (establishing mutual trust between Entra ID organizations for Teams shared channels without provisioning guests), and **Customer Identity and Access Management (CIAM)** (building customer-facing apps with self-service sign-up, social identity providers, and custom branding in a dedicated external tenant).

Use Entra External Identities when the POC requires guest user onboarding, cross-organization collaboration, external partner access governance, customer sign-up/sign-in flows, or social identity provider integration.

## External Identity Models

| Model | Target Users | Tenant Model | Key Capabilities |
|---|---|---|---|
| **B2B Collaboration** | Partners, vendors, contractors | Guest accounts in workforce tenant | Email OTP, Microsoft account, SAML/WS-Fed federation, cross-tenant access policies, redemption settings, Conditional Access for guests |
| **B2B Direct Connect** | Users in partner Entra ID tenants | No guest provisioning — mutual trust | Cross-tenant access settings, Teams shared channels, identity-based access without guest object |
| **CIAM (External ID for customers)** | Consumers, customers, citizens | Dedicated external tenant | Self-service sign-up, social IdPs (Google, Facebook, Apple), custom branding, user flows, token customization, API connectors |

## Configuration Objects

| Object | Description | Parent/Dependency |
|---|---|---|
| **Cross-Tenant Access Settings** | Tenant-wide and per-organization policies controlling inbound/outbound B2B collaboration and B2B direct connect. | None (top-level) |
| **Cross-Tenant Access Partner Configuration** | Per-partner override of default cross-tenant access settings (inbound/outbound trust, B2B collab, B2B direct connect). | Cross-Tenant Access Settings |
| **Invitation** | Object representing a guest user invitation with redirect URL, message, and redemption configuration. | None (top-level) |
| **Guest User** | External user account in workforce tenant with `userType=Guest` and external identity references. | Invitation (or self-service sign-up) |
| **External Tenant** | Dedicated Microsoft Entra tenant configured for external (customer) scenarios with CIAM capabilities. | None (separate tenant) |
| **User Flow** | Self-service sign-up/sign-in experience definition in external tenant (authentication methods, attributes, IdPs, branding). | External Tenant |
| **Identity Provider** | Configuration for external authentication sources: social (Google, Facebook, Apple), SAML/WS-Fed, or email OTP. | Tenant-level |
| **Custom Authentication Extension** | API connector that calls external APIs during sign-up/sign-in flows for validation, enrichment, or custom logic. | User Flow |
| **Application Registration** | App registered in external tenant with token configuration, API permissions, and redirect URIs for customer-facing apps. | External Tenant |
| **Company Branding** | Visual customization of sign-in/sign-up pages (logo, background, CSS, layout) in external tenant. | External Tenant |

## Graph API Endpoints

### Cross-Tenant Access Settings (B2B Collaboration & B2B Direct Connect)

| Operation | Endpoint | API Version |
|---|---|---|
| Get default cross-tenant access settings | `GET /policies/crossTenantAccessPolicy/default` | v1.0 |
| Update default settings | `PATCH /policies/crossTenantAccessPolicy/default` | v1.0 |
| List partner configurations | `GET /policies/crossTenantAccessPolicy/partners` | v1.0 |
| Create partner configuration | `POST /policies/crossTenantAccessPolicy/partners` | v1.0 |
| Update partner configuration | `PATCH /policies/crossTenantAccessPolicy/partners/{tenantId}` | v1.0 |
| Get inbound trust settings | `GET /policies/crossTenantAccessPolicy/partners/{tenantId}` | v1.0 |

### Guest User Management (B2B Collaboration)

| Operation | Endpoint | API Version |
|---|---|---|
| Invite user | `POST /invitations` | v1.0 |
| List guest users | `GET /users?$filter=userType eq 'Guest'` | v1.0 |
| Get invitation status | `GET /users/{id}?$select=externalUserState,externalUserStateChangeDateTime` | v1.0 |
| List external identities | `GET /users/{id}/authentication/methods` | v1.0 |
| Delete guest user | `DELETE /users/{id}` | v1.0 |

### Identity Providers

| Operation | Endpoint | API Version |
|---|---|---|
| List identity providers | `GET /identityProviders` | v1.0 |
| Create identity provider (social) | `POST /identityProviders` | v1.0 |
| List available provider types | `GET /identityProviders/availableProviderTypes` | v1.0 |
| Get SAML/WS-Fed IdP | `GET /identity/identityProviders/{id}` | beta |
| Create SAML/WS-Fed federation | `POST /identity/identityProviders` | beta |

### External Tenant & User Flows (CIAM)

| Operation | Endpoint | API Version |
|---|---|---|
| List user flows | `GET /identity/authenticationEventsFlows` | beta |
| Create user flow | `POST /identity/authenticationEventsFlows` | beta |
| Get user flow | `GET /identity/authenticationEventsFlows/{id}` | beta |
| List custom authentication extensions | `GET /identity/customAuthenticationExtensions` | v1.0 |
| Create custom authentication extension | `POST /identity/customAuthenticationExtensions` | v1.0 |
| Get branding | `GET /organizationalBranding/localizations` | v1.0 |
| Update branding | `PATCH /organizationalBranding/localizations/{id}` | v1.0 |

### Redemption & Authentication Settings

| Operation | Endpoint | API Version |
|---|---|---|
| Get external collaboration settings | `GET /policies/authorizationPolicy` | v1.0 |
| Update invitation settings | `PATCH /policies/authorizationPolicy` | v1.0 |
| Get authentication methods policy | `GET /policies/authenticationMethodsPolicy` | v1.0 |
| Get email OTP policy | `GET /policies/authenticationMethodsPolicy/authenticationMethodConfigurations/email` | v1.0 |

## Common Read Queries

**List all cross-tenant access partner configurations:**
```
GET /v1.0/policies/crossTenantAccessPolicy/partners
```

**Get default cross-tenant access settings (inbound/outbound B2B and direct connect):**
```
GET /v1.0/policies/crossTenantAccessPolicy/default
```

**List all guest users and their redemption state:**
```
GET /v1.0/users?$filter=userType eq 'Guest'&$select=displayName,mail,externalUserState,createdDateTime
```

**List configured identity providers (social IdPs, federation):**
```
GET /v1.0/identityProviders
```

**Check email OTP status:**
```
GET /v1.0/policies/authenticationMethodsPolicy/authenticationMethodConfigurations/email
```

**List user flows in external tenant (CIAM):**
```
GET /beta/identity/authenticationEventsFlows
```

## Configuration Relationships

```
External Identities
├── B2B Collaboration
│   ├── Cross-Tenant Access Settings
│   │   ├── Default policy (inbound/outbound)
│   │   │   ├── B2B collaboration settings (apps, users allowed)
│   │   │   └── Trust settings (MFA trust, compliant device trust)
│   │   └── Partner configurations (per-organization overrides)
│   │       ├── Inbound access (who from partner can access your tenant)
│   │       ├── Outbound access (who from your tenant can access partner)
│   │       └── Trust settings (accept partner MFA, device claims)
│   ├── Invitation Settings
│   │   ├── Who can invite (admins only, members, guests)
│   │   ├── Redemption order (Entra ID, Microsoft account, email OTP)
│   │   └── Self-service sign-up (enabled/disabled)
│   ├── Identity Providers (for guest redemption)
│   │   ├── Email one-time passcode
│   │   ├── Microsoft account
│   │   ├── Google federation
│   │   ├── Facebook federation
│   │   └── SAML/WS-Fed federation (per domain)
│   └── Guest Conditional Access
│       ├── Named location for external users
│       ├── MFA requirement for guests
│       └── Session controls (sign-in frequency)
├── B2B Direct Connect
│   ├── Cross-Tenant Access Settings (mutual configuration)
│   │   ├── Inbound direct connect (allow partner users)
│   │   ├── Outbound direct connect (allow your users)
│   │   └── Trust settings (accept partner MFA claims)
│   └── Teams Shared Channels
│       ├── Shared channel creation
│       ├── External user invitation to channel
│       └── No guest object provisioned
└── CIAM (External ID for Customers)
    ├── External Tenant
    │   ├── Tenant creation (customer configuration)
    │   ├── Custom domain (branded login URL)
    │   └── Admin roles and permissions
    ├── User Flows
    │   ├── Sign-up + sign-in flow
    │   │   ├── Identity providers (social, email + password, email OTP)
    │   │   ├── User attributes to collect
    │   │   ├── Custom branding (layout, CSS, logo)
    │   │   └── Custom authentication extensions (API connectors)
    │   └── Self-service password reset flow
    ├── Application Registration
    │   ├── Redirect URIs (SPA, web, native)
    │   ├── Token configuration (claims, lifetime)
    │   └── API permissions
    └── Company Branding
        ├── Default branding (logo, background, colors)
        └── Per-locale branding overrides
```

## Licensing

| License | Provides |
|---|---|
| **Microsoft Entra ID Free** | B2B Collaboration basics (invite guests, up to 50,000 MAU) |
| **Microsoft Entra ID P1** | Conditional Access for guests, dynamic groups with guest users |
| **Microsoft Entra ID P2** | ID Protection for guests, access reviews for external users, PIM for guest role assignments |
| **Microsoft Entra External ID** (standalone) | CIAM capabilities: external tenant, user flows, social IdPs, custom branding (first 50,000 MAU free, then per-authentication pricing) |
| **Microsoft Entra Suite** | Full External ID capabilities plus Private Access, Internet Access, ID Protection, ID Governance, Verified ID |

> [!NOTE]
> B2B Direct Connect does not require additional licenses beyond the base Entra ID license on both tenants. CIAM (External ID for customers) uses consumption-based pricing after the free tier.

## Required Admin Roles

| Role | Permissions |
|---|---|
| **Global Administrator** | Full access to all external identity features |
| **External Identity Provider Administrator** | Manage identity providers (social, SAML/WS-Fed federation) |
| **External ID User Flow Administrator** | Create and manage user flows in external tenant |
| **Guest Inviter** | Invite guest users (B2B collaboration) |
| **Security Administrator** | Manage cross-tenant access policies, Conditional Access for guests |
| **Application Administrator** | Register and configure apps in external tenant |
| **Global Reader** | Read-only access for validation and gap analysis |

## Supported Authentication Methods

| Method | B2B Collaboration | B2B Direct Connect | CIAM |
|---|---|---|---|
| **Email one-time passcode** | ✅ Default fallback | N/A | ✅ |
| **Microsoft account** | ✅ | N/A | ❌ |
| **Google federation** | ✅ | N/A | ✅ |
| **Facebook federation** | ❌ | N/A | ✅ |
| **Apple ID** | ❌ | N/A | ✅ |
| **SAML/WS-Fed federation** | ✅ Per-domain | N/A | ❌ |
| **Passkeys / FIDO2** | ✅ (via home tenant) | ✅ (via home tenant) | ✅ |
| **Home tenant MFA (trust)** | ✅ (cross-tenant trust) | ✅ (cross-tenant trust) | N/A |

> [!IMPORTANT]
> B2B Direct Connect authenticates users in their **home tenant** — no authentication configuration is needed in the resource tenant. The trust settings control whether the resource tenant accepts MFA and device compliance claims from the home tenant.
