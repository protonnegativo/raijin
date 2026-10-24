<p align="right"><a href="README.md">🇺🇸 English</a> · <b>🇧🇷 Português</b></p>

# ⚡ Raijin

**Ferramentas ofensivas feitas para IA. Sinal, não ruído.**

Raijin é um arsenal de ferramentas de segurança pensado para ser usado por agentes de IA. Cada ferramenta roda por baixo um motor já consagrado (nuclei, httpx, katana, ffuf...). Em vez de despejar milhares de linhas brutas, devolve um **JSON pequeno, sem duplicatas e ranqueado**, que um LLM consegue ler sem estourar o contexto.

> Status: ideia e design. Ainda não há nada implementado. Veja o [ROADMAP.md](ROADMAP.md).

## O problema

Um agente que roda `nuclei`, `ffuf` ou `katana` recebe de volta:

- milhares de linhas, quase todas duplicatas, 404 e info sem valor;
- o mesmo achado repetido em centenas de hosts;
- HTML inteiro onde bastava um header;
- stack trace em vez de "o que fazer agora".

O agente gasta o contexto com ruído, perde o achado real e entra em loop.

## A ideia

Toda ferramenta Raijin é **um wrapper e um redutor**:

```
alvo ──▶ motor (nuclei, httpx...) ──▶ saída bruta ──▶ redutor Raijin ──▶ Raijin Schema (JSON)
```

O motor faz o scan. O Raijin faz o que o agente faz mal: **comprimir o resultado no que importa**.

## Princípios

1. **Orçamento de tokens.** Cada ferramenta aceita `max_items` e `max_bytes`, devolve os N melhores e resume o que ficou de fora.
2. **O mesmo schema em todas as ferramentas** ([docs/schema.md](docs/schema.md)).
3. **Agrupar sem repetir e sem perder.** 500 hosts com o mesmo achado viram uma entrada só, que lista cada local uma vez, em vez de 500 cópias do mesmo template, título e metadados. Nada que foi achado some calado.
4. **Evidência mínima.** Cada achado traz só o trecho que o prova.
5. **Confiança, além de severidade:** `verified`, `matched` ou `heuristic`.
6. **Diff por padrão.** Com `--state`, uma nova execução mostra só o que mudou.
7. **Erros acionáveis.** Cada erro diz o que tentar a seguir.
8. **Próximo passo sugerido** no campo `next`.
9. **Escopo primeiro.** Toda ferramenta exige um escopo explícito e recusa o que estiver fora dele.

## O arsenal

O padrão é `raijin-<verbo>`. Todas as ferramentas usam o mesmo schema e as mesmas flags. A tabela completa, com o motor de cada ferramenta e o que o Raijin reduz, está no [README em inglês](README.md#the-arsenal).

| Ferramenta | Motor |
|---|---|
| raijin-probe | httpx |
| raijin-subs | subfinder + dnsx |
| raijin-ports | naabu |
| raijin-crawl | katana |
| raijin-js | katana + parsing de JS |
| raijin-params | arjun / x8 |
| raijin-scan | nuclei |
| raijin-fuzz | ffuf |
| raijin-tls | tlsx |
| raijin-secrets | trufflehog |
| raijin-xss | dalfox |
| raijin-cors | nativo |
| raijin-takeover | dnsx + fingerprints |
| raijin-diff | nativo |
| raijin-mcp | servidor MCP com todas as ferramentas |

**Fūjin**, o deus do vento que anda sempre com o Raijin, fica reservado para a parte passiva e de OSINT, que não manda nenhum pacote ao alvo.

## Uso responsável

O Raijin é só para teste autorizado: seus próprios ativos, pentests com escopo por escrito e programas de bug bounty dentro das regras de cada um.
