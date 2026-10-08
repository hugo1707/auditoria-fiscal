#!/usr/bin/env python3
"""Gera o site estático a partir de src/.

Uso:  python tools/build.py

Entrada:
  src/lessons/mX-lY.txt   uma lição por arquivo (cabeçalho + seções "=== nome")
  src/pages/*.html        miolo das páginas avulsas (fontes, bancas)
Saída:
  licoes/*.html, index.html, plano.html, fontes.html, bancas.html, assets/lessons.js
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

SITE = "Auditoria Fiscal · NF-e, EFD e CT-e"

MODULES = [
    (0, "Os arquivos por dentro",
     "Antes das regras, o objeto: como é, de verdade, um XML de NF-e e um arquivo de EFD."),
    (1, "NF-e e DANFE — Ajuste SINIEF 07/05",
     "A vida de uma NF-e, da emissão à guarda: autorização, rejeição, contingência, correção, cancelamento e eventos."),
    (2, "EFD ICMS/IPI — Ajuste SINIEF 02/09",
     "Quem é obrigado, o que se escritura, como o arquivo é validado, entregue e retificado."),
    (3, "CT-e e MDF-e",
     "O transporte no documento eletrônico: Ajuste SINIEF 09/07 e a prova de circulação da carga."),
    (4, "Auditoria com os arquivos",
     "Cruzar o que foi autorizado com o que foi escriturado e ler o resultado como um auditor."),
]

# Semanas do cronograma: ids por dia útil; o sábado é sempre revisão.
WEEKS = [
    ["m0-l1", "m0-l2", "m0-l3", "m0-l4", "m1-l1"],
    ["m1-l2", "m1-l3", "m1-l4", "m1-l5", "m1-l6"],
    ["m1-l7", "m1-l8", "m1-l9", "m2-l1", "m2-l2"],
    ["m2-l3", "m2-l4", "m2-l5", "m2-l6", "m3-l1"],
    ["m3-l2", "m3-l3", "m4-l1", "m4-l2", "m4-l3"],
]
DAYS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

FAVICON = ("<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' "
           "viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧾</text></svg>\">")
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700'
         '&family=Literata:opsz,wght@7..72,400;7..72,600&display=swap" rel="stylesheet">')


# ---------------------------------------------------------------- parsing
def parse_lesson(path: Path):
    text = path.read_text(encoding="utf-8")
    head, _, rest = text.partition("\n=== ")
    rest = "=== " + rest if rest else ""
    meta = {}
    for line in head.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    secs = {}
    for m in re.finditer(r"^=== (\w+)\n(.*?)(?=^=== |\Z)", rest, re.S | re.M):
        secs[m.group(1)] = m.group(2).strip("\n")
    meta["id"] = path.stem
    mod, les = re.match(r"m(\d+)-l(\d+)", path.stem).groups()
    meta["mod"], meta["n"] = int(mod), int(les)
    meta["code"] = f"{mod}.{les}"
    return meta, secs


def fence(text: str) -> str:
    """~~~xml ... ~~~  ->  <pre class="code">, com [[destaque]] -> <mark>."""
    def repl(m):
        lang = m.group(1) or ""
        body = html.escape(m.group(2).strip("\n"), quote=False)
        body = body.replace("[[", "<mark>").replace("]]", "</mark>")
        return f'<pre class="code" data-lang="{lang}"><code>{body}</code></pre>'
    return re.sub(r"^~~~(\w*)\n(.*?)\n~~~$", repl, text, flags=re.S | re.M)


def lis(text: str) -> str:
    return "".join(f"<li>{l.strip()[2:].strip()}</li>" for l in text.splitlines() if l.strip().startswith("- "))


# ---------------------------------------------------------------- templates
def page(title, body, depth=0, cls="", extra_head=""):
    p = "../" * depth
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#16323F">
<title>{html.escape(title)}</title>
{FONTS}
<link rel="stylesheet" href="{p}assets/style.css">
{FAVICON}
{extra_head}</head>
<body class="{cls}">
<header class="top"><a href="{p}index.html" class="brand">{SITE}</a><nav><a href="{p}plano.html">Cronograma</a><a href="{p}bancas.html">Bancas</a><a href="{p}fontes.html">Fontes</a></nav></header>
<main>
{body}
</main>
<script src="{p}assets/lessons.js"></script>
<script src="{p}assets/app.js"></script>
</body>
</html>
"""


