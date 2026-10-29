# Roadmap

## v0.1: the base
- [x] `raijin-core`: scope check, Raijin Schema envelope and state, shared by every tool: [protonnegativo/raijin-core](https://github.com/protonnegativo/raijin-core)
- [x] `raijin-probe` (httpx): [protonnegativo/raijin-probe](https://github.com/protonnegativo/raijin-probe)
- [x] `raijin-scan` (nuclei): [protonnegativo/raijin-scan](https://github.com/protonnegativo/raijin-scan)
- [x] `raijin-mcp`: MCP server exposing the tools above: [protonnegativo/raijin-mcp](https://github.com/protonnegativo/raijin-mcp)
- [x] Benchmark: raw engine output vs Raijin output on the same target (lines, bytes, tokens): `BENCHMARK.md` in every tool repo

## v0.2: recon
- [x] `raijin-subs` (subfinder + dnsx): [protonnegativo/raijin-subs](https://github.com/protonnegativo/raijin-subs)
- [x] `raijin-ports` (naabu + nmap): [protonnegativo/raijin-ports](https://github.com/protonnegativo/raijin-ports)
- [x] `raijin-crawl` (katana): [protonnegativo/raijin-crawl](https://github.com/protonnegativo/raijin-crawl)
- [x] `raijin-diff` + `--state` on every tool: [protonnegativo/raijin-diff](https://github.com/protonnegativo/raijin-diff)

## v0.3: discovery and vulns
- [x] `raijin-js` (katana + JS): [protonnegativo/raijin-js](https://github.com/protonnegativo/raijin-js)
- [x] `raijin-params` (arjun): [protonnegativo/raijin-params](https://github.com/protonnegativo/raijin-params)
- [x] `raijin-fuzz` (ffuf): [protonnegativo/raijin-fuzz](https://github.com/protonnegativo/raijin-fuzz)
- [x] `raijin-tls` (tlsx): [protonnegativo/raijin-tls](https://github.com/protonnegativo/raijin-tls)
- [x] `raijin-secrets` (trufflehog): [protonnegativo/raijin-secrets](https://github.com/protonnegativo/raijin-secrets)

## v0.4: confirmation
- [x] `raijin-xss` (dalfox): [protonnegativo/raijin-xss](https://github.com/protonnegativo/raijin-xss)
- [x] `raijin-cors` (native): [protonnegativo/raijin-cors](https://github.com/protonnegativo/raijin-cors)
- [x] `raijin-takeover` (dnsx + fingerprints): [protonnegativo/raijin-takeover](https://github.com/protonnegativo/raijin-takeover)
- [ ] `confidence: verified` paths for each

## Later
- [ ] Fūjin: passive / OSINT companion (no packets to the target)
- [ ] QuarkScan integration (use Raijin tools as its agents' tools)

## Open questions
- ~~One package per tool, or one package with every command?~~ Decided: Go, one repo and binary per tool.
- Default `max_items`: 20? Configurable per agent context size?
- How to rank `heuristic` findings without hiding real issues?
