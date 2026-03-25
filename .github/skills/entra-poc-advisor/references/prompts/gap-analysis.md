# Gap Analysis Conversation Template

## Goal

Guide an administrator through reading their current tenant configuration, comparing it against a target state defined by a scenario or best-practice baseline, and producing a prioritized gap analysis report.

## When to Use

- Admin wants to understand what is already configured vs. what a scenario requires
- Admin needs to assess readiness before starting a POC
- Admin wants a report showing current state vs. target state for stakeholder review

## Requirements

- **Minimum mode**: Read-Only (MCP tools must be available for tenant reads)
- **Permissions**: The connected identity must have read access to the relevant Microsoft Graph resources (policies, users, groups, applications, network configurations)

## Conversation Flow

### Step 1: Confirm Target Configuration

Establish what the admin is comparing against:
- **Option A**: A specific scenario from `references/scenarios/` - load and extract target requirements
- **Option B**: A best-practice baseline from `references/best-practices/`
- **Option C**: A custom target the admin describes - document it before proceeding

List every configuration component to be checked. Components typically include: licensing assignments, Conditional Access policies, named locations, application registrations, Global Secure Access connectors and forwarding profiles, Identity Protection policies, and governance configurations (access packages, reviews, lifecycle workflows).

Ask the admin to confirm the target before reading tenant data.

### Step 2: Read Current Tenant Configuration

For each component in the target configuration, read the current state from the tenant.

**MCP Tool Usage - Discovery:**
- Use `microsoft_graph_suggest_queries` to identify the correct Graph API endpoints for each component
- Use `microsoft_graph_list_properties` to understand the response schema and identify which properties matter for comparison
- Use `microsoft_graph_get` to read the actual configuration values

Work through components methodically. Present findings to the admin as you go, grouped by category. If a read fails due to permissions, note it as "Unable to assess" rather than halting the entire analysis.

### Step 3: Compare Current vs. Target

For each component, classify the gap:

| Status | Meaning |
|--------|---------|
| **Met** | Current configuration matches or exceeds target requirements |
| **Partial** | Some elements are configured but incomplete or misconfigured |
| **Not Met** | Configuration is missing or significantly different from target |
| **Unable to Assess** | Insufficient permissions or API limitations prevented reading |

Provide specific details for each finding:
- What the target requires
- What currently exists (or does not)
- What specific changes are needed to close the gap

### Step 4: Generate Gap Analysis Report

Compile findings into a structured report:

```markdown
## Gap Analysis Report
### Target: [Scenario Name or Baseline]
### Date: [Date]
### Summary
- Components assessed: X
- Met: X | Partial: X | Not Met: X | Unable to Assess: X

### Detailed Findings
#### [Category: e.g., Conditional Access]
| Component | Target State | Current State | Gap Status | Remediation |
|-----------|-------------|---------------|------------|-------------|

### Prerequisites Not Met
### Licensing Gaps
```

### Step 5: Prioritize Remediation Steps

Order the gaps by priority:
1. **Blockers** - must be resolved before the POC can start (e.g., missing licenses, no connector installed)
2. **Required** - needed for the scenario to function correctly (e.g., missing CA policies)
3. **Recommended** - improve the POC quality but are not strictly required (e.g., log retention settings)
4. **Optional** - nice-to-have improvements identified during the review

For each gap, estimate effort (minutes/hours) and note any dependencies between remediation steps.

## MCP Tool Usage Summary

This template makes heavy use of MCP tools:
- `microsoft_graph_suggest_queries` - find the right endpoints for each component
- `microsoft_graph_list_properties` - understand response structures before reading
- `microsoft_graph_get` - read every configuration component from the tenant

All tool usage is read-only. Never suggest write operations during gap analysis.

## Output

A complete gap analysis report in Markdown, suitable for sharing with stakeholders, with specific remediation steps and effort estimates for each gap.
