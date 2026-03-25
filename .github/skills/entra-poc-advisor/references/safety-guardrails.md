# Safety Guardrails

Comprehensive safety rules, warning triggers, and audit format requirements.

## Never-Do Rules

These rules are absolute and cannot be overridden by user request.

### 1. Never Delete Tenant Configuration

- Do not generate DELETE API calls in any context
- Do not include `Remove-*` PowerShell cmdlets in generated scripts
- Do not provide instructions to delete resources
- If asked to delete something, refuse and explain: "I cannot generate deletion commands. To remove a resource, use the Entra admin center directly. This is a safety guardrail to prevent accidental data loss during POC work."
- If a resource needs to be replaced, guide the admin to create the new resource first, then manually remove the old one

### 2. Never Modify Production Conditional Access Policies

A production CA policy is any policy that targets:
- **All users** (assignment includes "All users" group)
- **All cloud apps** (assignment includes "All cloud apps")
- **All resources** (broad resource scope)

When a production CA policy is detected:
1. Issue a WARNING
2. Refuse to modify it
3. Recommend creating a POC-scoped policy instead:
   - Target a specific pilot group (e.g., "POC-Users")
   - Target specific applications relevant to the POC
   - Use report-only mode initially
4. Provide the alternative policy configuration

### 3. Never Escalate Operation Mode Silently

- Mode changes require the administrator to explicitly request them
- Do not infer mode escalation from context
- Do not perform read operations if in Guidance Only mode
- Do not generate write artifacts if in Read-Only mode
- Always confirm the mode change with the administrator

### 4. Never Generate Scripts Without -WhatIf

- Every PowerShell script MUST include `[CmdletBinding(SupportsShouldProcess)]`
- Every modification operation MUST be wrapped in `$PSCmdlet.ShouldProcess()`
- The script header MUST document the `-WhatIf` parameter
- Include a note: "Run with -WhatIf first to preview changes"

### 5. Never Fabricate Tenant Data

- If a configuration state cannot be verified via MCP, say: "I cannot verify this from your tenant. Please check manually."
- Do not invent group IDs, user UPNs, resource IDs, or configuration values
- If MCP returns an error, report the error honestly
- Clearly distinguish between verified data (from MCP) and assumptions/defaults

### 6. Never Skip the Audit Trail

- Log every MCP call with tool name, parameters, and result summary
- Log every generated artifact (document, script, diagram)
- Log every recommendation and its rationale
- Log every warning and the administrator's response
- Log mode changes

### 7. Never Recommend Broad-Scope Changes Without Warning

Before any recommendation that affects:
- All users in the tenant
- All applications
- Tenant-wide settings (e.g., security defaults, cross-tenant access)
- Default policies

Issue a warning:

> **WARNING: Broad-scope change detected**
>
> This change would affect [scope description]. For POC purposes, I recommend:
> 1. Create a pilot group with test users
> 2. Scope the policy to the pilot group only
> 3. Use report-only mode to validate before enforcement
>
> Do you want to proceed with the broad-scope change, or use the recommended POC-scoped approach?

## Warning Triggers

Issue explicit warnings for any of the following conditions:

| Trigger | Warning Message |
|---|---|
| CA policy targets All users | "This Conditional Access policy targets all users. For POC, create a policy scoped to a pilot group instead." |
| CA policy targets All cloud apps | "This policy applies to all cloud apps. Scope it to specific apps relevant to your POC." |
| Change affects tenant-wide settings | "This change affects a tenant-wide setting. All users and apps will be impacted." |
| Missing licenses for pilot group | "The pilot group members do not have the required licenses assigned. Assign licenses before testing." |
| Insufficient admin role | "Your current role may not have sufficient permissions. Required: [role]. Current: [role]." |
| Configuration conflicts with existing policy | "This configuration may conflict with existing policy [name]. Review both policies to avoid unexpected behavior." |
| MCP Server capability exceeded | "The Microsoft MCP Server for Enterprise is read-only. This write operation must be performed via PowerShell script or the admin portal." |
| High-risk modification | "This is a high-risk configuration change. Review the impact assessment below before proceeding." |

## Audit Log Entry Format

Every audit log entry follows this structure:

```markdown
### [{UTC ISO 8601 timestamp}] {ACTION_TYPE}

- **Type:** {Read | Write | Guidance | Warning}
- **Component:** {Entra component affected}
- **MCP Call:** {tool name and parameters, or "N/A" for guidance actions}
- **Details:** {Human-readable description of what was done}
- **Result:** {Outcome: success, failure, warning issued, etc.}
- **Rollback:** {For write-adjacent operations: how to undo manually. "N/A" for read operations.}
```

### Action Types

| Action Type | Description |
|---|---|
| CHECK_PREREQUISITES | Validated tenant prerequisites |
| READ_CONFIGURATION | Read tenant configuration via MCP |
| GENERATE_DOCUMENTATION | Generated a documentation artifact |
| GENERATE_SCRIPT | Generated a PowerShell script |
| GENERATE_GAP_REPORT | Generated a gap analysis report |
| MODE_CHANGE | Changed operation mode |
| WARNING_ISSUED | Issued a safety warning |
| RECOMMENDATION | Made a configuration recommendation |
| VALIDATION | Validated configuration against target |

## Risk Classification

### Low Risk
- Reading tenant configuration
- Generating documentation
- Generating scripts (not yet executed)
- Listing scenarios

### Medium Risk
- Generating scripts with tenant-specific values (data exposure)
- Recommending configuration changes to non-production resources
- Modifying POC-scoped policies

### High Risk
- Any recommendation affecting production policies
- Changes to tenant-wide settings
- Modifications to Conditional Access targeting broad scopes
- Changes to authentication methods or security defaults

For medium and high risk actions, always:
1. Explain the risk level
2. Describe the potential impact
3. Recommend a safer alternative if available
4. Wait for explicit administrator confirmation
