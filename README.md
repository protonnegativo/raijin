<p align="right"><b>🇺🇸 English</b> · <a href="README.pt-BR.md">🇧🇷 Português</a></p>

# ⚡ Raijin

**AI-native offensive security tools. Signal, not noise.**

Raijin is an arsenal of security tools built to be driven by AI agents. Each tool runs a proven engine underneath (nuclei, httpx, katana, ffuf, ...). Instead of dumping thousands of raw lines, it returns a **small, deduplicated, ranked JSON** that an LLM can read without drowning its context.

> Status: early. First tool available: [**raijin-scan**](https://github.com/protonnegativo/raijin-scan) (nuclei, 37× to 168× fewer tokens on the same matches); the other 14 tools are built and private for now. See [ROADMAP.md](ROADMAP.md).

---

## The problem

Give an agent `nuclei`, `ffuf` or `katana` and it gets back:

- thousands of lines, mostly duplicates, 404s and low-value info;
- the same finding repeated across hundreds of hosts;
- full HTML bodies where one header was enough;
- stack traces instead of "what to do next".

The agent burns its context on noise, misses the real finding and loops.

## The idea

Every Raijin tool is a **wrapper + reducer**:

```
target ──▶ engine (nuclei, httpx, ...) ──▶ raw output ──▶ Raijin reducer ──▶ Raijin Schema (JSON)
                                                          dedup · group · rank
                                                          trim evidence · budget
```

The engines do the scanning. Raijin does the part agents are bad at: **compressing the result into what matters**.

## Principles

1. **Token budget.** Every tool takes `max_items` (and `max_bytes`). It returns the top N, plus a summary of what was left out: `"+340 identical 404 responses omitted"`.
2. **Same schema everywhere.** Every tool returns the [Raijin Schema](docs/schema.md): `summary`, `findings`, `groups`, `omitted`, `errors`, `next`. An agent learns it once.
3. **Group, don't repeat, don't drop.** 500 hosts with the same finding become one entry that lists every location once, instead of 500 copies of the same template, title and metadata. Nothing found is dropped silently.
4. **Minimal evidence.** Each finding carries the exact snippet that proves it (the header, the matched line, the reflected parameter), never the whole response.
5. **Confidence, not just severity.** Each finding says how sure it is and why (`verified`, `matched`, `heuristic`).
6. **Diff by default.** With a state file, a rerun reports only what changed since the last run.
7. **Actionable errors.** `"timeout on 3/50 hosts; retry with rate=10"`, not a stack trace.
8. **Suggested next step.** `next` proposes the obvious follow-up (`raijin-scan` on the 4 hosts running Jenkins), so the agent doesn't have to guess.
9. **Scope first.** Every tool takes an explicit scope (allow/deny lists) and refuses targets outside it.

## The arsenal

Every tool is named `raijin-<verb>`: the same prefix, the same schema and the same flags (`--scope`, `--max-items`, `--state`, `--json`).

| Tool | Engine underneath | What Raijin reduces |
|---|---|---|
| **[raijin-probe](https://github.com/protonnegativo/raijin-probe)** | httpx | Status, title, tech and size per host; groups identical responses, flags outliers |
| **[raijin-subs](https://github.com/protonnegativo/raijin-subs)** | subfinder + dnsx | Live subdomains only, grouped by IP / CNAME / provider; flags dangling CNAMEs |
| **[raijin-ports](https://github.com/protonnegativo/raijin-ports)** | naabu (+ nmap) | Open ports grouped by service; highlights unusual ports per host |
| **[raijin-crawl](https://github.com/protonnegativo/raijin-crawl)** | katana | Unique endpoints and parameters, collapsed by route pattern (`/user/{id}`) |
| **[raijin-js](https://github.com/protonnegativo/raijin-js)** | katana + JS parsing | Endpoints, API routes and secrets found in JS bundles, deduped across files |
| **[raijin-params](https://github.com/protonnegativo/raijin-params)** | arjun (x8 planned) | Hidden parameters that actually change the response |
| **raijin-scan** | nuclei | Unique findings with the matched evidence; collapses the same template across hosts |
| **[raijin-fuzz](https://github.com/protonnegativo/raijin-fuzz)** | ffuf | Only responses that differ from the baseline (status, size, words, timing) |
| **[raijin-tls](https://github.com/protonnegativo/raijin-tls)** | tlsx | Weak protocols/ciphers and certificate issues, grouped by issue |
| **[raijin-secrets](https://github.com/protonnegativo/raijin-secrets)** | trufflehog | Verified secrets first, with the minimal context line, never the full file |
| **[raijin-xss](https://github.com/protonnegativo/raijin-xss)** | dalfox | Confirmed reflections with the payload and the context it landed in |
| **[raijin-cors](https://github.com/protonnegativo/raijin-cors)** | native | Exploitable CORS only (credentials + reflected/null origin), with the proof request |
| **[raijin-takeover](https://github.com/protonnegativo/raijin-takeover)** | dnsx + fingerprints | Dangling records with the provider and the claim hint |
| **[raijin-diff](https://github.com/protonnegativo/raijin-diff)** | native | What changed between two runs of any tool |
| **[raijin-mcp](https://github.com/protonnegativo/raijin-mcp)** | — | One MCP server that exposes every tool to any agent (Claude Code, Cursor, QuarkScan, ...) |

Companion: **Fūjin**, the wind god who always travels with Raijin, is reserved for the passive / OSINT side (no packets to the target).

## Example

```console
$ raijin-scan --scope scope.txt --max-items 5 hosts.txt
```

```json
{
  "tool": "raijin-scan",
  "summary": "312 hosts scanned, 9 unique findings (2 high), 1840 raw matches collapsed",
  "findings": [
    {
      "id": "exposed-git-config",
      "severity": "high",
      "confidence": "matched",
      "hosts": ["dev.example.com"],
      "evidence": "GET /.git/config -> 200, body contains \"[remote \\\"origin\\\"]\"",
      "engine_ref": "nuclei:git-config"
    }
  ],
  "groups": [
    {"id": "tech-detect:nginx", "count": 241, "examples": ["a.example.com", "b.example.com"]}
  ],
  "omitted": {"info": 1712, "duplicates": 119},
  "errors": [{"hosts": 3, "kind": "timeout", "hint": "retry with --rate 10"}],
  "next": ["raijin-crawl dev.example.com"]
}
```

## Install

> **AI agents:** read [INSTALL.md](INSTALL.md) and follow it. It installs the tools, their engines and the MCP server, with a check after each step.

```bash
git clone https://github.com/protonnegativo/raijin && cd raijin
./install.sh --all    # every tool, the missing engines, and raijin-mcp registered in Claude Code
```

Go, one repo and one binary per tool (`raijin-<verb>`), all sharing the Raijin Schema and the same flags. Engines are external binaries found on `PATH`; a missing engine is reported with an install hint.

## Responsible use

Raijin is for authorized testing only: your own assets, pentests with written scope, and bug bounty programs within their rules. Every tool requires an explicit scope and refuses anything outside it.
