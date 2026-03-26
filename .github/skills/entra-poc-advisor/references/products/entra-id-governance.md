# Entra ID Governance — Product Reference

## Overview

Microsoft Entra ID Governance automates the identity lifecycle and access management. It covers access reviews (periodic certification of who has access to what), entitlement management (self-service access request and approval workflows), lifecycle workflows (automated joiner/mover/leaver processes), and Privileged Identity Management (just-in-time activation of admin roles). Together these features enforce least privilege and ensure access is appropriate, time-limited, and auditable.

Use Entra ID Governance when the POC requires automated access certification, self-service access request portals, employee lifecycle automation, or just-in-time privileged role activation.

## Configuration Objects

| Object | Description | Parent/Dependency |
|---|---|---|
| **Access Review Definition** | Recurring or one-time review that asks reviewers to certify access to groups, apps, or roles. Defines scope, reviewers, duration, and auto-actions. | None (top-level) |
| **Access Review Instance** | A specific occurrence of an access review definition. Contains the decisions made by reviewers. | Access Review Definition |
| **Catalog** | Container for resources (groups, apps, roles) that can be packaged into access packages. Controls resource visibility and delegation. | None (top-level) |
| **Access Package** | Bundles one or more resource roles from a catalog. Users request access packages to receive bundled resources. | Catalog |
| **Assignment Policy** | Defines who can request an access package, approval workflow, access duration, and review settings. | Access Package |
| **Access Package Assignment** | Record of a user who has been granted an access package. Tracks start/end dates and status. | Access Package + Assignment Policy |
| **Lifecycle Workflow** | Automated workflow triggered by employee lifecycle events (hire, role change, departure). Executes tasks like adding to groups, sending emails, or removing access. | None (top-level) |
| **Workflow Task** | Individual action within a lifecycle workflow (e.g., add user to group, generate TAP, send email, remove access). | Lifecycle Workflow |
| **PIM Role Assignment** | Just-in-time eligible or active role assignment with time-bound activation, approval, and MFA requirements. | PIM role settings |
| **PIM Role Settings** | Configuration for a specific role: activation duration, approval requirements, MFA enforcement, notification rules. | None (per-role) |

## Graph API Endpoints

### Access Reviews

| Operation | Endpoint | API Version |
|---|---|---|
| List access review definitions | `GET /identityGovernance/accessReviews/definitions` | v1.0 |
| Get access review definition | `GET /identityGovernance/accessReviews/definitions/{id}` | v1.0 |
| Create access review | `POST /identityGovernance/accessReviews/definitions` | v1.0 |
| List instances | `GET /identityGovernance/accessReviews/definitions/{id}/instances` | v1.0 |
| List decisions | `GET /identityGovernance/accessReviews/definitions/{id}/instances/{instanceId}/decisions` | v1.0 |

### Entitlement Management

| Operation | Endpoint | API Version |
|---|---|---|
| List catalogs | `GET /identityGovernance/entitlementManagement/catalogs` | v1.0 |
| Create catalog | `POST /identityGovernance/entitlementManagement/catalogs` | v1.0 |
| List catalog resources | `GET /identityGovernance/entitlementManagement/catalogs/{id}/resources` | v1.0 |
| Add resource to catalog | `POST /identityGovernance/entitlementManagement/catalogs/{id}/resourceRequests` | v1.0 |
| List access packages | `GET /identityGovernance/entitlementManagement/accessPackages` | v1.0 |
| Create access package | `POST /identityGovernance/entitlementManagement/accessPackages` | v1.0 |
| List assignment policies | `GET /identityGovernance/entitlementManagement/assignmentPolicies` | v1.0 |
| Create assignment policy | `POST /identityGovernance/entitlementManagement/assignmentPolicies` | v1.0 |
| List assignments | `GET /identityGovernance/entitlementManagement/assignments` | v1.0 |

### Lifecycle Workflows

| Operation | Endpoint | API Version |
|---|---|---|
| List workflows | `GET /identityGovernance/lifecycleWorkflows/workflows` | v1.0 |
| Get workflow | `GET /identityGovernance/lifecycleWorkflows/workflows/{id}` | v1.0 |
| Create workflow | `POST /identityGovernance/lifecycleWorkflows/workflows` | v1.0 |
| List workflow runs | `GET /identityGovernance/lifecycleWorkflows/workflows/{id}/runs` | v1.0 |
| List task definitions | `GET /identityGovernance/lifecycleWorkflows/taskDefinitions` | v1.0 |

