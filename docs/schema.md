# Raijin Schema (v1)

Every Raijin tool returns one JSON object with this shape. An agent learns it once and can read any tool.

The JSON is compact (one line) by default; `--pretty` indents it. **Anything the agent can rebuild is left out**: empty lists and objects, fields at their default, and counts equal to what is listed. The output never loses information, it only skips what can be rebuilt.

```json
{
  "schema_version": 1,
  "tool": "raijin-<verb>",
  "version": "v0.2.0",
  "target": "scope or input summary",
  "summary": "one sentence an agent can quote back",
  "findings": [],
  "groups": [],
  "omitted": {},
  "errors": [],
  "next": [],
  "raw": "/tmp/raijin-scan-123.jsonl",
  "budget": {"max_items": 20, "max_bytes": 8000, "truncated": true}
}
```

## Fields

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | integer | Version of this schema, always the first field. Readers must check it before parsing and refuse a value they do not know (a document without the field is version 0) |
| `tool` | string | Which tool produced the result |
| `version` | string | Tool version (the release tag, with its `v`) |
| `target` | string | What was scanned, in one line |
| `summary` | string | One sentence: counts and the most important fact |
| `findings` | array | Ranked findings, at most `max_items` (see below) |
| `groups` | array | Info-level output collapsed per rule (see below) |
| `omitted` | object | What was dropped and why: `{"info": 1712, "duplicates": 119, "out_of_scope": 4}`. Left out when empty |
| `errors` | array | `{hosts, kind, hint}`; `hint` says what to try next. Left out when empty |
| `next` | array | Suggested follow-up commands, ready to run. Left out when empty |
| `raw` | string | File with the engine's full output, for details the result leaves out |
| `budget` | object | The limits applied. Written only when something was cut (`truncated: true`) |

## Finding

```json
{
  "id": "stable-id",
  "title": "Short human title",
  "severity": "critical|high|medium|low|info",
  "confidence": "verified|heuristic",
  "cve": ["CVE-2021-44228"],
  "cvss": 9.8,
  "locations": ["https://a.example.com/.env [DB_PASSWORD=x]", "https://b.example.com/.env"],
  "count": 42,
  "engine_ref": "engine:template-or-rule",
  "new": true
}
```

- `locations` lists **every** place the finding matched: the URL (or host:port), plus the values extracted there in brackets. Each location is cut at 300 characters. Two different URLs on one host are two locations.
- `count` is written only when the budget cut `locations`; otherwise it is `len(locations)`.
- `confidence` is left out when it is `matched`.
- `cve` and `cvss` appear when the engine rule has them. A CVE that is already the `id` is not repeated.
- `engine_ref` is written only when the engine rule is not the `id` up to the first `:`.
- `new` appears only with `--state`, and only when it is true.

`confidence` values:

- `verified`: the tool confirmed it (secret validated, reflection executed, takeover claimable).
- `matched` (the default, left out): the engine matched a signature; not confirmed.
- `heuristic`: inferred (outlier, unusual port); worth a look.

## Group

```json
{"id": "http-missing-security-headers", "variants": ["x-frame-options", "content-security-policy"], "locations": ["https://a", "https://b"], "count": 2}
```

Info-level output, collapsed per rule: **every variant listed matched every location listed.** Variants that matched different locations go in separate groups with the same `id`, so no variant/location pair is lost. `count` is written only when the budget cut `locations`.

## Rules every tool follows

1. **Lossless for what an agent acts on.** Every finding and every location is in the output. Only exact repeats collapse, and they are counted in `omitted.duplicates`.
2. Sort by `severity`, then `confidence`, then number of locations.
3. Never put a full response body in the output. Everything the engine produced is saved to the file in `raw`.
4. The same `tool` and `id` in two runs means the same finding. `raijin-diff` relies on it.
5. If `max_items` or `max_bytes` cut something, set `budget.truncated`, count it in `omitted` and point to `raw` in `next`. Cut the least important data first: info locations, info groups, extra locations of low-ranked findings, low-ranked findings.
6. Exit code `0` if the run worked (even with findings), `1` on usage error, `2` if the engine is missing.

## Errors and exit codes

The exit code is one contract across every tool, so an agent can branch on it before reading anything:

| Exit | Meaning | Stdout |
|---|---|---|
| `0` | The run finished. A partial failure (an engine died halfway) is still `0` and is listed in `errors[]`: always read that field | The result |
| `2` | A structured error: nothing, or not everything, was run. Read `errors[].kind` and `errors[].hint` | The result, with `errors` |
| `1` | Wrong usage (bad flag, missing argument) | Nothing; the message is on stderr |

Common `errors[].kind` values: `scope` (one entry per invalid scope line, the hint starts with `line N:` and says what to write instead), `missing_engine`, `no_targets` (the scope names no single host to scan; the hint says where to get one), `schema_version` (an input from a newer schema, `raijin-diff`).

