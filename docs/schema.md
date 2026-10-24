# Raijin Schema (v0, draft)

Every Raijin tool returns one JSON object with this shape. An agent learns it once and can read any tool.

```json
{
  "tool": "raijin-<verb>",
  "version": "0.1.0",
  "target": "scope or input summary",
  "summary": "one sentence an agent can quote back",
  "findings": [],
  "groups": [],
  "omitted": {},
  "errors": [],
  "next": [],
  "budget": {"max_items": 20, "max_bytes": 8000, "truncated": false}
}
```

## Fields

| Field | Type | Meaning |
|---|---|---|
| `tool` | string | Which tool produced the result |
| `version` | string | Tool version; the schema version is the major |
| `target` | string | What was scanned, in one line |
| `summary` | string | One sentence: counts and the most important fact |
| `findings` | array | Ranked findings, at most `max_items` (see below) |
| `groups` | array | Things that repeat, collapsed: `{id, count, examples[≤3]}` |
| `omitted` | object | What was dropped and why: `{"info": 1712, "duplicates": 119, "out_of_scope": 4}` |
| `errors` | array | `{hosts, kind, hint}`; `hint` says what to try next |
| `next` | array | Suggested follow-up commands, ready to run |
| `budget` | object | The limits applied and whether anything was cut |

## Finding

```json
{
  "id": "stable-id",
  "title": "Short human title",
  "severity": "critical|high|medium|low|info",
  "confidence": "verified|matched|heuristic",
  "hosts": ["one or more hosts, collapsed"],
  "evidence": "the minimal proof: one header, one line, one reflected value",
  "engine_ref": "engine:template-or-rule",
  "fingerprint": "hash used for dedup and diff"
}
```

- `verified`: the tool confirmed it (secret validated, reflection executed, takeover claimable).
- `matched`: the engine matched a signature; not confirmed.
- `heuristic`: inferred (outlier, unusual port); worth a look.

## Rules every tool follows

1. Sort by `severity`, then `confidence`, then number of hosts.
2. Never put a full response body in `evidence`. At most 300 characters.
3. The same `fingerprint` in two runs means the same finding. `raijin-diff` relies on it.
4. If `max_items` or `max_bytes` cut something, set `budget.truncated` and count it in `omitted`.
5. Exit code `0` if the run worked (even with findings), `1` on usage error, `2` if the engine is missing.
