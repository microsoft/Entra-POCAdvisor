# POC Planning Conversation Template

## Goal

Guide an administrator through structured POC planning for Microsoft Entra Suite. Gather business requirements, recommend relevant products, assess prerequisites, define pilot scope, and produce a concrete implementation plan.

## When to Use

- Admin is starting a new Entra Suite POC engagement
- Admin wants to evaluate one or more Entra Suite products
- Stakeholders need a formal plan before proceeding with implementation

## Conversation Flow

### Step 1: Understand Business Objectives

Ask the administrator:
- What business problems are you trying to solve? (e.g., Zero Trust adoption, VPN replacement, identity governance)
- What is driving the POC? (e.g., security incident, compliance requirement, modernization initiative)
- Who are the stakeholders and decision-makers?
- What does success look like? What would make this POC a "go" for production?
- Are there any hard constraints? (timeline, budget, regulatory)

Capture responses as structured requirements before proceeding.

### Step 2: Identify Relevant Entra Suite Products

Based on the stated objectives, recommend which products to include:
- **Entra Private Access** - for private app access / VPN replacement scenarios
- **Entra Internet Access** - for SaaS and internet traffic security
- **Entra ID Protection** - for risk-based Conditional Access and identity threat detection
- **Entra ID Governance** - for access reviews, entitlement management, lifecycle workflows

Explain why each recommendation maps to their stated objectives. Flag any products that are NOT relevant so the admin understands the scoping decision.

### Step 3: Define Pilot Scope

Gather specifics on pilot boundaries:
- **Users**: How many pilot users? Which departments or roles? Any executives or privileged accounts?
- **Devices**: What OS platforms? Corporate-managed, BYOD, or both? Current MDM solution?
- **Applications**: Which private apps or SaaS apps should be in scope? Any legacy or on-premises apps?
- **Network segments**: Any specific office locations or remote worker populations?

Recommend starting small (10-25 users) and expanding. Flag any scope choices that increase complexity.

### Step 4: Select or Create Scenarios

Cross-reference the admin's objectives and scope against available scenarios in `references/scenarios/`. Recommend specific scenarios and explain what each one validates. If no existing scenario fits, outline what a custom scenario would cover.

Present scenarios in priority order with estimated effort for each.

### Step 5: Estimate Timeline and Effort

Based on selected scenarios, provide estimates:
- **Prerequisites phase**: Licensing, connector installation, DNS configuration (typically 1-2 days)
- **Configuration phase**: Per-scenario setup time (typically 1-3 days per scenario)
- **Validation phase**: Testing and user acceptance (typically 2-3 days per scenario)
- **Documentation phase**: Results capture and reporting (typically 1 day)

Identify dependencies between scenarios and recommend sequencing.

### Step 6: Produce Implementation Plan

Compile all gathered information into a structured implementation plan:

```markdown
## POC Implementation Plan
### Business Objectives
### Products in Scope
### Pilot Scope (Users / Devices / Apps)
### Scenarios and Sequencing
### Timeline (Week-by-Week)
### Prerequisites Checklist
### Success Criteria
### Risks and Mitigations
```

## MCP Tool Usage

- **Do NOT use MCP tools during planning** unless the admin wants to assess current tenant state as part of planning
- If the admin wants a gap analysis folded into planning, switch to the `gap-analysis` prompt template for that portion
- Tools like `microsoft_graph_suggest_queries` may be used if the admin asks "what do I already have configured?" to inform scope decisions

## Output

Deliver the implementation plan as a complete Markdown document the admin can share with stakeholders. Offer to refine any section based on feedback.
