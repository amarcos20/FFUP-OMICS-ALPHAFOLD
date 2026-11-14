"""Gera um site estático (GitHub Pages) a partir das fontes do deck em apresentacao/slides_fonte/.

Uso:  python apresentacao/build_site.py  [pasta_destino]   (por omissão: docs/, servida pelo GitHub Pages)

O resultado é um index.html autónomo + assets/ (imagens). Navegação: ← → / espaço / clique,
F = ecrã inteiro, N = notas do orador, #n no URL abre o diapositivo n.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FONTE = AQUI / "slides_fonte"
ASSETS = AQUI / "assets"

# ids dos assets carregados no artifact -> ficheiros locais
BLOBS = {
    "1beb68a2ec31db3fa177552b56d045b8": "fcup.png",
    "41ca46d5fd46bb0c02d16c6adfbed002": "ffup.png",
    "ed5a2db8b38cd943d607e14285522a51": "plddt.png",
    "cfe973d2f9ed82eca7e82a724caba6c6": "pae.png",
    "04773cf3143021ff1b6ba6b8c73690c9": "workflow.png",
}

SETA = ('<svg class="arrow-svg" width="72" height="36" viewBox="0 0 72 36" aria-hidden="true">'
        '<path d="M0 11h43V0l29 18-29 18V25H0z" fill="#6b2c8a"/></svg>')

# Valores por omissão do formato Slides que o browser não aplica sozinho
RESET = """
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: #0f0c1d; overflow: hidden; }
#palco { position: fixed; left: 50%; top: 50%; width: 1920px; height: 1080px; transform-origin: 0 0; }
#palco > section { position: absolute; inset: 0; width: 1920px; height: 1080px; overflow: hidden;
                   visibility: hidden; }
#palco > section.ativo { visibility: visible; }
#palco section * { margin: 0; }
#palco section aside { display: none; }
#palco section ul { margin: 0; }
#palco section img { display: block; }
#palco section table { border-collapse: collapse; }
#palco section th { text-align: left; font-weight: 600; border-bottom: 2px solid #b9b0c8; }
#palco section td { border-bottom: 1px solid #ddd6e6; }
#palco section th, #palco section td { padding: 0.35em 0.6em; vertical-align: top; }
/* animações só no diapositivo ativo (repetem ao voltar) */
#palco section .anim { animation: none; }
#palco section.ativo .anim { animation: sobe 500ms ease-out both; animation-delay: calc(var(--i, 0) * 120ms); }
#notas { position: fixed; left: 0; right: 0; bottom: 0; max-height: 40vh; overflow: auto; display: none;
         background: rgba(15, 12, 29, .94); color: #f4f1f8; font: 18px/1.5 'IBM Plex Sans', Arial, sans-serif;
         padding: 16px 24px; }
#notas.on { display: block; }
#ajuda { position: fixed; right: 12px; bottom: 10px; color: #8d86a3; font: 13px Arial, sans-serif; }
@media print { #ajuda, #notas { display: none !important; } }
"""

JS = """
const sl = [...document.querySelectorAll('#palco > section')];
const palco = document.getElementById('palco'), notas = document.getElementById('notas');
let i = 0;
function ajusta() {
  const s = Math.min(innerWidth / 1920, innerHeight / 1080);
  palco.style.transform = `scale(${s}) translate(-50%, -50%)`;
}
function mostra(n) {
  i = Math.max(0, Math.min(sl.length - 1, n));
  sl.forEach((s, k) => s.classList.toggle('ativo', k === i));
  const a = sl[i].querySelector('aside');
  notas.textContent = a ? a.textContent : '';
  history.replaceState(null, '', '#' + (i + 1));
}
addEventListener('resize', ajusta);
addEventListener('keydown', e => {
  if (['ArrowRight', 'PageDown', ' ', 'Enter'].includes(e.key)) { mostra(i + 1); e.preventDefault(); }
  else if (['ArrowLeft', 'PageUp', 'Backspace'].includes(e.key)) { mostra(i - 1); e.preventDefault(); }
  else if (e.key === 'Home') mostra(0);
  else if (e.key === 'End') mostra(sl.length - 1);
  else if (e.key === 'f' || e.key === 'F') { document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); }
  else if (e.key === 'n' || e.key === 'N') notas.classList.toggle('on');
});
addEventListener('click', e => { if (!notas.contains(e.target)) mostra(e.clientX > innerWidth / 3 ? i + 1 : i - 1); });
let x0 = null;
addEventListener('touchstart', e => { x0 = e.touches[0].clientX; });
addEventListener('touchend', e => { if (x0 === null) return; const d = e.changedTouches[0].clientX - x0; if (Math.abs(d) > 40) mostra(i + (d < 0 ? 1 : -1)); x0 = null; });
ajusta();
mostra((parseInt(location.hash.slice(1)) || 1) - 1);
"""


def main(destino: Path) -> None:
    deck = json.loads((FONTE / "deck.json").read_text())
    css = (FONTE / "deck.css").read_text()
    slides = []
    for sid in deck["order"]:
        s = (FONTE / "slides" / f"{sid}.html").read_text()
        for blob, nome in BLOBS.items():
            s = s.replace(f"/_blob/{blob}", f"assets/{nome}")
        s = re.sub(r'<x-shape kind="arrow-right" class="arrow"></x-shape>', SETA, s)
        if "/_blob/" in s or "<x-" in s:
            raise SystemExit(f"Diapositivo {sid}: elemento sem conversão (/_blob ou x-*). Atualizar BLOBS/conversões.")
        slides.append(s.strip())

    fontes = "\n".join(f'<link rel="stylesheet" href="{html.escape(f["href"])}">' for f in deck["faces"].values())
    titulo = html.escape(deck["title"])
    pagina = f"""<!doctype html>
<html lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="Apresentação do trabalho da UC Ómicas sobre o AlphaFold (versões 2 e 3).">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fontes}
<style>
{css}
{RESET}
</style>
</head>
<body>
<div id="palco">
{chr(10).join(slides)}
</div>
<div id="notas" aria-live="polite"></div>
<div id="ajuda">← → navegar · F ecrã inteiro · N notas</div>
<script>{JS}</script>
</body>
</html>
"""
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "index.html").write_text(pagina)
    (destino / "assets").mkdir(exist_ok=True)
    for nome in BLOBS.values():
        shutil.copy2(ASSETS / nome, destino / "assets" / nome)
    (destino / ".nojekyll").write_text("")
    print(f"OK: {len(slides)} diapositivos -> {destino / 'index.html'}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI.parent / "docs")
