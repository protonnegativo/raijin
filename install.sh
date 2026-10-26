#!/usr/bin/env bash
# Install the Raijin tools, optionally their engines, and register the MCP server.
#
#   ./install.sh                 install every raijin-<verb> binary
#   ./install.sh --engines       also install the engines that are missing (nuclei, httpx, ...), at the
#                                versions each tool was tested with (its engines.json)
#   ./install.sh --mcp           also register raijin-mcp with Claude Code (user scope)
#   ./install.sh --all           both
#   ./install.sh --force         the engines at their latest version instead, even untested
#   ./install.sh --pinned        the tested versions, also over the engines already on PATH
#   RAIJIN_TOOLS="scan probe" ./install.sh   only these tools (raijin-mcp is always added)
#
# Safe to run again: it reinstalls the latest tools and skips engines already on PATH (unless --pinned).
# It never uses sudo: system packages (nmap, libpcap) are printed as a hint instead.
# Ends with a status table; exit 0 when every requested tool installed, 1 otherwise.
set -uo pipefail

ALL_TOOLS="scan probe subs ports crawl js params fuzz tls secrets xss cors takeover diff mcp"
OWNER=github.com/protonnegativo
LOG=$(mktemp -d "${TMPDIR:-/tmp}/raijin-install.XXXXXX")
want_engines=0 want_mcp=0 want_pinned=0 want_force=0
for a in "$@"; do
  case "$a" in
    --engines) want_engines=1 ;;
    --mcp) want_mcp=1 ;;
    --all) want_engines=1 want_mcp=1 ;;
    --pinned) want_engines=1 want_pinned=1 ;;
    --force) want_engines=1 want_force=1 ;;
    -h|--help) sed -n 2,16p "$0"; exit 0 ;;
    *) echo "unknown option: $a" >&2; exit 1 ;;
  esac
done
[ $want_pinned = 1 ] && [ $want_force = 1 ] && { echo "--pinned and --force do not go together" >&2; exit 1; }

fail() { echo "error: $*" >&2; exit 1; }

# 1. Go 1.22+
command -v go >/dev/null || fail "Go is not installed. Install Go 1.22+ from https://go.dev/dl/ and run this again."
gov=$(go env GOVERSION | sed 's/^go//')
[ "$(printf '%s\n1.22\n' "${gov%%[!0-9.]*}" | sort -V | head -1)" = "1.22" ] || fail "Go $gov is too old; Raijin needs 1.22+."
GOBIN=$(go env GOBIN); [ -n "$GOBIN" ] || GOBIN="$(go env GOPATH)/bin"
mkdir -p "$GOBIN"
case ":$PATH:" in *":$GOBIN:"*) ;; *) export PATH="$GOBIN:$PATH"; path_hint=1 ;; esac

# 2. Access: the repos are private for now, so Go must fetch them with your git credentials.
export GOPRIVATE="${GOPRIVATE:+$GOPRIVATE,}$OWNER/*"
if ! git ls-remote "https://$OWNER/raijin-scan" HEAD >/dev/null 2>&1; then
  fail "cannot read $OWNER/raijin-scan with git. Log in with an account that has access: gh auth login && gh auth setup-git"
fi

# 3. Raijin tools
tools="${RAIJIN_TOOLS:-$ALL_TOOLS}"
case " $tools " in *" mcp "*) ;; *) tools="$tools mcp" ;; esac
declare -A status
for v in $tools; do
  if go install "$OWNER/raijin-$v/cmd/raijin-$v@latest" 2>$LOG/raijin-install-$v.log; then
    status[$v]=ok
  else
    status[$v]="FAILED (see $LOG/raijin-install-$v.log)"
  fi
done

# 4. Engines: binary name, then how to install it
declare -A engine_for=(
  [scan]=nuclei [probe]=httpx [subs]="subfinder dnsx" [ports]="naabu nmap" [crawl]=katana [js]=katana
  [params]=arjun [fuzz]=ffuf [tls]=tlsx [secrets]=trufflehog [xss]=dalfox [cors]= [takeover]=dnsx [diff]= [mcp]=
)
declare -A install_cmd=(
  [nuclei]="go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
  [httpx]="go install github.com/projectdiscovery/httpx/cmd/httpx@latest"
  [subfinder]="go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
  [dnsx]="go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
  [naabu]="go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
  [katana]="go install github.com/projectdiscovery/katana/cmd/katana@latest"
  [tlsx]="go install github.com/projectdiscovery/tlsx/cmd/tlsx@latest"
  [ffuf]="go install github.com/ffuf/ffuf/v2@latest"
  [dalfox]="go install github.com/hahwul/dalfox/v2@latest"
  [trufflehog]="go install github.com/trufflesecurity/trufflehog/v3@latest"
  [arjun]="pipx install arjun"
  [nmap]=""
)
declare -A hint=(
  [nmap]="system package: apt install nmap / brew install nmap (raijin-ports runs without it, with --no-services)"
  [naabu]="go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest (needs libpcap: apt install libpcap-dev / brew install libpcap)"
  [arjun]="pipx install arjun (or pip install --user arjun)"
)
engines=$(for v in $tools; do echo ${engine_for[$v]:-}; done | tr ' ' '\n' | sort -u | grep -v '^$')

