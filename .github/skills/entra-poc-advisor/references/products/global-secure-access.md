# Global Secure Access — Product Reference

## Overview

Global Secure Access (GSA) is the unified network access control plane in Microsoft Entra that underpins both Entra Private Access and Entra Internet Access. It provides the traffic forwarding infrastructure, the GSA Client, remote network connectivity, traffic logging, and centralized settings. GSA must be activated in a tenant before Private Access or Internet Access can function.

Use this reference when the POC involves GSA activation, traffic forwarding profile management, GSA Client deployment, remote network configuration, or traffic log analysis.

## Configuration Objects

| Object | Description | Parent/Dependency |
|---|---|---|
| **GSA Settings** | Tenant-level activation and configuration for Global Secure Access. Must be enabled before any GSA feature works. | None (tenant-level) |
| **Traffic Forwarding Profile** | Controls which traffic types are routed through GSA. Three built-in profiles: Microsoft 365, Private Access, Internet Access. Each can be independently enabled/disabled. | GSA Settings (must be active) |
| **Forwarding Policy** | Rules within a traffic forwarding profile that define specific traffic selectors (destinations, ports, protocols) for routing. | Traffic Forwarding Profile |
| **GSA Client** | Windows agent installed on endpoint devices. Creates a secure tunnel to the Entra cloud edge and routes traffic per the enabled forwarding profiles. | Traffic Forwarding Profile (at least one enabled) |
| **Remote Network** | Site-to-site connectivity from a branch office or data center to GSA via IPSec tunnel. Alternative to per-device GSA Client deployment. | GSA Settings |
| **Device Link** | IPSec tunnel configuration within a remote network, specifying the CPE device, bandwidth, and tunnel parameters. | Remote Network |
| **Traffic Logs** | Audit logs of all traffic processed by GSA, including source user, destination, action (allow/block), and matched policy. | GSA Settings |

## Graph API Endpoints

### Settings

| Operation | Endpoint | API Version |
|---|---|---|
| Get GSA settings | `GET /networkAccess/settings` | beta |
| Update GSA settings | `PATCH /networkAccess/settings` | beta |

### Traffic Forwarding Profiles

| Operation | Endpoint | API Version |
|---|---|---|
| List forwarding profiles | `GET /networkAccess/forwardingProfiles` | beta |
| Get forwarding profile | `GET /networkAccess/forwardingProfiles/{id}` | beta |
| Update forwarding profile | `PATCH /networkAccess/forwardingProfiles/{id}` | beta |
| List forwarding policies | `GET /networkAccess/forwardingProfiles/{id}/policies` | beta |

### Remote Networks

| Operation | Endpoint | API Version |
|---|---|---|
| List remote networks | `GET /networkAccess/connectivity/remoteNetworks` | beta |
| Get remote network | `GET /networkAccess/connectivity/remoteNetworks/{id}` | beta |
| Create remote network | `POST /networkAccess/connectivity/remoteNetworks` | beta |
| List device links | `GET /networkAccess/connectivity/remoteNetworks/{id}/deviceLinks` | beta |
| Create device link | `POST /networkAccess/connectivity/remoteNetworks/{id}/deviceLinks` | beta |

### Traffic Logs

| Operation | Endpoint | API Version |
|---|---|---|
| List traffic logs | `GET /networkAccess/logs/traffic` | beta |
| Get traffic log entry | `GET /networkAccess/logs/traffic/{id}` | beta |

### Alerts

| Operation | Endpoint | API Version |
|---|---|---|
| List alerts | `GET /networkAccess/alerts` | beta |

## Common Read Queries

**Check if GSA is activated:**
```
GET /beta/networkAccess/settings
  → Look for: isEnabled == true
```

**List all forwarding profiles and their state:**
```
GET /beta/networkAccess/forwardingProfiles
  → Returns three profiles with trafficForwardingType: "m365", "private", "internet"
  → Check state: "enabled" or "disabled" for each
```

**Get forwarding policies within a profile:**
```
GET /beta/networkAccess/forwardingProfiles/{id}/policies
  → Returns traffic selectors (destinations, ports) within the profile
```

**List remote networks and tunnel status:**
```
GET /beta/networkAccess/connectivity/remoteNetworks?$expand=deviceLinks
  → Look for: deviceLinks[].tunnelConfiguration, deviceLinks[].bgpConfiguration
```

**Query recent traffic logs for a specific user:**
```
GET /beta/networkAccess/logs/traffic?$filter=userId eq '{userId}'&$top=50&$orderby=createdDateTime desc
```

**Query blocked traffic entries:**
```
GET /beta/networkAccess/logs/traffic?$filter=action eq 'block'&$top=50&$orderby=createdDateTime desc
```

## Configuration Relationships

```
GSA Settings (tenant-level activation)
├── Traffic Forwarding Profile: Microsoft 365
│   ├── Forwarding policies (Exchange, SharePoint, Teams destinations)
│   └── Requires: Entra ID P1 minimum
├── Traffic Forwarding Profile: Private Access
│   ├── Forwarding policies (configured app segments)
│   ├── Requires: Entra Private Access license
│   └── Depends on: Connectors, Connector Groups, App Segments
├── Traffic Forwarding Profile: Internet Access
│   ├── Forwarding policies (all internet traffic)
│   ├── Requires: Entra Internet Access license
│   └── Depends on: Filtering Policies, Security Profiles
├── GSA Client (per-device)
│   ├── Routes traffic per enabled profiles
│   ├── Requires: Windows 10/11 22H2+
│   └── Authenticated with user's Entra ID credentials
├── Remote Networks (per-site)
│   ├── Device Link (IPSec tunnel)
│   │   ├── Tunnel configuration (IKE, IPSec parameters)
│   │   └── BGP configuration (optional)
│   └── Forwarding profile association
└── Traffic Logs
    └── Records all processed traffic with user, destination, action, policy
```

GSA is the prerequisite for everything. If GSA settings show `isEnabled: false`, no Private Access or Internet Access feature will function. Traffic forwarding profiles are the next dependency — at least one profile must be enabled and the GSA Client or a remote network must be connected for traffic to flow.

## Licensing

| License | GSA Features Enabled |
|---|---|
| **Microsoft Entra ID P1** | GSA activation, Microsoft 365 traffic profile only |
| **Microsoft Entra Private Access** | Private Access traffic profile + connectors |
| **Microsoft Entra Internet Access** | Internet Access traffic profile + filtering |
| **Microsoft Entra Suite** | All profiles + all Private Access + all Internet Access features |

The Microsoft 365 traffic profile is available with any Entra ID P1 license. Private Access and Internet Access profiles require their respective product licenses.

## Required Admin Roles

| Role | Permissions |
|---|---|
| **Global Administrator** | Full configuration access including GSA activation |
| **Global Secure Access Administrator** | Can manage all GSA settings, profiles, remote networks, and view logs |
| **Security Administrator** | Can manage Conditional Access integration and security settings |
| **Security Reader** | Read-only access to traffic logs and settings |
| **Global Reader** | Read-only access for validation and gap analysis |

> [!NOTE]
> GSA activation is a one-time tenant-level operation. Once activated, it cannot be deactivated through the admin center. Plan accordingly for POC tenants.

> [!WARNING]
> Enabling the Microsoft 365 traffic forwarding profile routes Exchange, SharePoint, and Teams traffic through GSA. Test thoroughly in the POC before enabling in production, as misconfiguration can disrupt Microsoft 365 connectivity.
