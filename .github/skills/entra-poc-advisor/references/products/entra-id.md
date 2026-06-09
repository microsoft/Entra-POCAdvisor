# Entra ID — Product Reference

## Overview

Microsoft Entra ID is the cloud identity and access management service that provides authentication, authorization, and identity governance for organizations. It serves as the foundation for all Entra Suite products and provides core capabilities including authentication methods, Conditional Access, self-service password reset (SSPR), and account recovery.

This reference focuses on the Account Recovery capability — a high-assurance self-service recovery mechanism for users who have lost all authentication methods.

## Account Recovery

Account recovery enables users to regain access to their accounts when all registered authentication methods are unavailable (total lockout). Unlike SSPR which requires at least one existing method, account recovery re-establishes trust through government-issued ID verification and biometric matching via third-party identity verification providers.

### Account Recovery vs. SSPR

| Aspect | Self-Service Password Reset (SSPR) | Account Recovery |
|---|---|---|
| Primary use case | Forgot password, retains auth methods | Lost ALL authentication methods |
| Authentication requirement | At least one registered method | Identity verification through certified provider |
| Trust assumption | Verified through existing methods | Identity must be re-established |
| Recovery scope | Password only | Complete authentication method reset |
| Technology | Existing MFA methods | Verified ID + IDV providers + Face Check |
| Security level | Medium | High (government ID + biometric proofing) |

## Configuration Objects

| Object | Description | Parent/Dependency |
|---|---|---|
| **Identity Verification Profile** | Defines how account recovery works for a user population: which IDV provider performs verification, recovery mode (Evaluation/Production), target user groups, and account validation rules. Multiple profiles supported for different populations. | Verified ID, Face Check, IDV provider subscription |
| **Identity Verification Provider (IDV)** | Third-party service subscribed through the Microsoft Security Store that validates user identity using government-issued documents and biometric verification. Covers 192 countries/regions. | Azure subscription (for pay-as-you-go billing) |
| **Recovery Mode** | Profile setting controlling behavior: **Evaluation** (test flow without actual recovery) or **Production** (full recovery with TAP issuance). | Identity Verification Profile |
| **Account Validation Rules** | Claim matching configuration: maps IDV provider claims (firstName, lastName) to Entra user properties. Supports Exact or Relaxed match confidence. | Identity Verification Profile |
| **Custom Authentication Extension** | Optional Azure Function, Logic App, or REST API that validates IDV claims against organizational data (HRIS, employee directory) during recovery for additional assurance. | Identity Verification Profile, Azure Function/Logic App |
| **Temporary Access Pass (TAP)** | Time-limited passcode issued after successful recovery, allowing the user to sign in and register new authentication methods (passkeys, MFA). | Authentication Methods Policy |

## Authentication Methods Relevant to Recovery

| Method | Primary Auth | MFA | SSPR | Account Recovery |
|---|---|---|---|---|
| Passkey (FIDO2) | Yes | Yes | No | No |
| Microsoft Authenticator | Yes | Yes | Yes | No |
| Verified ID | No | No | No | **Yes** |
| Temporary Access Pass (TAP) | Yes | Yes | No | Issued after recovery |
| SMS | Yes | Yes | Yes | No |
| Email OTP | No | No | Yes | No |

## Portal Paths

| Task | Path |
|---|---|
| Account Recovery overview | **Entra admin center** > **Entra ID** > **Account recovery** |
| Create/manage profiles | **Account recovery** > **Profiles** tab > **Add** |
| Subscribe to IDV provider | **Account recovery** > **Profiles** > **Add** > Identity verification providers panel > **Get Solution** |
| View audit logs | **Account recovery** > **View audit logs** |
| Cost savings estimator | **Account recovery** > Overview > **Estimate savings** |
| Verify user profiles | **Entra ID** > **Users** > Select user > **Edit properties** (check First Name, Last Name) |
| Authentication Methods policy | **Protection** > **Authentication methods** > **Policies** |
| Enable passkeys | **Authentication methods** > **Policies** > **Passkey (FIDO2)** > Enable |
| Temporary Access Pass policy | **Authentication methods** > **Policies** > **Temporary Access Pass** |
| Verified ID setup | **Verified ID** > **Overview** |
| Face Check setup | **Verified ID** > **Face Check** |

## Account Recovery Flow

```
1. User at sign-in → "Can't access your account?"
2. System checks identity verification profiles → finds matching profile
3. User redirected to IDV provider
4. IDV provider verifies government-issued ID (document scan + fraud detection)
5. Liveness check + facial recognition (biometric match)
6. Verified ID credential issued → stored in Microsoft Authenticator
7. User presents Verified ID to Entra ID
8. Account validation: match claims (firstName, lastName) against Entra user properties
9. (Optional) Custom authentication extension validates against HRIS/employee directory
10. Temporary Access Pass issued to user
11. User signs in with TAP → registers new passkey and/or MFA methods
12. Account fully recovered
```

## Configuration Relationships

```
Account Recovery
├── Identity Verification Profile (per user population)
│   ├── Recovery Mode: Evaluation | Production
│   ├── User Groups: Include / Exclude
│   ├── IDV Provider (subscribed via Microsoft Security Store)
│   │   └── Government ID verification + biometric matching
│   ├── Account Validation
│   │   ├── Claim Mapping: firstName → First Name, lastName → Last Name
│   │   ├── Match Confidence: Exact | Relaxed
│   │   └── Custom Authentication Extension (optional)
│   │       └── Azure Function / Logic App / REST API
│   └── Output: Temporary Access Pass
├── Dependencies
│   ├── Microsoft Entra Verified ID (authority + linked domain)
│   ├── Face Check (biometric verification)
│   ├── Authentication Methods Policy
│   │   ├── Temporary Access Pass: Enabled
│   │   └── Passkey (FIDO2): Enabled (recommended post-recovery)
│   └── Microsoft Security Store subscription (IDV provider)
└── Audit & Monitoring
    └── Account Recovery audit logs
```

## Licensing

| License | Provides |
|---|---|
| **Microsoft Entra ID P1** | Account Recovery capability |
| **Microsoft Entra Suite** | Includes P2 + all Entra products |
| **Azure subscription** | Required for IDV provider billing (pay-as-you-go via Microsoft Security Store) |

## Required Admin Roles

| Role | Permissions |
|---|---|
| **Authentication Administrator** | Configure account recovery, create/manage identity verification profiles |
| **User Administrator** | Verify and update user profile properties (First Name, Last Name) |
| **Contributor / Billing Administrator** | Subscribe to IDV providers in Microsoft Security Store (Azure subscription) |
| **Global Administrator** | Full access to all settings |

> [!IMPORTANT]
> User profiles must have **First Name** and **Last Name** properties populated and matching the user's government-issued ID. The Display Name is NOT used in account recovery matching. Verify these properties before enabling recovery for any user population.

> [!NOTE]
> Start with **Evaluation mode** when deploying account recovery. This allows testing the full identity verification flow without actually recovering accounts. Switch to Production mode only after confirming the flow works correctly for your pilot users.
