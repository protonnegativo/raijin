# Raijin Schema (v0, draft)

Every Raijin tool returns one JSON object with this shape. An agent learns it once and can read any tool.

The JSON is compact (one line) by default; `--pretty` indents it. **Anything the agent can rebuild is left out**: empty lists and objects, fields at their default, and counts equal to what is listed. The output never loses information, it only skips what can be rebuilt.

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
  "budget": {"max_items": 20, "max_bytes": 8000, "truncated": true}
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
| `groups` | array | Things that repeat, collapsed: `{id, count, examples[≤3], variants}`. `count` is the total; `examples` may be cut by the budget; `variants` lists the sub-matches (for example the missing headers) |
| `omitted` | object | What was dropped and why: `{"info": 1712, "duplicates": 119, "out_of_scope": 4}`. Left out when empty |
| `errors` | array | `{hosts, kind, hint}`; `hint` says what to try next. Left out when empty |
| `next` | array | Suggested follow-up commands, ready to run. Left out when empty |
| `budget` | object | The limits applied. Written only when something was cut (`truncated: true`) |

## Finding

```json
{
  "id": "stable-id",
  "title": "Short human title",
  "severity": "critical|high|medium|low|info",
  "confidence": "verified|heuristic",
  "hosts": ["up to 5 hosts"],
  "hosts_count": 42,
  "evidence": "the minimal proof: one header, one line, one reflected value",
  "engine_ref": "engine:template-or-rule",
  "new": true
}
```

- `confidence` is left out when it is `matched`.
- `hosts_count` is written only when it is larger than the number of `hosts` listed.
- `engine_ref` is written only when the engine rule is not the `id` up to the first `:`.
- `new` appears only with `--state`, and only when it is true.

- `verified`: the tool confirmed it (secret validated, reflection executed, takeover claimable).
- `matched` (the default, left out): the engine matched a signature; not confirmed.
- `heuristic`: inferred (outlier, unusual port); worth a look.

## Rules every tool follows

1. Sort by `severity`, then `confidence`, then number of hosts.
2. Never put a full response body in `evidence`. At most 300 characters.
3. The same `tool` and `id` in two runs means the same finding. `raijin-diff` relies on it.
4. If `max_items` or `max_bytes` cut something, set `budget.truncated` and count it in `omitted`.
5. Exit code `0` if the run worked (even with findings), `1` on usage error, `2` if the engine is missing.
