# AlphaFold 2 e 3 — Trabalho da UC Ómicas (2026/27)

Trabalho de grupo (FCUP/FFUP) sobre o AlphaFold: relatório escrito e apresentação oral.
Grupo: Afonso Marcos, Pedro Afonso, Artur Anselmo.

**Apresentação:** https://amarcos20.github.io/FFUP-OMICS-ALPHAFOLD/
(← → navegar · F ecrã inteiro · N notas do orador)

## Conteúdo

| Caminho | O quê |
|---|---|
| `relatorio.ipynb` | Fonte do relatório (texto + análise) |
| `scripts/analise_af.py` | pLDDT, RMSD/Kabsch, TM-score, geometria do heme |
| `data/af2`, `data/af3` | Resultados do ColabFold e do AlphaFold Server |
| `figures/` | Figuras e tabelas geradas |
| `apresentacao/` | Fontes do deck e `build_site.py` |
| `docs/` | Site da apresentação (GitHub Pages, gerado) |

## Gerar

```bash
conda activate omicas
./build.sh --execute               # relatório -> build/relatorio.pdf
python apresentacao/build_site.py  # apresentação -> docs/
```
