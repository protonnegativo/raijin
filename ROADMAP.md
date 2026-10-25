# Roadmap

## v0.1: the base
- [ ] `raijin-core`: Raijin Schema, reducer helpers (dedup, group, rank, trim, budget), scope check, engine discovery on `PATH`
- [x] `raijin-probe` (httpx): [protonnegativo/raijin-probe](https://github.com/protonnegativo/raijin-probe) (private)
- [x] `raijin-scan` (nuclei): [protonnegativo/raijin-scan](https://github.com/protonnegativo/raijin-scan)
- [x] `raijin-mcp`: MCP server exposing the tools above: [protonnegativo/raijin-mcp](https://github.com/protonnegativo/raijin-mcp) (private)
- [x] Benchmark: raw engine output vs Raijin output on the same target (lines, bytes, tokens): `BENCHMARK.md` in every tool repo

## v0.2: recon
- [x] `raijin-subs` (subfinder + dnsx): [protonnegativo/raijin-subs](https://github.com/protonnegativo/raijin-subs) (private)
- [x] `raijin-ports` (naabu + nmap): [protonnegativo/raijin-ports](https://github.com/protonnegativo/raijin-ports) (private)
- [x] `raijin-crawl` (katana): [protonnegativo/raijin-crawl](https://github.com/protonnegativo/raijin-crawl) (private)
- [x] `raijin-diff` + `--state` on every tool: [protonnegativo/raijin-diff](https://github.com/protonnegativo/raijin-diff) (private)

## v0.3: discovery and vulns
- [x] `raijin-js` (katana + JS): [protonnegativo/raijin-js](https://github.com/protonnegativo/raijin-js) (private)
- [x] `raijin-params` (arjun): [protonnegativo/raijin-params](https://github.com/protonnegativo/raijin-params) (private)
- [x] `raijin-fuzz` (ffuf): [protonnegativo/raijin-fuzz](https://github.com/protonnegativo/raijin-fuzz) (private)
- [x] `raijin-tls` (tlsx): [protonnegativo/raijin-tls](https://github.com/protonnegativo/raijin-tls) (private)
- [x] `raijin-secrets` (trufflehog): [protonnegativo/raijin-secrets](https://github.com/protonnegativo/raijin-secrets) (private)

## v0.4: confirmation
- [x] `raijin-xss` (dalfox): [protonnegativo/raijin-xss](https://github.com/protonnegativo/raijin-xss) (private)
- [x] `raijin-cors` (native): [protonnegativo/raijin-cors](https://github.com/protonnegativo/raijin-cors) (private)
- [x] `raijin-takeover` (dnsx + fingerprints): [protonnegativo/raijin-takeover](https://github.com/protonnegativo/raijin-takeover) (private)
- [ ] `confidence: verified` paths for each

## Later
- [ ] Fūjin: passive / OSINT companion (no packets to the target)
- [ ] QuarkScan integration (use Raijin tools as its agents' tools)

## Open questions
- ~~One package per tool, or one package with every command?~~ Decided: Go, one repo and binary per tool.
- Default `max_items`: 20? Configurable per agent context size?
- How to rank `heuristic` findings without hiding real issues?
