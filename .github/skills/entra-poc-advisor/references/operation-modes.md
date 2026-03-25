# Operation Modes

Detailed definitions and transition rules for the three operation modes.

## Mode Definitions

### Mode 1: Guidance Only

**Connection:** None
**Tenant Access:** None
**Use When:** The administrator wants advisory guidance, documentation, or scripts without connecting to a tenant.

Capabilities:
- Discuss requirements and recommend Entra Suite products/features
- Generate step-by-step configuration documentation (Markdown)
- Generate architecture and relationship diagrams (Mermaid)
- Generate PowerShell automation scripts (for later execution)
- Provide pre-defined scenario templates and walkthroughs
- Explain product concepts, licensing, and architecture

Limitations:
- Cannot read tenant configuration
- Cannot validate prerequisites against the actual tenant
- Cannot produce gap analysis with real tenant data
- Generated scripts use placeholder values for tenant-specific parameters

### Mode 2: Read-Only

**Connection:** Microsoft MCP Server for Enterprise (authenticated)
**Tenant Access:** Read only
**Use When:** The administrator wants to assess their current tenant state, validate prerequisites, or produce gap analysis reports.

Includes all Guidance Only capabilities, plus:
- Authenticate to tenant via Entra ID OAuth (delegated)
- Validate prerequisites: licenses, roles, permissions, feature activation
- Read current tenant configuration for any Entra component
- Produce gap analysis reports comparing current state to target
- Validate existing configuration against POC requirements
- Identify misconfigurations and missing settings
- Generate scripts with tenant-specific values populated from live data

MCP Tools Used:
- `microsoft_graph_suggest_queries` -- discover relevant Graph API endpoints
- `microsoft_graph_get` -- execute read-only Graph API calls
- `microsoft_graph_list_properties` -- discover entity schemas

### Mode 3: Read-Write

**Connection:** Microsoft MCP Server for Enterprise (authenticated)
**Tenant Access:** Read + write artifact generation
**Use When:** The administrator wants to generate ready-to-execute configuration artifacts with full tenant awareness.

Includes all Read-Only capabilities, plus:
- Generate PowerShell scripts pre-populated with tenant-specific values (group IDs, user UPNs, existing resource references)
- Generate step-by-step portal instructions that reference the current tenant state
- Produce configuration artifacts that account for existing resources (skip already-configured items)

Current constraint: The Microsoft MCP Server for Enterprise is read-only. Write operations are handled by:
1. PowerShell scripts the admin reviews and executes
2. Step-by-step portal instructions for manual configuration
3. NEVER direct writes through the MCP Server

## Mode Transition Rules

### Starting a Session

At the start of every session, ask the administrator:

> Which operation mode would you like to use for this session?
>
> 1. **Guidance Only** -- No tenant connection. I provide advice, documentation, and scripts.
> 2. **Read-Only** -- I connect to your tenant to read configuration. No changes are made.
> 3. **Read-Write** -- I read your tenant and generate executable configuration artifacts.

If the administrator does not specify, default to **Guidance Only**.

### Escalating Modes

- **Guidance Only to Read-Only:** The administrator must explicitly request read access. Verify that Microsoft MCP Server for Enterprise is connected before proceeding.
- **Read-Only to Read-Write:** The administrator must explicitly request write artifact generation. Display the consent prompt:

> **Read-Write mode consent:**
>
> In this mode, I will generate PowerShell scripts and portal instructions that are ready to execute against your tenant. These artifacts will contain tenant-specific values from your live configuration.
>
> - I will NOT make any changes to your tenant directly
> - All generated scripts include -WhatIf support for dry-run execution
> - You review and execute all scripts yourself
>
> Do you want to proceed with Read-Write mode?

- **Any mode to a lower mode:** Always allowed without consent. Inform the administrator of the mode change.

### Mode Violations

If the administrator requests an action that requires a higher mode:

1. Inform them which mode is required
2. Explain what the higher mode enables
3. Ask if they want to switch modes
4. Do NOT perform the action until mode is explicitly changed

Example: If in Guidance Only mode and the admin asks "Check my tenant licenses":

> That requires Read-Only mode so I can connect to your tenant via the Microsoft MCP Server for Enterprise. Would you like to switch to Read-Only mode?