### Privileged Identity Management

| Operation | Endpoint | API Version |
|---|---|---|
| List role eligibility schedules | `GET /roleManagement/directory/roleEligibilityScheduleRequests` | v1.0 |
| List role assignment schedules | `GET /roleManagement/directory/roleAssignmentScheduleRequests` | v1.0 |
| List active role assignments | `GET /roleManagement/directory/roleAssignmentScheduleInstances` | v1.0 |
| Get PIM role settings | `GET /policies/roleManagementPolicies` | v1.0 |
| Get PIM role setting rules | `GET /policies/roleManagementPolicies/{id}/rules` | v1.0 |

## Common Read Queries

**List all active access reviews:**
```
GET /v1.0/identityGovernance/accessReviews/definitions?$filter=status eq 'InProgress'
```

**List catalogs and their resource counts:**
```
GET /v1.0/identityGovernance/entitlementManagement/catalogs?$expand=resources($count=true)
```

**List access packages in a catalog:**
```
GET /v1.0/identityGovernance/entitlementManagement/accessPackages?$filter=catalog/id eq '{catalogId}'
```

**List users with eligible PIM role assignments:**
```
GET /v1.0/roleManagement/directory/roleEligibilityScheduleInstances
```

**Get PIM role settings (activation rules, approval config):**
```
GET /v1.0/policies/roleManagementPolicies?$filter=scopeId eq '/' and scopeType eq 'DirectoryRole'
  → Then: GET /v1.0/policies/roleManagementPolicies/{id}/rules
```

## Configuration Relationships

```
ID Governance
├── Access Reviews
│   ├── Review Definition (scope: group, app, or role)
│   │   ├── Instances (recurring occurrences)
│   │   │   └── Decisions (approve/deny per user)
│   │   ├── Reviewers (manager, owner, self, specific users)
│   │   └── Auto-actions (remove access, apply recommendations)
│   └── Can review PIM role assignments
├── Entitlement Management
│   ├── Catalog
│   │   ├── Resources (groups, apps, SharePoint sites, roles)
│   │   └── Catalog owners (delegated management)
│   ├── Access Package
│   │   ├── Resource roles (from catalog)
│   │   ├── Assignment Policy
│   │   │   ├── Request settings (who can request)
│   │   │   ├── Approval stages (approvers, escalation)
│   │   │   ├── Access duration (expiration)
│   │   │   └── Review settings (periodic re-certification)
│   │   └── Assignments (granted users)
│   └── Connected organizations (external user access)
├── Lifecycle Workflows
│   ├── Workflow (trigger: joiner/mover/leaver)
│   │   ├── Execution conditions (scope, trigger)
│   │   ├── Tasks (add to group, generate TAP, send email, disable account, etc.)
│   │   └── Runs (execution history)
│   └── Depends on: employeeHireDate, employeeLeaveDateTime in user profile
└── Privileged Identity Management (PIM)
    ├── Role settings (per directory role)
    │   ├── Activation: max duration, require MFA, require justification
    │   ├── Approval: require approval, designated approvers
    │   └── Notification: on activation, on assignment
    ├── Eligible assignments (just-in-time)
    └── Active assignments (permanent or time-bound)
```

## Licensing

| License | Provides |
|---|---|
| **Microsoft Entra ID Governance** (standalone) | Access Reviews, Entitlement Management, Lifecycle Workflows, PIM |
| **Microsoft Entra Suite** | Full ID Governance (includes Private Access, Internet Access, ID Protection, Verified ID) |
| **Microsoft Entra ID P2** | PIM and Access Reviews only (not Entitlement Management or Lifecycle Workflows) |

For full entitlement management and lifecycle workflows, either ID Governance standalone or Entra Suite is required.

## Required Admin Roles

| Role | Permissions |
|---|---|
| **Global Administrator** | Full access to all governance features |
| **Identity Governance Administrator** | Access Reviews, Entitlement Management, Lifecycle Workflows |
| **Privileged Role Administrator** | PIM role assignment and settings management |
| **User Administrator** | Can manage user properties needed by Lifecycle Workflows (e.g., employeeHireDate) |
| **Global Reader** | Read-only access for validation and gap analysis |

> [!NOTE]
> Lifecycle Workflows depend on the `employeeHireDate` and `employeeLeaveDateTime` attributes being populated in user profiles. If these attributes are empty, joiner/leaver workflows will not trigger. Verify attribute population during prerequisites validation.
