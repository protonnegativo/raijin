# Installing Raijin (for AI agents and humans)

This file is written so an AI agent (Claude Code, Cursor, Codex, ...) can install Raijin by itself. Each step says what to run, how to check it worked, and what to do if it did not. Run the steps in order. Do not use `sudo` without asking the user.

## TL;DR

```bash
git clone https://github.com/protonnegativo/raijin && cd raijin
./install.sh --all      # tools + missing engines + MCP server registered in Claude Code
```

The script ends with a status table. Every `raijin-*` line must say `ok`. An engine line that says `missing: ...` gives the command that installs it. Then restart the agent session so it loads the MCP server.

## Step 1: Go 1.22+

```bash
go version
```

- **Pass:** `go1.22` or newer.
- **Fail:** install Go from https://go.dev/dl/ (or `brew install go`, or the distro package if it is 1.22+). Ask the user before installing system packages.

## Step 2: access to the repos

The Raijin repos are private for now, so Go fetches them with your git credentials.

```bash
git ls-remote https://github.com/protonnegativo/raijin-scan HEAD
```

- **Pass:** prints a commit hash.
- **Fail:** the account has no access, or git has no credentials. Ask the user to run `gh auth login` and then `gh auth setup-git` (interactive: in Claude Code the user types `! gh auth login`). The account must have been granted access to the repos.

`install.sh` sets `GOPRIVATE=github.com/protonnegativo/*` itself. To install by hand, export it first.

## Step 3: the tools

```bash
./install.sh                          # every tool
RAIJIN_TOOLS="scan probe" ./install.sh   # only some (raijin-mcp is always added)
```

By hand, the same thing per tool:

```bash
export GOPRIVATE=github.com/protonnegativo/*
go install github.com/protonnegativo/raijin-scan/cmd/raijin-scan@latest
```

- **Check:** `raijin-scan --version` prints `raijin-scan 0.1.0`.
- **Fail:** `command not found` means `$(go env GOPATH)/bin` is not on `PATH`. The script prints the `export PATH=...` line to add.
- **Fail:** a `FAILED` line in the table points to its log file. Read the log and fix the cause.

## Step 4: the engines

Each tool runs a proven engine underneath and finds it on `PATH`. `./install.sh --engines` installs the missing Go and Python ones. It never installs system packages; for those it prints the command for the user to approve.

| Engine | Used by | Install |
|---|---|---|
| nuclei | raijin-scan | `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` |
| httpx | raijin-probe | `go install github.com/projectdiscovery/httpx/cmd/httpx@latest` |
| subfinder + dnsx | raijin-subs | `go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` and `go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest` |
| naabu (+ nmap) | raijin-ports | `go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest` (needs libpcap: `apt install libpcap-dev`); nmap: `apt install nmap`, optional (`--no-services` works without it) |
| katana | raijin-crawl, raijin-js | `go install github.com/projectdiscovery/katana/cmd/katana@latest` |
| arjun | raijin-params | `pipx install arjun` (or `pip install --user arjun`) |
| ffuf | raijin-fuzz | `go install github.com/ffuf/ffuf/v2@latest` |
| tlsx | raijin-tls | `go install github.com/projectdiscovery/tlsx/cmd/tlsx@latest` |
| trufflehog | raijin-secrets | `go install github.com/trufflesecurity/trufflehog/v3@latest` |
| dalfox | raijin-xss | `go install github.com/hahwul/dalfox/v2@latest` |
| dnsx | raijin-takeover | as above |
| (none) | raijin-cors, raijin-diff, raijin-mcp | native |

`./install.sh --pinned` installs each engine at the version its tool was tested with, read from the tool's `engines.json`, instead of keeping whatever is on `PATH`. Use it when results must match the benchmarks exactly, for example during an engagement. Without it, the latest engine is used, which is what the weekly drift job (below) checks.

You only need the engines of the tools you use. A tool whose engine is missing still runs: it exits 2 and its JSON has an `errors` entry of kind `missing_engine` with the install command.

## Step 5: the MCP server

`raijin-mcp` exposes every installed tool to the agent as an MCP tool (`raijin_scan`, `raijin_probe`, ...).

**Claude Code** (what `./install.sh --mcp` does):

```bash
claude mcp add raijin -s user -- "$(go env GOPATH)/bin/raijin-mcp"
```

- **Check:** `claude mcp list` shows `raijin` as connected. After restarting the session, the agent sees the `raijin_*` tools.

**Cursor, Claude Desktop and other MCP clients:** add this to the client's MCP config (for Cursor, `~/.cursor/mcp.json`). Use the absolute path that `command -v raijin-mcp` prints:

```json
{ "mcpServers": { "raijin": { "command": "/home/you/go/bin/raijin-mcp" } } }
```

- **Check without a client:** `raijin-mcp --list` prints the tools it would expose. A tool whose binary is missing is not listed. `raijin-mcp --list --list-missing` also shows the missing ones, with the hint to install each.

## Step 6: smoke test

These two commands send no traffic.

```bash
raijin-diff --version && raijin-scan --version
raijin-mcp --list | head -c 300; echo
```

- **Pass:** both versions print, and `--list` prints JSON that starts with `{"tools":[`.

## Using it

Every tool needs a scope file with the authorized targets: one rule per line (`example.com`, `*.example.com`, `10.0.0.0/24`, `!excluded.example.com`). With only `--scope`, a tool works on every host the scope names, so this is a full run:

```bash
raijin-scan --scope scope.txt
```

Through MCP, pass only the scope: `{"scope": ["example.com", "*.example.com"]}`.

The output is one compact JSON line (the Raijin Schema, see [docs/schema.md](docs/schema.md)). Read `findings` first. `next` holds the exact follow-up commands, for example enumerating a wildcard with `raijin-subs` before scanning it. `raw` is the engine's full output on disk, for details. To scan only after explicit authorization, see [Responsible use](README.md#responsible-use).

## Engine updates

Each tool records the engine versions it was tested with in `engines.json`, and checks the installed engine at run time:

- `errors` kind `engine_version`: the installed engine has another major version, or is older than the tested one. The hint has the command that installs the tested version.
- `errors` kind `engine_format`: the engine's output lacks fields the tool needs, so its format probably changed. Those results are counted in `omitted.unparsed`, and the full output is in `raw`.

An agent that sees either error should trust `raw` over the summary for that run, and tell the user.

Every tool repo also runs two GitHub Actions workflows:

- `ci`, on every push: vet, format, tests, and the offline benchmark. It fails if any engine result is missing from the output.
- `engine-drift`, weekly (Monday 06:00 UTC) and on demand: installs the latest engine and runs the live benchmark against the local lab in the runner.
  - If something is missing or the format changed, it opens an issue labeled `engine-drift`.
  - If everything passes on a newer engine, it opens a PR that bumps `engines.json`. Merging that PR updates the tested versions that `--pinned` installs.

## Update and uninstall

- **Update:** run `./install.sh` again. It installs the latest version of each tool.
- **Uninstall:**

  ```bash
  claude mcp remove raijin -s user
  rm "$(go env GOPATH)"/bin/raijin-*
  ```
