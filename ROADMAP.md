# Roadmap

## v0.1: the base
- [ ] `raijin-core`: Raijin Schema, reducer helpers (dedup, group, rank, trim, budget), scope check, engine discovery on `PATH`
- [x] `raijin-probe` (httpx): [protonnegativo/raijin-probe](https://github.com/protonnegativo/raijin-probe) (private)
- [x] `raijin-scan` (nuclei): [protonnegativo/raijin-scan](https://github.com/protonnegativo/raijin-scan)
- [ ] `raijin-mcp`: MCP server exposing the tools above
- [ ] Benchmark: raw engine output vs Raijin output on the same target (lines, bytes, tokens)

## v0.2: recon
- [ ] `raijin-subs` (subfinder + dnsx)
- [ ] `raijin-ports` (naabu)
- [ ] `raijin-crawl` (katana)
- [ ] `raijin-diff` + `--state` on every tool

## v0.3: discovery and vulns
- [ ] `raijin-js`, `raijin-params`, `raijin-fuzz` (ffuf)
- [ ] `raijin-tls` (tlsx), `raijin-secrets` (trufflehog)

## v0.4: confirmation
- [ ] `raijin-xss` (dalfox), `raijin-cors`, `raijin-takeover`
- [ ] `confidence: verified` paths for each

## Later
- [ ] Fūjin: passive / OSINT companion (no packets to the target)
- [ ] QuarkScan integration (use Raijin tools as its agents' tools)

## Open questions
- ~~One package per tool, or one package with every command?~~ Decided: Go, one repo and binary per tool.
- Default `max_items`: 20? Configurable per agent context size?
- How to rank `heuristic` findings without hiding real issues?
