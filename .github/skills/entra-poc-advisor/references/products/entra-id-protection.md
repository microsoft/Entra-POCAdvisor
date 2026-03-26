# Entra ID Protection — Product Reference

## Overview

Microsoft Entra ID Protection uses machine learning and Microsoft threat intelligence to detect identity-based risks in real time. It identifies compromised credentials, anomalous sign-in patterns, and suspicious user behavior, then enables automated remediation through risk-based Conditional Access policies. ID Protection covers both sign-in risk (is this authentication attempt suspicious?) and user risk (has this user's identity been compromised?).

Use Entra ID Protection when the POC requires risk-based access controls, automated threat response for identity attacks, risky user investigation, or MFA registration enforcement.

## Configuration Objects

| Object | Description | Parent/Dependency |
|---|---|---|
| **Risk Detection** | An individual risk event detected by the system (e.g., leaked credentials, anonymous IP, atypical travel). Aggregated into user risk and sign-in risk levels. | None (system-generated) |
| **Risky User** | A user whose aggregated risk level (low/medium/high) indicates potential compromise. Risk persists until dismissed or remediated. | Risk Detections |
| **Risky Sign-in** | A sign-in event flagged with risk. Contains the sign-in risk level and the specific detections that triggered it. | Risk Detections |
| **User Risk Policy** | Built-in policy that triggers remediation (password change) when user risk reaches a threshold. Superseded by Conditional Access risk policies. | Risky Users |
| **Sign-in Risk Policy** | Built-in policy that triggers MFA when sign-in risk reaches a threshold. Superseded by Conditional Access risk policies. | Risky Sign-ins |
| **MFA Registration Policy** | Policy that requires users to register for MFA proactively, ensuring self-remediation is available when risk policies trigger. | None |
| **Risk-based Conditional Access** | Conditional Access policies using user risk level or sign-in risk level as conditions. Recommended over the built-in risk policies for more granular control. | Conditional Access, ID Protection |

## Graph API Endpoints

### Risk Detections

| Operation | Endpoint | API Version |
|---|---|---|
| List risk detections | `GET /identityProtection/riskDetections` | v1.0 |
| Get risk detection | `GET /identityProtection/riskDetections/{id}` | v1.0 |

### Risky Users

| Operation | Endpoint | API Version |
|---|---|---|
| List risky users | `GET /identityProtection/riskyUsers` | v1.0 |
| Get risky user | `GET /identityProtection/riskyUsers/{id}` | v1.0 |
| List risk history | `GET /identityProtection/riskyUsers/{id}/history` | v1.0 |
| Confirm user compromised | `POST /identityProtection/riskyUsers/confirmCompromised` | v1.0 |
| Dismiss user risk | `POST /identityProtection/riskyUsers/dismiss` | v1.0 |

### Risky Sign-ins

| Operation | Endpoint | API Version |
|---|---|---|
| List risky sign-ins | `GET /identityProtection/riskyServicePrincipals` | v1.0 |
| List risky sign-in events | `GET /reports/security/getAttackSimulationSignInSummary` | beta |

### Service Principal Risk

| Operation | Endpoint | API Version |
|---|---|---|
| List risky service principals | `GET /identityProtection/riskyServicePrincipals` | v1.0 |
| Get risky service principal | `GET /identityProtection/riskyServicePrincipals/{id}` | v1.0 |

### MFA and Authentication Methods

| Operation | Endpoint | API Version |
|---|---|---|
| Get auth methods registration summary | `GET /reports/authenticationMethods/userRegistrationDetails` | v1.0 |
| MFA registration details per user | `GET /reports/authenticationMethods/userRegistrationDetails?$filter=userPrincipalName eq '{upn}'` | v1.0 |
| Authentication methods usage | `GET /reports/authenticationMethods/usersRegisteredByFeature` | v1.0 |

### Sign-in Logs (risk context)

| Operation | Endpoint | API Version |
|---|---|---|
| List sign-ins with risk | `GET /auditLogs/signIns?$filter=riskLevelDuringSignIn ne 'none'` | v1.0 |

## Common Read Queries

**List high-risk users:**
```
GET /v1.0/identityProtection/riskyUsers?$filter=riskLevel eq 'high'
  → Returns users with high aggregated risk; check riskState for "atRisk" vs. "remediated"
```

**List recent risk detections (last 7 days):**
```
GET /v1.0/identityProtection/riskDetections?$filter=detectedDateTime ge {7daysAgo}&$orderby=detectedDateTime desc&$top=50
  → Look for: riskEventType, riskLevel, userDisplayName, ipAddress
```

**Check MFA registration status for pilot group:**
```
GET /v1.0/reports/authenticationMethods/userRegistrationDetails?$filter=isMfaRegistered eq false
  → Users without MFA cannot self-remediate; these must register before risk policies are enforced
```

**Query risky sign-ins:**
```
GET /v1.0/auditLogs/signIns?$filter=riskLevelDuringSignIn eq 'high'&$top=25&$orderby=createdDateTime desc
```

**Get risk detection types summary:**
```
GET /v1.0/identityProtection/riskDetections?$select=riskEventType&$top=999
  → Aggregate by riskEventType to understand the threat landscape
```

## Configuration Relationships

```
ID Protection
├── Risk Detection Engine (system-managed)
│   ├── Sign-in Risk Detections
│   │   ├── Anonymous IP address
│   │   ├── Atypical travel
│   │   ├── Malware-linked IP
│   │   ├── Unfamiliar sign-in properties
│   │   ├── Password spray
│   │   └── Token issuer anomaly
│   └── User Risk Detections
│       ├── Leaked credentials
│       ├── Threat intelligence (Microsoft)
│       └── Anomalous user activity
├── Risky Users (aggregated user risk)
│   └── Risk history per user
├── Risky Sign-ins (per sign-in risk)
├── Risk Policies (built-in, legacy)
│   ├── User Risk Policy → remediation: password change
│   └── Sign-in Risk Policy → remediation: MFA
├── Conditional Access (recommended)
│   ├── CA policy: user risk condition → grant: password change + MFA
│   └── CA policy: sign-in risk condition → grant: MFA
└── MFA Registration Policy
    └── Ensures users can self-remediate
```

Risk-based Conditional Access policies are the recommended approach over the built-in risk policies. CA policies provide more granular control (e.g., different policies per user group, combined with device compliance or location conditions). Built-in risk policies and CA risk policies should not be used simultaneously for the same users.

## Licensing

| License | Provides |
|---|---|
| **Microsoft Entra ID P2** | Full ID Protection: risk detections, risky users, risk policies, risk-based CA |
| **Microsoft Entra Suite** | Full ID Protection (includes Private Access, Internet Access, ID Governance, Verified ID) |
| **Microsoft Entra ID P1** | Sign-in logs only (no risk detections, no risk policies) |

All users covered by risk policies must have P2 or Suite licenses assigned.

## Required Admin Roles

| Role | Permissions |
|---|---|
| **Global Administrator** | Full access to all ID Protection settings |
| **Security Administrator** | Can configure risk policies, view and remediate risky users, manage CA risk policies |
| **Security Operator** | Can view risk reports and dismiss/confirm user risk |
| **Security Reader** | Read-only access to risk detections, risky users, and reports |
| **Global Reader** | Read-only access for validation and gap analysis |

> [!IMPORTANT]
> Users must be registered for MFA before user risk policies can enforce self-remediation (password change requires MFA). Deploy the MFA registration policy or verify MFA registration status before enabling risk policies.
