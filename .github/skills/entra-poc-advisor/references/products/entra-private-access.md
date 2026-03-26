# Entra Private Access — Product Reference

## Overview

Microsoft Entra Private Access provides zero trust network access (ZTNA) to private applications and resources without requiring a traditional VPN. It replaces legacy VPN with identity-centric, per-app access controls that integrate with Conditional Access. Traffic flows from the Global Secure Access Client through the Microsoft Entra cloud service to on-premises connectors, which proxy connections to internal resources.

Use Entra Private Access when the POC requires secure remote access to internal web apps, file shares, RDP/SSH servers, or any TCP/UDP resource on the corporate network.

## Configuration Objects

| Object | Description | Parent/Dependency |
|---|---|---|
| **Quick Access Application** | A single enterprise app that provides broad access to all configured private resources via FQDN/IP segments. Fastest path to replace VPN. | Traffic Forwarding Profile (Private Access) |
| **Per-App Enterprise Application** | Individual enterprise app per private resource with dedicated application segments and access controls. Enables granular zero trust. | Traffic Forwarding Profile (Private Access) |
| **Application Segment** | Defines a destination (FQDN, IP, IP range, CIDR) and port/protocol combination that the service routes to a connector. Attached to Quick Access or a Per-App app. | Quick Access or Per-App Application |
| **Connector** | Windows service installed on an on-premises server that receives traffic from the Entra cloud edge and forwards it to internal resources. | Connector Group |
| **Connector Group** | Logical grouping of connectors. Apps are assigned to a connector group to control which connectors handle their traffic. Enables network segmentation. | None (top-level) |
| **Private DNS** | Configuration that maps internal DNS suffixes to connector groups, enabling the GSA Client to resolve internal hostnames through the connector. | Connector Group |

## Graph API Endpoints

### Connectors and Connector Groups

| Operation | Endpoint | API Version |
|---|---|---|
| List connectors | `GET /onPremisesPublishingProfiles/applicationProxy/connectors` | beta |
| Get connector | `GET /onPremisesPublishingProfiles/applicationProxy/connectors/{id}` | beta |
| List connector groups | `GET /onPremisesPublishingProfiles/applicationProxy/connectorGroups` | beta |
| Create connector group | `POST /onPremisesPublishingProfiles/applicationProxy/connectorGroups` | beta |
| Assign connector to group | `POST /onPremisesPublishingProfiles/applicationProxy/connectorGroups/{groupId}/members/$ref` | beta |
| List connectors in group | `GET /onPremisesPublishingProfiles/applicationProxy/connectorGroups/{groupId}/members` | beta |

### Private Access Applications

| Operation | Endpoint | API Version |
|---|---|---|
| List Private Access apps | `GET /networkAccess/connectivity/remoteNetworks` | beta |
| Get application segments | `GET /applications/{appId}/onPremisesPublishing` | beta |
| Update application segment | `PATCH /applications/{appId}/onPremisesPublishing` | beta |

### Traffic Forwarding

| Operation | Endpoint | API Version |
|---|---|---|
| List forwarding profiles | `GET /networkAccess/forwardingProfiles` | beta |
| Enable Private Access profile | `PATCH /networkAccess/forwardingProfiles/{id}` | beta |

## Common Read Queries

**Check connector health:**
```
GET /beta/onPremisesPublishingProfiles/applicationProxy/connectors
  → Look for: status == "active", machineName, externalIp
```

**List connector groups and their members:**
```
GET /beta/onPremisesPublishingProfiles/applicationProxy/connectorGroups?$expand=members
```

**Verify Private Access traffic profile is enabled:**
```
GET /beta/networkAccess/forwardingProfiles
  → Filter for profile with trafficForwardingType == "private" and state == "enabled"
```

**Check Quick Access enterprise app assignment:**
```
GET /v1.0/servicePrincipals?$filter=displayName eq 'Quick Access'
GET /v1.0/servicePrincipals/{spId}/appRoleAssignedTo
```

## Configuration Relationships

```
Traffic Forwarding Profile (Private Access)
├── Quick Access Application
│   ├── Application Segment (FQDN / IP + Port)
│   ├── Application Segment (CIDR + Port range)
│   └── Connector Group assignment
├── Per-App Enterprise Application
│   ├── Application Segment (FQDN + Port)
│   ├── Connector Group assignment
│   ├── User/Group assignment
│   └── Conditional Access policy (targets this app)
└── Private DNS
    ├── DNS Suffix → Connector Group mapping
    └── Used by GSA Client for internal name resolution
```

Connector Groups are shared infrastructure — multiple apps can reference the same group. Connectors must be healthy (status: active) for traffic to flow. If all connectors in a group are down, apps assigned to that group become unreachable.

## Licensing

| License | Provides |
|---|---|
| **Microsoft Entra Suite** | Full Private Access functionality (includes Internet Access, ID Protection, ID Governance, Verified ID) |
| **Microsoft Entra Private Access** (standalone) | Private Access only |

Licenses must be assigned to users who will access private resources through the GSA Client. Connector servers do not require per-user licenses.

## Required Admin Roles

| Role | Permissions |
|---|---|
| **Global Administrator** | Full configuration access |
| **Security Administrator** | Can manage GSA settings and Conditional Access policies |
| **Application Administrator** | Can manage connectors, connector groups, and enterprise app assignments |
| **Global Secure Access Administrator** | Can manage all Global Secure Access settings including traffic profiles and Private Access |
| **Global Reader** | Read-only access for validation and gap analysis |

> [!NOTE]
> Connector installation requires local administrator rights on the Windows Server. The installing user must also have Application Administrator or Global Administrator role in Entra ID.
