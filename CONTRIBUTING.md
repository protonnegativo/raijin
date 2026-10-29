# Contributing to Raijin

Raijin is a set of small tools, one repo each, plus [raijin-core](https://github.com/protonnegativo/raijin-core) for the code they share. This repo holds the overview, the installer and the schema docs.

- **A bug or an idea about one tool:** open the issue in that tool's repo. Include the command, the scope file (without real targets) and the JSON you got.
- **The schema or the exit-code contract** ([docs/schema.md](docs/schema.md)): open an issue here first. Those are promises to every agent that reads the output, so a change is a breaking change.
- **A new tool:** open an issue with the engine you want to wrap and what noise it produces. A tool is a wrapper plus a reducer, and the reducer must never drop a finding silently.
- Keep commits short and in the imperative. `go vet` and `go test ./... -race` must pass in the repo you touch.
- AI-assisted contributions are welcome if you understand and have tested every line.

Raijin is for authorized testing only. Do not send changes meant to scan targets without permission.
