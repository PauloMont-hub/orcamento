# Orçamento

Controlo simples de gastos pessoais por ciclo de salário.

Define um plafond mensal, regista cada despesa por categoria e gera um painel
que mostra quanto já gastaste, quanto falta e onde está a ir o dinheiro.

## Como funciona

- O ciclo vai do dia 24 ao dia 23 do mês seguinte (dia do salário).
- Os dados ficam num único ficheiro JSON (`dados-orcamento.json`).
- O script `gerar_painel.py` lê o JSON e gera o painel em HTML (`painel.html`).
- Alerta quando o gasto atinge 90% do plafond.

## Utilização

    python3 gerar_painel.py dados-orcamento.json painel.html

Depois abre o `painel.html` no browser.

## Estrutura dos dados

Vê `dados-exemplo.json` para o formato: plafond, categorias (com cor),
ciclo atual e lista de despesas (`data`, `categoria`, `descricao`, `valor`).

## Estado

Versão pessoal a funcionar. Em desenvolvimento: app para outras pessoas usarem.
