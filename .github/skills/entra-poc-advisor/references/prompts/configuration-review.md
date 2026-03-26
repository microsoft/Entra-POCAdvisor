# Configuration Review Template

## Goal

Guide an administrator through reviewing existing tenant configuration for correctness, security posture, and alignment with Microsoft best practices. Produce a review report with findings and recommendations.

## When to Use

- Admin has completed a scenario and wants to verify the configuration is correct
- Admin wants a security review of their current Entra configuration
- Admin is preparing for production rollout and needs a pre-flight check
- Admin inherited a tenant and wants to understand what is configured

## Requirements

- **Minimum mode**: Read-Only (MCP tools must be available for tenant reads)
- **Permissions**: The connected identity needs read access across Entra ID, Conditional Access, Global Secure Access, and Identity Governance resources

## Conversation Flow

### Step 1: Identify Components to Review

Ask the admin what scope they want:

- **Full review** - all Entra Suite components (comprehensive, takes longer)
- **Product-specific review** - one area: Conditional Access / Identity Protection, Global Secure Access, or Identity Governance
- **Scenario-specific review** - only configuration related to a specific scenario

For a full review, work through components in this order: Conditional Access policies, Identity Protection policies, authentication methods and MFA, Global Secure Access connectors and forwarding profiles, Private Access application segments, Internet Access security profiles, named locations, and Identity Governance configurations.

### Step 2: Read Configuration via MCP

Systematically read each component in the review scope.

**MCP Tool Usage - Reading Configuration:**
- Use `microsoft_graph_suggest_queries` to find the appropriate endpoints for each component
- Use `microsoft_graph_list_properties` to understand the full property set before reading, so no important settings are missed
- Use `microsoft_graph_get` to read the configuration

Present each component's configuration to the admin in a readable summary. Do not dump raw JSON unless the admin requests it. Translate API responses into human-readable descriptions.

### Step 3: Check Against Best Practices

For each component, evaluate against best practices from `references/best-practices/`. Key checks per area:

- **Conditional Access** - correct user/group targeting, break-glass exclusions, report-only vs enforced state, appropriate grant controls (MFA, compliant device)
- **Identity Protection** - risk policies enabled, risk levels not too permissive, self-remediation configured
- **Global Secure Access** - connector health and redundancy (2+ per group), forwarding profile assignments, application segments scoped to specific FQDNs/IPs
- **Identity Governance** - access review frequency, catalog scoping, lifecycle workflow triggers

### Step 4: Identify Security Gaps

Flag any configuration that creates security risk:

| Severity | Examples |
|----------|---------|
| **Critical** | No MFA required, Identity Protection disabled, break-glass accounts not excluded from CA |
| **High** | Overly permissive CA policies, connectors with no redundancy, stale access not reviewed |
| **Medium** | Report-only policies that should be enforced, missing named locations, weak authentication methods allowed |
| **Low** | Cosmetic issues, naming inconsistencies, unused policy objects |

For each finding, explain the risk in business terms, not just technical terms.

### Step 5: Produce Recommendations

Generate the review report:

```markdown
## Configuration Review Report
### Scope: [Full / Product / Scenario]
### Date: [Date]
### Executive Summary
- Components reviewed: X
- Critical findings: X | High: X | Medium: X | Low: X

### Findings by Component
#### [Component Name]
| # | Finding | Severity | Current State | Recommendation |
|---|---------|----------|---------------|----------------|

### Prioritized Remediation Plan
1. [Critical items first]
2. [High items next]
3. [Medium and low items]

### Positive Findings
[List configurations that are correct and well-implemented]
```

Always include positive findings. Stakeholders need to see what is working well, not just problems.

## MCP Tool Usage Summary

This template relies on MCP tools for every component check:
- `microsoft_graph_suggest_queries` - discover endpoints for each component area
- `microsoft_graph_list_properties` - ensure comprehensive property coverage
- `microsoft_graph_get` - read all configuration objects

All operations are strictly read-only. To remediate findings, switch to a scenario walkthrough as a separate activity.

## Output

A configuration review report in Markdown with severity-rated findings, recommendations, and a prioritized remediation plan suitable for security teams and management.
