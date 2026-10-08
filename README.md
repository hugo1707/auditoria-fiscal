# Auditoria Fiscal — NF-e, EFD e CT-e

Trilha de estudo em 25 lições curtas, organizada para quem vai fazer concursos de auditoria fiscal (várias bancas).
Começa pelos arquivos de verdade (XML da NF-e, texto da EFD) e só depois entra nas normas:
Ajustes SINIEF 07/05 (NF-e e DANFE), 02/09 (EFD) e 09/07 (CT-e), MDF-e e cruzamentos de auditoria.

Cada lição tem: caso resolvido, onde o texto engana, como as bancas costumam cobrar, base normativa,
lista de domínio e campo de anotações. Não há questões de concursos nem simulado no material.

## Dados do estudante
Progresso, anotações e marcações ficam no `localStorage` do navegador (sem conta, sem servidor).
Na página inicial há botões para exportar, importar e apagar uma cópia (.json).

## Editar o conteúdo
O site é gerado. Não edite os `.html` de `licoes/`, `index.html`, `plano.html`, `fontes.html` ou `bancas.html`.

- Lições: `src/lessons/mX-lY.txt` (cabeçalho + seções `=== nome`; blocos de código com `~~~xml` ... `~~~`, destaque com `[[ ]]`)
- Páginas avulsas: `src/pages/*.html`
- Módulos e cronograma: constantes `MODULES` e `WEEKS` em `tools/build.py`

Depois de editar, rode:

```
python tools/build.py
```

## Publicar no GitHub Pages
1. Envie o conteúdo desta pasta para um repositório (index.html na raiz).
2. Em Settings > Pages, escolha "Deploy from a branch", branch `main`, pasta `/ (root)`.
3. Abra `https://SEU-USUARIO.github.io/NOME-DO-REPO/` no celular.
