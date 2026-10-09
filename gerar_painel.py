#!/usr/bin/env python3
"""Gera o painel de orçamento (painel.html) a partir de dados-orcamento.json.

Uso:  python gerar_painel.py [dados.json] [saida.html]
Fonte de dados única = o JSON. Este script calcula tudo (nunca fazer contas à mão).
"""
import json, sys, html
from datetime import date

DADOS = sys.argv[1] if len(sys.argv) > 1 else "dados-orcamento.json"
SAIDA = sys.argv[2] if len(sys.argv) > 2 else "painel.html"

with open(DADOS, encoding="utf-8") as f:
    d = json.load(f)

plafond   = float(d["plafond"])
simbolo   = d.get("simbolo", "€")
limiar    = float(d.get("limiar_alerta", 0.9))
cats      = d["categorias"]
ciclo     = d["ciclo_atual"]
despesas  = ciclo.get("despesas", [])

MESES = ["", "jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]

def d_pt(iso):
    y, m, dd = map(int, iso.split("-"))
    return f"{dd} {MESES[m]}"

def d_pt_ano(iso):
    y, m, dd = map(int, iso.split("-"))
    return f"{dd} {MESES[m]} {y}"

def eur(v):
    s = f"{v:,.2f}"                       # 1,234.50
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {simbolo}"

# ---- cálculos ----
total = round(sum(float(x["valor"]) for x in despesas), 2)
restante = round(plafond - total, 2)
pct = (total / plafond) if plafond else 0
pct_txt = f"{round(pct*100)}%"
bar_w = min(pct, 1.0) * 100

por_cat = {c["nome"]: 0.0 for c in cats}
for x in despesas:
    por_cat[x["categoria"]] = round(por_cat.get(x["categoria"], 0.0) + float(x["valor"]), 2)
max_cat = max(por_cat.values()) if por_cat else 0

# estado / semáforo
if pct > 1.0:
    estado_txt, estado_cls = "Plafond ultrapassado", "st-danger"
    bar_col = "var(--danger)"
elif pct >= limiar:
    estado_txt, estado_cls = f"Atenção · {round(limiar*100)}% atingido", "st-warn"
    bar_col = "var(--warn)"
else:
    estado_txt, estado_cls = "Dentro do plafond", "st-ok"
    bar_col = "linear-gradient(90deg, var(--accent), var(--good))"

restante_cls = "neg" if restante < 0 else ""
ciclo_label = f"{d_pt(ciclo['inicio'])} – {d_pt_ano(ciclo['fim'])}"
hoje = d.get("atualizado", date.today().isoformat())
atualizado_txt = d_pt_ano(hoje)

# ---- blocos HTML ----
cat_html = []
for c in cats:
    nome = html.escape(c["nome"]); cor = c["cor"]
    v = por_cat.get(c["nome"], 0.0)
    w = (v / max_cat * 100) if max_cat else 0
    share = f"{round(v/total*100)}% do total" if total else "sem gastos"
    cat_html.append(f"""
    <div class="cat">
      <div class="cat-name"><span class="swatch" style="background:{cor}"></span>{nome}</div>
      <div class="cat-val">{eur(v)}</div>
      <div class="cat-bar"><span style="width:{w:.1f}%;background:{cor}"></span></div>
      <div class="cat-pct">{share}</div>
    </div>""")
cats_html = "".join(cat_html)

cor_por_cat = {c["nome"]: c["cor"] for c in cats}
if despesas:
    linhas = []
    for x in sorted(despesas, key=lambda e: e["data"], reverse=True):
        cor = cor_por_cat.get(x["categoria"], "#888")
        linhas.append(f"""
        <tr>
          <td class="num">{html.escape(d_pt(x['data']))}</td>
          <td><span class="tag" style="background:{cor}22;color:{cor}">{html.escape(x['categoria'])}</span></td>
          <td>{html.escape(x.get('descricao',''))}</td>
          <td class="amount">{eur(float(x['valor']))}</td>
        </tr>""")
    movimentos = f"""
    <div class="table-scroll">
      <table>
        <thead><tr><th>Data</th><th>Categoria</th><th>Descrição</th><th class="amount">Valor</th></tr></thead>
        <tbody>{''.join(linhas)}</tbody>
      </table>
    </div>"""
    n_reg = f"{len(despesas)} registo{'s' if len(despesas)!=1 else ''}"
else:
    movimentos = """
    <div class="empty">
      <div class="big">Ainda sem gastos neste ciclo</div>
      <div>Começa a registar e a tabela preenche-se sozinha.</div>
      <div class="hint">Escreve-me, por exemplo: <code>gastei 12€ em tabaco</code></div>
    </div>"""
    n_reg = "0 registos"

TEMPLATE = """<title>Orçamento do ciclo</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Public+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
  :root {
    --bg:#f3f5f1; --surface:#ffffff; --surface-2:#f7f9f5;
    --ink:#1a231e; --muted:#5d6a62; --faint:#8a978e;
    --line:#e2e7df; --accent:#0e6e5c; --accent-soft:#daece6;
    --good:#2e8b57; --warn:#c0801a; --warn-soft:#f6ecd6; --danger:#b53a34; --danger-soft:#f6dcda;
    --shadow:0 1px 2px rgba(26,35,30,.04), 0 8px 24px rgba(26,35,30,.06);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg:#12160f; --surface:#1a1f18; --surface-2:#202619;
      --ink:#eef2e8; --muted:#9fab9f; --faint:#74806f;
      --line:#2a3126; --accent:#4fc9a9; --accent-soft:#173b32;
      --good:#5cc98a; --warn:#e0aa4e; --warn-soft:#33290f; --danger:#eb7b74; --danger-soft:#3a1e1c;
      --shadow:0 1px 2px rgba(0,0,0,.3), 0 10px 30px rgba(0,0,0,.35);
    }
  }
  :root[data-theme="dark"] {
    --bg:#12160f; --surface:#1a1f18; --surface-2:#202619;
    --ink:#eef2e8; --muted:#9fab9f; --faint:#74806f;
    --line:#2a3126; --accent:#4fc9a9; --accent-soft:#173b32;
    --good:#5cc98a; --warn:#e0aa4e; --warn-soft:#33290f; --danger:#eb7b74; --danger-soft:#3a1e1c;
    --shadow:0 1px 2px rgba(0,0,0,.3), 0 10px 30px rgba(0,0,0,.35);
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
    font-family:"Public Sans",system-ui,sans-serif; line-height:1.5; -webkit-font-smoothing:antialiased; }
  .wrap { max-width:820px; margin:0 auto; padding:40px 22px 72px; }
  .num { font-family:"IBM Plex Mono",ui-monospace,monospace; font-variant-numeric:tabular-nums; }
  header.top { margin-bottom:26px; }
  .eyebrow { font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--accent); font-weight:600; margin:0 0 6px; }
  h1 { font-family:"Bricolage Grotesque",sans-serif; font-weight:800; font-size:clamp(28px,5.5vw,42px);
    line-height:1.02; margin:0; letter-spacing:-.02em; text-wrap:balance; }
  .sub { color:var(--muted); margin:8px 0 0; font-size:15px; }
  .hero { background:var(--surface); border:1px solid var(--line); border-radius:18px; box-shadow:var(--shadow); padding:26px 26px 24px; margin-bottom:22px; }
  .hero-head { display:flex; justify-content:space-between; align-items:baseline; gap:16px; flex-wrap:wrap; margin-bottom:18px; }
  .hero-label { font-size:13px; color:var(--muted); font-weight:500; }
  .remaining { font-family:"Bricolage Grotesque",sans-serif; font-weight:800; font-size:clamp(38px,9vw,60px);
    line-height:1; letter-spacing:-.03em; color:var(--ink); display:flex; align-items:baseline; gap:6px; }
  .remaining.neg { color:var(--danger); }
  .remaining .cur { font-size:.5em; color:var(--muted); font-weight:700; }
  .status-pill { display:inline-flex; align-items:center; gap:7px; font-size:13px; font-weight:600; padding:6px 12px; border-radius:999px; }
  .status-pill .dot { width:8px; height:8px; border-radius:50%; background:currentColor; }
  .st-ok { background:var(--accent-soft); color:var(--accent); }
  .st-warn { background:var(--warn-soft); color:var(--warn); }
  .st-danger { background:var(--danger-soft); color:var(--danger); }
  .bar { height:14px; border-radius:999px; background:var(--surface-2); border:1px solid var(--line); overflow:hidden; margin:4px 0 14px; }
  .bar > span { display:block; height:100%; border-radius:999px; transition:width .6s ease; }
  .hero-foot { display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; font-size:14px; color:var(--muted); }
  .hero-foot b { color:var(--ink); font-weight:600; }
  .sec-title { font-family:"Bricolage Grotesque",sans-serif; font-weight:700; font-size:18px; margin:30px 0 14px; display:flex; align-items:center; gap:10px; }
  .sec-title .count { font-size:13px; color:var(--faint); font-weight:500; font-family:"IBM Plex Mono",monospace; }
  .cats { display:grid; gap:10px; }
  .cat { background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:14px 16px;
    display:grid; grid-template-columns:1fr auto; gap:2px 12px; align-items:center; }
  .cat-name { font-weight:600; font-size:15px; display:flex; align-items:center; gap:9px; }
  .swatch { width:10px; height:10px; border-radius:3px; flex:none; }
  .cat-val { font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums; font-weight:600; font-size:15px; text-align:right; }
  .cat-bar { grid-column:1 / -1; height:7px; border-radius:999px; background:var(--surface-2); overflow:hidden; margin-top:6px; }
  .cat-bar > span { display:block; height:100%; border-radius:999px; }
  .cat-pct { grid-column:1 / -1; font-size:12px; color:var(--faint); margin-top:3px; }
  .ledger-wrap { border:1px solid var(--line); border-radius:14px; overflow:hidden; background:var(--surface); box-shadow:var(--shadow); }
  .table-scroll { overflow-x:auto; }
  table { width:100%; border-collapse:collapse; min-width:460px; }
  th, td { text-align:left; padding:12px 16px; font-size:14px; border-bottom:1px solid var(--line); }
  th { font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--faint); font-weight:600; background:var(--surface-2); }
  tbody tr:last-child td { border-bottom:none; }
  td.amount, th.amount { text-align:right; font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums; }
  td.amount { font-weight:600; }
  .tag { display:inline-block; font-size:12px; font-weight:600; padding:2px 9px; border-radius:999px; }
  .empty { padding:40px 22px; text-align:center; color:var(--muted); }
  .empty .big { font-family:"Bricolage Grotesque",sans-serif; font-weight:700; color:var(--ink); font-size:17px; margin-bottom:6px; }
  .empty .hint { display:inline-block; margin-top:14px; font-size:13px; background:var(--surface-2); border:1px solid var(--line); padding:8px 14px; border-radius:10px; color:var(--muted); }
  .empty .hint code { font-family:"IBM Plex Mono",monospace; color:var(--accent); }
  footer.foot { margin-top:34px; font-size:12.5px; color:var(--faint); text-align:center; line-height:1.7; }
</style>
<div class="wrap">
  <header class="top">
    <p class="eyebrow">Orçamento · ciclo do salário (24 a 23)</p>
    <h1>__CICLO__</h1>
    <p class="sub">Atualizado a __ATUALIZADO__ · plafond de __PLAFOND__</p>
  </header>
  <section class="hero">
    <div class="hero-head">
      <div>
        <div class="hero-label">__LABEL_RESTANTE__</div>
        <div class="remaining __REST_CLS__"><span class="cur">__SIMB__</span>__RESTANTE__</div>
      </div>
      <span class="status-pill __EST_CLS__"><span class="dot"></span>__ESTADO__</span>
    </div>
    <div class="bar"><span style="width:__BARW__%;background:__BARCOL__"></span></div>
    <div class="hero-foot">
      <span>Gasto: <b class="num">__TOTAL__</b> de <b class="num">__PLAFOND__</b></span>
      <span><b class="num">__PCT__</b> do plafond usado</span>
    </div>
  </section>
  <h2 class="sec-title">Por categoria <span class="count">__NCATS__ categorias</span></h2>
  <div class="cats">__CATS__</div>
  <h2 class="sec-title">Movimentos <span class="count">__NREG__</span></h2>
  <div class="ledger-wrap">__MOV__</div>
  <footer class="foot">
    Painel pessoal de controlo de gastos · valores em euros<br>
    Diz-me sempre que gastares algo e eu atualizo este painel.
  </footer>
</div>"""

label_restante = "Já gastaste a mais" if restante < 0 else "Disponível até 23 do próximo mês"
rest_abs = eur(abs(restante))

out = (TEMPLATE
  .replace("__CICLO__", html.escape(ciclo_label))
  .replace("__ATUALIZADO__", html.escape(atualizado_txt))
  .replace("__PLAFOND__", eur(plafond))
  .replace("__LABEL_RESTANTE__", label_restante)
  .replace("__REST_CLS__", restante_cls)
  .replace("__SIMB__", ("-" + simbolo) if restante < 0 else simbolo)
  .replace("__RESTANTE__", rest_abs.replace(" "+simbolo, "").strip())
  .replace("__EST_CLS__", estado_cls)
  .replace("__ESTADO__", estado_txt)
  .replace("__BARW__", f"{bar_w:.1f}")
  .replace("__BARCOL__", bar_col)
  .replace("__TOTAL__", eur(total))
  .replace("__PCT__", pct_txt)
  .replace("__NCATS__", str(len(cats)))
  .replace("__CATS__", cats_html)
  .replace("__NREG__", n_reg)
  .replace("__MOV__", movimentos)
  .replace("__SIMB__", simbolo)
)

with open(SAIDA, "w", encoding="utf-8") as f:
    f.write(out)
print(f"OK: {SAIDA} | gasto={total} restante={restante} pct={pct_txt} despesas={len(despesas)}")