def render_lesson(meta, secs, prev, nxt):
    mod_title = dict((m[0], m[1]) for m in MODULES)[meta["mod"]]
    parts = []
    parts.append(f'<article class="lesson" data-id="{meta["id"]}">')
    parts.append(
        '<div class="form">'
        f'<div class="cell c-mod"><span>Módulo {meta["mod"]}</span>{html.escape(mod_title)}</div>'
        f'<div class="cell"><span>Lição</span>{meta["code"]}</div>'
        f'<div class="cell"><span>Tempo</span>{meta["min"]} min</div>'
        f'<div class="cell c-norma"><span>Norma principal</span>{meta["norma"]}</div>'
        '</div>')
    parts.append(f'<h1>{meta["title"]}</h1>')
    parts.append(f'<p class="obj">{meta["obj"]}</p>')
    parts.append(f'<div class="content">\n{fence(secs["content"])}\n</div>')
    if secs.get("caso"):
        parts.append(f'<section class="caso"><h2>Caso resolvido</h2>{fence(secs["caso"])}</section>')
    if secs.get("armadilhas"):
        parts.append(f'<section class="armadilhas"><h2>Onde o texto engana</h2><ul>{lis(secs["armadilhas"])}</ul></section>')
    if secs.get("bancas"):
        parts.append(f'<section class="bancas"><h2>Como as bancas costumam cobrar</h2><ul>{lis(secs["bancas"])}</ul>'
                     '<p class="hint">Padrões de formulação, não questões. Veja o <a href="../bancas.html">guia por estilo de banca</a>.</p></section>')
    if secs.get("auditor"):
        parts.append(f'<aside class="auditor"><h2>No olhar do auditor</h2><p>{secs["auditor"]}</p></aside>')
    if secs.get("base"):
        parts.append(f'<section class="base"><h2>Base normativa</h2><ul>{lis(secs["base"])}</ul>'
                     '<p class="hint">Confira a redação vigente no texto consolidado: prazos e dispositivos mudam por alteração do Ajuste.</p></section>')
    if secs.get("dominio"):
        items = [l.strip()[2:].strip() for l in secs["dominio"].splitlines() if l.strip().startswith("- ")]
        boxes = "".join(
            f'<li><label><input type="checkbox" data-check="{i}"><span>{t}</span></label></li>'
            for i, t in enumerate(items))
        parts.append(f'<section class="dominio"><h2>Antes de seguir, você domina?</h2>'
                     f'<p class="hint">Marque só o que conseguiria explicar sem olhar. Fica salvo neste navegador.</p><ul>{boxes}</ul></section>')
    parts.append('<section class="notes"><h2>Suas anotações</h2>'
                 '<textarea id="note" rows="4" placeholder="Dúvidas, macetes, o que errou ao revisar… (salvo neste navegador)"></textarea></section>')
    parts.append(f'<button class="done-btn" type="button" data-id="{meta["id"]}">Marcar lição como concluída</button>')
    pager = ['<nav class="pager">']
    if prev:
        pager.append(f'<a href="{prev["id"]}.html" class="prev"><small>Anterior</small>{prev["code"]} {prev["title"]}</a>')
    else:
        pager.append('<span></span>')
    if nxt:
        pager.append(f'<a href="{nxt["id"]}.html" class="next"><small>Próxima</small>{nxt["code"]} {nxt["title"]}</a>')
    else:
        pager.append('<a href="../plano.html" class="next"><small>Fim da trilha</small>Rever o cronograma</a>')
    pager.append('</nav>')
    parts.append("".join(pager))
    parts.append('</article>')
    return "\n".join(parts)


def render_index(lessons):
    total_min = sum(int(l["min"]) for l in lessons)
    chave = [("28", "cUF"), ("2609", "AAMM"), ("12345678000195", "CNPJ"), ("55", "mod"), ("001", "série"),
             ("000004521", "nNF"), ("1", "tpEmis"), ("83749261", "cNF"), ("7", "cDV")]
    segs = "".join(f'<span class="seg"><b>{v}</b><i>{k}</i></span>' for v, k in chave)
    mods = []
    for num, title, resumo in MODULES:
        ls = [l for l in lessons if l["mod"] == num]
        rows = "".join(
            f'<li><a href="licoes/{l["id"]}.html" data-id="{l["id"]}"><span class="code">{l["code"]}</span>'
            f'<span class="t">{l["title"]}</span><span class="min">{l["min"]} min</span></a></li>' for l in ls)
        mods.append(f'<section class="mod"><h2><span class="mnum">{num}</span>{html.escape(title)}</h2>'
                    f'<p class="mres">{resumo}</p><ol class="lessons">{rows}</ol></section>')
    first = lessons[0]
    body = f"""
<section class="hero">
  <p class="kicker">Trilha de estudo em {len(lessons)} lições curtas</p>
  <h1>Entenda os arquivos. Depois, domine as regras.</h1>
  <div class="chave" aria-label="Exemplo de chave de acesso decomposta">{segs}</div>
  <p class="chave-cap">Chave de acesso fictícia de uma NF-e de Sergipe, decomposta nos nove campos. Ela é o fio condutor: liga o XML autorizado à linha da EFD que o escritura.</p>
</section>
<section class="progress-box">
  <div class="pbar"><div class="pfill" id="pfill"></div></div>
  <p id="ptext">Carregando progresso…</p>
  <a class="continue" id="continue" href="licoes/{first["id"]}.html">Começar pela lição {first["code"]}</a>
</section>
<section class="howto">
  <h2>Como usar</h2>
  <p>A trilha começa mostrando o <strong>arquivo de verdade</strong> (o XML da NF-e, o texto da EFD) e só depois entra nas normas, na ordem em que o documento vive: emissão, autorização, circulação, correção, escrituração. Cada lição tem um caso resolvido, as armadilhas de redação, o jeito como as bancas costumam cobrar o tema e a base normativa para você conferir no texto original. Leva cerca de {total_min // 60} horas no total. O <a href="plano.html">cronograma</a> distribui tudo em cinco semanas, com revisão aos sábados, e o <a href="bancas.html">guia de bancas</a> mostra como o mesmo conteúdo aparece em estilos de prova diferentes.</p>
</section>
<section class="backup">
  <h2>Seus dados ficam neste navegador</h2>
  <p>Progresso, anotações e marcações são salvos localmente, sem conta e sem servidor. Se for trocar de aparelho ou limpar os dados do navegador, exporte uma cópia antes.</p>
  <div class="btns"><button type="button" id="exp">Exportar cópia (.json)</button><label class="filebtn">Importar cópia<input type="file" id="imp" accept="application/json"></label><button type="button" id="rst" class="danger">Apagar tudo</button></div>
  <p class="hint" id="bmsg" role="status"></p>
</section>
{''.join(mods)}
"""
    return page("Auditoria Fiscal — NF-e, EFD e CT-e", body, 0, "home")


