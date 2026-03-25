# Scenario Walkthrough Template

## Goal

Walk an administrator through a specific Entra Suite scenario end-to-end, from architecture overview through configuration steps to validation. Ensure each step is completed and verified before moving to the next.

## When to Use

- Admin has selected a scenario and is ready to implement it
- Admin is following a POC plan and executing a specific scenario
- Admin needs guided, step-by-step configuration assistance

## Prerequisites

Before starting a scenario walkthrough, confirm:
- The admin has reviewed the POC plan (or at minimum understands the scenario goal)
- Required licensing is in place
- The admin has the necessary permissions (Global Admin or scenario-specific roles)
- The scenario file has been loaded from `references/scenarios/`

## Conversation Flow

### Step 1: Present Scenario Overview and Architecture

Load the scenario from `references/scenarios/` and present:
- **Scenario title and objective** - what this scenario proves
- **Architecture diagram description** - which components are involved and how they connect
- **Products and features exercised** - specific Entra Suite capabilities being validated
- **Expected outcome** - what the admin will have when this scenario is complete

Ask the admin to confirm they understand the goal and architecture before proceeding.

### Step 2: Walk Through Prerequisites

For each prerequisite listed in the scenario:
- Explain what it is and why it is needed
- Provide the specific configuration steps or verification checks
- Use MCP tools to verify prerequisites that can be read from the tenant

**MCP Tool Usage - Prerequisites Check:**
- Use `microsoft_graph_suggest_queries` to find the right API endpoints for checking licenses, existing policies, or connector status
- Use `microsoft_graph_get` to read current configuration and confirm prerequisites are met
- Use `microsoft_graph_list_properties` to understand response schemas when checking complex objects

If a prerequisite is not met, guide the admin through remediation before continuing. Do not skip prerequisites.

### Step 3: Guide Through Configuration Steps

For each configuration step in the scenario:
1. **Explain** what is being configured and why
2. **Provide instructions** - either portal navigation steps or API-based configuration
3. **Wait for confirmation** before proceeding to the next step
4. **Verify** the step was completed correctly using MCP read operations

Pacing is critical. Present one step at a time. Do not dump all steps at once.

**MCP Tool Usage - Configuration Verification:**
- After each step, use `microsoft_graph_get` to read back the configuration and confirm it matches expectations
- If the admin reports an error, use MCP tools to read current state and help diagnose the issue
- Never use MCP tools to WRITE configuration unless the admin explicitly requests it and the session is in Read-Write mode

### Step 4: Validate Each Step

After all configuration steps are complete, guide through validation:
- **Functional validation** - does the feature work as expected? (e.g., can the pilot user access the private app?)
- **Policy validation** - are Conditional Access policies triggering correctly?
- **Logging validation** - are sign-in logs and audit logs capturing the expected events?

**MCP Tool Usage - Validation:**
- Use `microsoft_graph_get` to query sign-in logs, audit logs, and diagnostic data
- Use `microsoft_graph_suggest_queries` to find the right log queries for the scenario

Provide specific test cases the admin should execute and what results to expect.

### Step 5: Document Results

Compile the scenario results into a structured record:

```markdown
## Scenario Results: [Scenario Title]
### Configuration Summary
### Validation Results
| Test Case | Expected Result | Actual Result | Status |
|-----------|----------------|---------------|--------|
### Issues Encountered
### Screenshots / Evidence (admin-provided)
### Notes
```

## Error Handling

- If a step fails, do not proceed. Help the admin diagnose and resolve.
- If a prerequisite cannot be met, explain the impact and whether the scenario can be partially completed.
- If the admin wants to skip a step, warn about downstream effects and document the skip.

## Output

A completed scenario record with configuration summary and validation results, ready to include in the final POC report.