# Tested versions (unless --force): each tool ships engines.json with the engine versions its fixtures
# were made with. Read it from the module Go just downloaded; the first tool that names an engine sets
# its version. --force keeps the tested version only for engines with a "below" bound (known broken
# from that version on, e.g. dnsx 1.3).
declare -A pinned
if [ $want_engines = 1 ] && { [ $want_force = 0 ] || command -v python3 >/dev/null; }; then
  command -v python3 >/dev/null || fail "the tested engine versions need python3 to read engines.json (or use --force for the latest)"
  for v in $tools; do
    dir=$(go mod download -json "$OWNER/raijin-$v@latest" 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("Dir",""))')
    [ -f "$dir/engines.json" ] || continue
    while IFS=' ' read -r e ver kind src below; do
      [ $want_force = 1 ] && [ -z "$below" ] && continue
      if [ -n "${pinned[$e]:-}" ]; then
        read -r first _ <<<"${pinned[$e]}"
        [ "$first" = "$ver" ] || echo "note: raijin-$v was tested with $e $ver, an earlier tool with $first; installing $first" >&2
        continue
      fi
      pinned[$e]="$ver $kind $src"
      case $kind in
        go) install_cmd[$e]="go install $src@v$ver" ;;
        pip) install_cmd[$e]="pipx install --force $src==$ver" ;;
      esac
    done < <(python3 -c 'import json,sys
for e,v in json.load(open(sys.argv[1])).items():
    kind=next((k for k in ("go","pip","system") if k in v),"")
    print(e, v.get("version",""), kind, v.get(kind,""), v.get("below",""))' "$dir/engines.json")
  done
fi

declare -A estatus
for e in $engines; do
  read -r pver pkind psrc <<<"${pinned[$e]:-}"
  [ "$pkind" = system ] && pver=""   # system packages are never installed by this script
  # on PATH: kept, unless --pinned asks for the tested version
  if { [ $want_pinned = 0 ] || [ -z "$pver" ]; } && command -v "$e" >/dev/null; then estatus[$e]=ok; continue; fi
  if [ $want_engines = 1 ] && [ -n "${install_cmd[$e]:-}" ]; then
    cmd=${install_cmd[$e]}
    if [ "$e" = arjun ] && ! command -v pipx >/dev/null; then
      pkg=arjun; [ -n "$pver" ] && pkg="arjun==$pver"
      cmd="python3 -m pip install --user $pkg"
    fi
    if $cmd >$LOG/raijin-install-$e.log 2>&1 && command -v "$e" >/dev/null; then
      estatus[$e]="ok (installed${pver:+ v$pver})"
      at=$(command -v "$e")
      if [ "$pkind" = go ] && [ "$at" != "$GOBIN/$e" ]; then estatus[$e]+="; but $at comes first on PATH"; fi
      continue
    fi
  fi
  estatus[$e]="missing: ${hint[$e]:-${install_cmd[$e]:-}}"
done

# 5. MCP
mcp_line="not registered (run with --mcp, or see INSTALL.md for other clients)"
if [ $want_mcp = 1 ] && [ "${status[mcp]}" = ok ]; then
  if command -v claude >/dev/null; then
    claude mcp remove raijin -s user >/dev/null 2>&1
    if claude mcp add raijin -s user -- "$GOBIN/raijin-mcp" >$LOG/raijin-install-mcp-add.log 2>&1; then
      mcp_line="registered in Claude Code as \"raijin\" (user scope); restart the session to load it"
    else
      mcp_line="claude mcp add failed (see $LOG/raijin-install-mcp-add.log)"
    fi
  else
    mcp_line="claude CLI not found; add {\"command\": \"$GOBIN/raijin-mcp\"} to your MCP client config"
  fi
fi

# 6. Status
rc=0
echo "Raijin tools ($GOBIN):"
for v in $tools; do
  printf '  raijin-%-9s %s\n' "$v" "${status[$v]}"
  [ "${status[$v]}" = ok ] || rc=1
done
echo "Engines:"
for e in $engines; do printf '  %-11s %s\n' "$e" "${estatus[$e]}"; done
echo "MCP: $mcp_line"
[ "${path_hint:-0}" = 1 ] && echo "PATH: add $GOBIN to PATH (export PATH=\"$GOBIN:\$PATH\")"
exit $rc