def render_plano(by_id):
    weeks = []
    for i, w in enumerate(WEEKS, 1):
        rows = ""
        for day, lid in zip(DAYS, w):
            l = by_id[lid]
            rows += (f'<tr><td>{day}</td><td><a href="licoes/{lid}.html" data-id="{lid}">{l["code"]} {l["title"]}</a></td>'
                     f'<td>{l["min"]} min</td></tr>')
        codes = f'{by_id[w[0]]["code"]} a {by_id[w[-1]]["code"]}'
        if i == len(WEEKS):
            rev = ("Revisão geral: sem consultar, reconstrua o ciclo de vida da NF-e (da emissão à guarda) e o calendário da EFD "
                   "(envio, retificação, recibo). Depois releia as armadilhas de todas as lições.")
        else:
            rev = (f"Revisão ativa das lições {codes}: feche o material e escreva, de memória, o quadro-resumo de cada uma. "
                   "Só então confira. Refaça os casos resolvidos trocando os números ou o agente da história.")
        rows += f'<tr class="rev"><td>Sábado</td><td colspan="2">{rev}</td></tr>'
        weeks.append(f'<section class="week"><h2>Semana {i}</h2><div class="tbl"><table>{rows}</table></div></section>')
    body = f"""
<h1 class="ph">Cronograma</h1>
<p class="lead">{len(by_id)} lições em 5 semanas, uma por dia útil. Aos sábados, revisão ativa: escrever de memória antes de reler. Se atrasar, não pule a revisão: empurre a semana inteira.</p>
{''.join(weeks)}
<section class="howto"><h2>Revisão espaçada</h2><p>Além do sábado, volte ao quadro-resumo de cada módulo cerca de uma semana e um mês depois de concluí-lo. O que você não conseguir reconstruir sem olhar merece releitura do trecho do normativo, não só da lição. A lista de verificação no fim de cada lição serve de guia: desmarque o que não se sustentar.</p></section>
"""
    return page("Cronograma — Auditoria Fiscal", body, 0)


def render_simple(name, title):
    body = (SRC / "pages" / f"{name}.html").read_text(encoding="utf-8")
    return page(title, body, 0)


# ---------------------------------------------------------------- main
def main():
    lessons, secs_by_id = [], {}
    for path in sorted((SRC / "lessons").glob("m*-l*.txt")):
        meta, secs = parse_lesson(path)
        lessons.append(meta)
        secs_by_id[meta["id"]] = secs
    lessons.sort(key=lambda m: (m["mod"], m["n"]))
    by_id = {m["id"]: m for m in lessons}

    planned = [x for w in WEEKS for x in w]
    assert planned == [m["id"] for m in lessons], f"cronograma e lições divergem:\n{planned}\n{[m['id'] for m in lessons]}"

    out = ROOT / "licoes"
    out.mkdir(exist_ok=True)
    for old in out.glob("*.html"):
        old.unlink()
    for i, m in enumerate(lessons):
        prev = lessons[i - 1] if i else None
        nxt = lessons[i + 1] if i + 1 < len(lessons) else None
        body = render_lesson(m, secs_by_id[m["id"]], prev, nxt)
        (out / f'{m["id"]}.html').write_text(page(f'{m["code"]} {html.unescape(re.sub("<[^>]+>", "", m["title"]))}', body, 1), encoding="utf-8")

    (ROOT / "index.html").write_text(render_index(lessons), encoding="utf-8")
    (ROOT / "plano.html").write_text(render_plano(by_id), encoding="utf-8")
    (ROOT / "fontes.html").write_text(render_simple("fontes", "Fontes — Auditoria Fiscal"), encoding="utf-8")
    (ROOT / "bancas.html").write_text(render_simple("bancas", "Guia de bancas — Auditoria Fiscal"), encoding="utf-8")

    data = [{"id": m["id"], "code": m["code"], "title": re.sub("<[^>]+>", "", m["title"])} for m in lessons]
    (ROOT / "assets" / "lessons.js").write_text("window.LESSONS=" + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"{len(lessons)} lições geradas")


if __name__ == "__main__":
    main()
