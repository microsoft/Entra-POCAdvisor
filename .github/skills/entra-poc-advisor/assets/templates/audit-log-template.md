# POC Audit Log

> Session started: {session-start-utc}
> Mode: {operation-mode}
> Tenant: {tenant-id}
> Scenario: {scenario-name}

## Actions

<!-- Append one entry per action. Do not remove previous entries. -->

### [{entry-index}] {action-timestamp-utc}

- **Action:** {action-type}
- **Type:** {read|write|generate|recommend}
- **Component:** {component-name}
- **MCP Call:** `{mcp-tool-name}` -- `{api-endpoint-or-na}`
- **Details:** {action-description}
- **Result:** {success|skipped|failed|warning} -- {result-details}
- **Rollback:** {rollback-instructions-or-na}

---

<!-- Copy the block above for each additional action. -->

### [{entry-index}] {action-timestamp-utc}

- **Action:** {action-type}
- **Type:** {read|write|generate|recommend}
- **Component:** {component-name}
- **MCP Call:** `{mcp-tool-name}` -- `{api-endpoint-or-na}`
- **Details:** {action-description}
- **Result:** {success|skipped|failed|warning} -- {result-details}
- **Rollback:** {rollback-instructions-or-na}

---

## Summary

| Metric | Count |
|---|---|
| Total actions | {total-actions} |
| Reads | {read-count} |
| Writes | {write-count} |
| Generations | {generate-count} |
| Warnings | {warning-count} |
| Failures | {failure-count} |

> [!NOTE]
> This audit log is append-only. Do not edit or remove entries.
> All timestamps are in UTC (ISO 8601 format).
