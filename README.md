# EntraSuite-POC

A [GitHub Copilot Skill](https://docs.github.com/en/copilot/customizing-copilot/copilot-extensions/building-copilot-skills) that guides Microsoft Entra administrators through proof-of-concept deployments of the Microsoft Entra Suite. It provides expert advisory, configuration guidance, and documentation generation — all through a conversational-first approach.

## Overview

EntraSuite-POC is designed for **Entra administrators** who need to plan, configure, validate, and document POC deployments across the Microsoft Entra Suite. Instead of generating outputs immediately, the assistant engages you in conversation: it asks clarifying questions, surfaces considerations you may not have thought of, recommends best practices, and helps you think through your POC strategy before producing any artifacts.

When you're ready, it generates production-grade documentation, PowerShell scripts, gap analysis reports, and architecture diagrams — all following Microsoft documentation standards.

> [!NOTE]
> This skill integrates with the **Microsoft MCP Server for Enterprise** to read tenant configuration in real time. It also works fully offline in Guidance Only mode.

## Products Covered

The assistant covers six Microsoft Entra Suite products:

| Product | Key Capabilities |
|---|---|
| **Global Secure Access** | Traffic forwarding profiles, GSA Client deployment, remote networks, traffic logging, Conditional Access integration |
| **Entra Private Access** | Zero Trust network access, application connectors, Quick Access (VPN replacement), Per-App Access, Private DNS |
| **Entra Internet Access** | Web content filtering, security profiles, TLS inspection, Universal Tenant Restrictions |
| **Entra ID Protection** | Risk detection engine, risky users/sign-ins reports, risk-based Conditional Access policies |
| **Entra ID Governance** | Access reviews, entitlement management, lifecycle workflows, Privileged Identity Management |
| **Entra Verified ID** | Digital credential issuance and verification, decentralized identity flows |

Detailed product references are available under [.github/skills/entra-poc-advisor/references/products/](.github/skills/entra-poc-advisor/references/products/).

## Operation Modes

You select an operation mode at the start of every session. The assistant never escalates beyond the selected mode without your explicit consent.

| Mode | Tenant Connection | What You Get |
|---|---|---|
| **Guidance Only** | None | Advisory conversation, documentation, scripts (with placeholder values), architecture diagrams, scenario templates |
| **Read-Only** | Microsoft MCP Server (read) | Everything above, plus live prerequisite validation, current-state configuration reads, and gap analysis reports with real tenant data |
| **Read-Write** | Microsoft MCP Server (read) | Everything above, plus PowerShell scripts and portal instructions pre-populated with your tenant-specific values (group IDs, UPNs, resource references) |

> [!IMPORTANT]
> Even in Read-Write mode, the assistant **never writes directly** to your tenant. All changes are performed by you — via PowerShell scripts you review and execute, or portal instructions you follow manually.

See [.github/skills/entra-poc-advisor/references/operation-modes.md](.github/skills/entra-poc-advisor/references/operation-modes.md) for detailed mode transition rules.

## POC Lifecycle

Every POC engagement follows a six-phase lifecycle. Phases are iterative — you can loop back at any point.

```mermaid
flowchart TD
    A["1. Planning"] --> B["2. Prerequisites"]
    B --> C["3. Configuration"]
    C --> D["4. Validation"]
    D --> E{"Gaps found?"}
    E -->|Yes| C
    E -->|No| F["5. Testing"]
    F --> G["6. Documentation"]

    A ---|"Gather requirements\nSelect scenarios\nDefine pilot scope"| A
    B ---|"Check licenses\nVerify roles\nValidate infrastructure"| B
    C ---|"Manual via docs\nScripted via PowerShell\nHybrid approach"| C
    D ---|"Read tenant config\nCompare against target\nGenerate gap report"| D
    F ---|"Client connectivity\nPolicy enforcement\nTraffic routing"| F
    G ---|"Export final docs\nExport audit log\nProduction planning"| G
```

| Phase | What Happens |
|---|---|
| **1. Planning** | Conversational requirements gathering. You describe your goals, the assistant recommends products and scenarios, and together you refine the approach. Output generation starts **only when you say you're ready**. |
| **2. Prerequisites** | Validates licenses, admin roles, and infrastructure. In Read-Only/Read-Write modes, the assistant checks your live tenant via MCP and reports gaps with remediation guidance. |
| **3. Configuration** | You choose your path — manual (step-by-step Markdown docs), scripted (idempotent PowerShell), or hybrid (docs with embedded scripts). |
| **4. Validation** | Compares your current tenant configuration against the target state and produces a gap analysis report. Loops back to Configuration if gaps are found. |
| **5. Testing** | Provides testing checklists and procedures. Validates test outcomes via MCP where possible (e.g., sign-in logs). |
| **6. Documentation** | Exports the complete POC guide, architecture diagrams, gap analysis, and session audit log. |

See [.github/skills/entra-poc-advisor/references/poc-lifecycle.md](.github/skills/entra-poc-advisor/references/poc-lifecycle.md) for detailed phase guidance.

## Pre-Built Scenarios

14 ready-to-use scenarios across five categories, each with prerequisites, architecture diagrams, configuration steps, and validation procedures:

| Category | Scenario | Complexity | Est. Time |
|---|---|---|---|
| **Private Access** | Quick Access (VPN replacement) | Medium | 45 min |
| | Per-App Access (granular resources) | High | 90 min |
| | Private DNS | High | 60 min |
| **Internet Access** | Web Content Filtering | Medium | 30 min |
| | Security Profiles | Medium | 45 min |
| | TLS Inspection | High | 60 min |
| | Universal Tenant Restrictions | Medium | 30 min |
| **Global Secure Access** | Traffic Forwarding Profiles | Low | 20 min |
| | GSA Client Deployment | Medium | 30 min |
| | Conditional Access Integration | Medium | 45 min |
| **Identity** | Conditional Access Baseline | Medium | 45 min |
| | ID Protection Risk Policies | Medium | 30 min |
| **Governance** | Access Reviews | Medium | 45 min |
| | Entitlement Management | High | 60 min |

You can also describe a **custom scenario** in natural language, and the assistant will structure it following the same schema.

See [.github/skills/entra-poc-advisor/references/scenarios/](.github/skills/entra-poc-advisor/references/scenarios/) for full scenario definitions.

## Conversation Templates

Four reusable conversation flows are available as starting points:

| Template | When to Use |
|---|---|
| [POC Planning](.github/skills/entra-poc-advisor/references/prompts/poc-planning.md) | Starting a new POC — requirements gathering, product recommendations, scenario selection, timeline and effort estimates |
| [Configuration Review](.github/skills/entra-poc-advisor/references/prompts/configuration-review.md) | Reviewing an existing deployment — identify components, read config via MCP, check against best practices, produce findings |
| [Gap Analysis](.github/skills/entra-poc-advisor/references/prompts/gap-analysis.md) | Comparing current vs. target state — define target, read tenant config, classify gaps, prioritize remediation |
| [Scenario Walkthrough](.github/skills/entra-poc-advisor/references/prompts/scenario-walkthrough.md) | Step-by-step guided configuration — overview, prerequisites, configuration steps with validation at each stage |

## Artifacts You Can Get

The assistant generates the following output artifacts on request:

| Artifact | Format | Description |
|---|---|---|
| **POC Guide** | Markdown | Complete step-by-step configuration guide with numbered instructions, portal navigation paths, prerequisites, and validation steps |
| **Gap Analysis Report** | Markdown + Mermaid | Current vs. target state comparison with per-component status, prioritized remediation steps, and visual gap diagrams |
| **PowerShell Scripts** | `.ps1` | Idempotent, `-WhatIf`-enabled automation scripts with `Connect-MgGraph` authentication, color-coded progress output, and error handling |
| **Architecture Diagrams** | Mermaid | Visual topology diagrams showing POC components, traffic flows, and deployment sequences |
| **Audit Log** | Markdown + JSON | Complete session record of every MCP call, recommendation, warning, and generated artifact |
| **Prerequisite Report** | Markdown | Pass/fail checklist for licenses, admin roles, and infrastructure with remediation guidance for each gap |

Templates for these artifacts are available under [.github/skills/entra-poc-advisor/assets/templates/](.github/skills/entra-poc-advisor/assets/templates/).

## Safety Guardrails

Seven absolute safety rules are enforced at all times and **cannot be overridden**:

1. **No deletions** — Never generates DELETE API calls, `Remove-*` PowerShell cmdlets, or instructions to delete resources
2. **No production CA policy changes** — Refuses to modify Conditional Access policies targeting "All users" or "All cloud apps"; recommends POC-scoped alternatives
3. **No silent mode escalation** — Mode changes require your explicit request
4. **No scripts without `-WhatIf`** — Every PowerShell script supports dry-run execution
5. **No fabricated data** — If a configuration state cannot be verified via MCP, the assistant says so honestly
6. **No skipped audit trails** — Every MCP call, recommendation, and warning is logged
7. **No broad-scope changes without warning** — Changes affecting all users, all apps, or tenant-wide settings trigger an explicit warning and confirmation prompt

See [.github/skills/entra-poc-advisor/references/safety-guardrails.md](.github/skills/entra-poc-advisor/references/safety-guardrails.md) for detailed rules and warning triggers.

## Repository Structure

```
.github/
└── skills/
    └── entra-poc-advisor/              # Copilot Skill (auto-discovered by VS Code)
        ├── SKILL.md                      # Skill definition and core behavior
        ├── assets/
        │   └── templates/                # Output artifact templates
        │       ├── audit-log-template.md
        │       ├── gap-report-template.md
        │       ├── poc-guide-template.md
        │       └── powershell-template.ps1
        ├── references/
        │   ├── documentation-standards.md    # Microsoft documentation style guide
        │   ├── operation-modes.md            # Mode definitions and transition rules
        │   ├── poc-lifecycle.md              # Six-phase lifecycle detailed guidance
        │   ├── powershell-standards.md       # PowerShell conventions and patterns
        │   ├── safety-guardrails.md          # Safety rules and warning triggers
        │   ├── products/                     # Product reference sheets
        │   │   ├── entra-id-governance.md
        │   │   ├── entra-id-protection.md
        │   │   ├── entra-internet-access.md
        │   │   ├── entra-private-access.md
        │   │   ├── entra-verified-id.md
        │   │   └── global-secure-access.md
        │   ├── prompts/                      # Conversation templates
        │   │   ├── configuration-review.md
        │   │   ├── gap-analysis.md
        │   │   ├── poc-planning.md
        │   │   └── scenario-walkthrough.md
        │   └── scenarios/                    # Pre-built POC scenarios
        │       ├── index.md
        │       ├── global-secure-access.md
        │       ├── governance.md
        │       ├── identity.md
        │       ├── internet-access.md
        │       └── private-access.md
        └── scripts/                          # Automation and validation scripts
            ├── audit-logger.py
            ├── Deploy-EmployeeGuestOnboarding.ps1
            ├── Deploy-PrivateAccessQuickAccess.ps1
            ├── generate-gap-report.py
            ├── validate-configuration.py
            └── validate-prerequisites.py
benchmarks/                                   # Automated benchmark suite
├── README.md
├── run_benchmark.py
├── compare_results.py
├── evaluators/                               # Scoring evaluators
├── scoring/                                  # Rubrics
└── test_cases/                               # Triggering, functional, performance tests
```

## Benchmarks

An automated benchmark suite with **30 test cases** measures skill quality across three categories:

| Category | Tests | What It Measures |
|---|---|---|
| **Triggering** | 15 | Skill activates on relevant Entra POC queries and stays silent on unrelated ones |
| **Functional** | 10 | Response quality for core tasks — planning, configuration, gap analysis, script generation |
| **Performance** | 5 | End-to-end output quality for complex multi-step scenarios |

See [benchmarks/README.md](benchmarks/README.md) for setup instructions and execution modes.

## Installation & Setup

Choose one of the two installation options below, then verify the skill is detected.

### Prerequisites

| Requirement | Details |
|---|---|
| **VS Code** | Version 1.99 or later ([download](https://code.visualstudio.com/)) |
| **GitHub Copilot subscription** | Copilot Pro, Business, or Enterprise ([plans](https://github.com/features/copilot#pricing)) |
| **GitHub Copilot extension** | Install from the VS Code Marketplace — includes Copilot Chat ([install](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)) |
| **Git** | Any recent version ([download](https://git-scm.com/downloads)) |
| **Node.js 18+** | Required for Option A — includes `npm` and `npx` ([download](https://nodejs.org/)) |
| **Python 3.10+** *(optional)* | Only needed if you want to run the benchmark suite or utility scripts |

### Install Node.js

Option A requires **Node.js 18 or later**. If you don't have it installed, follow the steps for your operating system below.

> [!TIP]
> Download the **LTS (Long Term Support)** version for the best stability.

#### Windows

1. Go to [https://nodejs.org/](https://nodejs.org/) and download the **Windows Installer (.msi)** for the LTS version.
2. Run the installer and follow the prompts — the default options work for most users.
3. Open a new terminal and verify the installation:

   ```bash
   node --version
   npm --version
   ```

#### macOS

**Option 1 — Installer:**

1. Go to [https://nodejs.org/](https://nodejs.org/) and download the **macOS Installer (.pkg)** for the LTS version.
2. Run the installer and follow the prompts.

**Option 2 — Homebrew:**

```bash
brew install node@18
```

Verify:

```bash
node --version
npm --version
```

#### Linux

The recommended approach is to use [nvm (Node Version Manager)](https://github.com/nvm-sh/nvm):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install 18
```

Verify:

```bash
node --version
npm --version
```

> [!NOTE]
> Both commands should return a version number (e.g., `v18.x.x` and `10.x.x`). If you get "command not found", restart your terminal or check that Node.js is on your `PATH`.

---

### Option A — Install via Skills CLI (recommended)

The [skills CLI](https://www.npmjs.com/package/skills) is an open-source tool that installs agent skills to 40+ coding agents — including GitHub Copilot, Claude Code, Cursor, Codex, and more.

Run a single command to install the **entra-poc-assistant** skill:

```bash
npx skills add https://github.com/LuisPFlores/EntraSuite-POC
```

The CLI auto-detects the coding agents installed on your machine and prompts you to select where to install the skill.

#### Targeting a specific agent

To install only for GitHub Copilot:

```bash
npx skills add https://github.com/LuisPFlores/EntraSuite-POC -a github-copilot
```

#### Global installation

Add `-g` to make the skill available across all your projects (installed to `~/.copilot/skills/`):

```bash
npx skills add https://github.com/LuisPFlores/EntraSuite-POC -a github-copilot -g
```

#### Other useful commands

```bash
# List available skills in the repo without installing
npx skills add https://github.com/LuisPFlores/EntraSuite-POC --list

# List installed skills
npx skills list

# Check for updates
npx skills check

# Update to the latest version
npx skills update
```

> [!TIP]
> For GitHub Copilot, project-level skills are installed to `.agents/skills/` in your workspace. Global skills go to `~/.copilot/skills/`.

Once installed, skip to [Verify the Skill Is Detected](#step-3--verify-the-skill-is-detected).

---

### Option B — Clone the Repository Manually

#### Step 1 — Clone

```bash
git clone https://github.com/<YOUR-ORG>/EntraSuite-POC.git
```

> Replace `<YOUR-ORG>` with the GitHub organization or username that hosts this repository.

#### Step 2 — Open in VS Code

```bash
cd EntraSuite-POC
code .
```

Or in VS Code: **File → Open Folder…** and select the cloned `EntraSuite-POC` directory.

---

### Step 3 — Verify the Skill Is Detected

1. Open **Copilot Chat** — press `Ctrl+Alt+I` (Windows/Linux) or `Cmd+Alt+I` (macOS), or click the Copilot Chat icon in the Activity Bar.
2. Type `/` in the chat input — you should see **entra-poc-advisor** listed as an available skill.
3. Alternatively, just ask a relevant question like *"Help me plan a Global Secure Access POC"* — the skill activates automatically based on your prompt.

> [!TIP]
> If the skill does not appear, make sure the Copilot extension is up to date and the workspace is opened at the repository root (the folder containing `.github/`).

### Step 4 — Start a Conversation

1. **Mention an Entra POC topic** — for example:
   - *"I need to set up a Private Access POC to replace our VPN"*
   - *"What licenses do I need for Internet Access web content filtering?"*
   - *"Help me plan a Global Secure Access proof of concept"*

2. **Select your operation mode** when prompted — Guidance Only, Read-Only, or Read-Write.

3. **Have a conversation** — describe your goals, ask questions, explore options. The assistant acts as your Entra Suite SME.

4. **Request artifacts when ready** — say *"generate the POC guide"*, *"create the PowerShell scripts"*, or *"produce the gap analysis"* and the assistant will produce the outputs.

### Optional: Connect the Microsoft MCP Server for Enterprise

Read-Only and Read-Write modes require a connection to the **Microsoft MCP Server for Enterprise** so the assistant can read your tenant configuration in real time. Guidance Only mode works without any MCP setup.

#### 1. Add the MCP server configuration

Create (or update) the file `.vscode/mcp.json` in the repository root with the following structure:

```jsonc
// .vscode/mcp.json
{
  "servers": {
    "microsoft-graph-enterprise": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@microsoft/mcp-server-enterprise"
      ]
    }
  }
}
```

> [!NOTE]
> The exact package name and arguments may vary. Refer to the [Microsoft MCP Server for Enterprise documentation](https://aka.ms/mcp-server-enterprise) for the latest installation instructions and authentication requirements.

#### 2. Authenticate

When you first use the MCP server, you will be prompted to sign in with your Microsoft Entra ID credentials. The account must have at least **read access** to the Entra resources you want to inspect (e.g., Global Reader, Security Reader, or equivalent roles).

#### 3. Verify the connection

In Copilot Chat, ask the assistant:

> *"Can you check how many users are in my tenant?"*

If the MCP server is connected and authenticated, the assistant will query the Microsoft Graph API and return the result. If it fails, check that:
- The MCP server process started successfully (look for errors in the VS Code Output panel under the MCP server channel)
- Your Entra ID credentials are valid and have the required permissions
- Your network allows outbound connections to `graph.microsoft.com`

## Quick Start

```text
You:        "I want to set up a Private Access POC to replace our legacy VPN."
Assistant:   Asks clarifying questions — environment, user scope, existing infrastructure…
You:        "We have 50 pilot users, Entra P2 + GSA licenses, hybrid-joined devices."
Assistant:   Recommends the Quick Access scenario, walks through prerequisites…
You:        "Sounds good. Generate the POC guide."
Assistant:   Produces the full Markdown guide with numbered steps, validation checks, and architecture diagram.
```

## License

MIT
