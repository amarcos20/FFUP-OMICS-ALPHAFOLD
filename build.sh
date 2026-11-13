#!/usr/bin/env bash
# Gera build/relatorio.pdf a partir de relatorio.ipynb
#   ./build.sh            -> só converte (usa figuras já existentes em figures/)
#   ./build.sh --execute  -> executa primeiro as células de código (regenera figuras)
set -euo pipefail
cd "$(dirname "$0")"
ENV_BIN="${OMICAS_ENV:-$HOME/miniconda3/envs/omicas}/bin"
export PATH="$ENV_BIN:$PATH"

EXTRA=()
[[ "${1:-}" == "--execute" ]] && EXTRA+=(--execute --ExecutePreprocessor.timeout=600)

jupyter nbconvert relatorio.ipynb --to latex \
  --TemplateExporter.extra_template_basedirs=templates \
  --template relatorio \
  --TemplateExporter.exclude_code_cell=True \
  --output-dir build "${EXTRA[@]}"

tectonic --keep-logs build/relatorio.tex 2>&1 | grep -v "accessing absolute path\|^note:" || true
PAGES=$(pdfinfo build/relatorio.pdf 2>/dev/null | awk '/^Pages/{print $2}')
echo "PDF: build/relatorio.pdf (${PAGES:-?} páginas, incluindo capa e referências; limite: 10)"
