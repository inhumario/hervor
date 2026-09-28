#!/usr/bin/env python3
"""Busca en amazon.es desde el navegador del VPS y guarda los resultados orgánicos (ASIN, título,
precio, estrellas, nº de reseñas) en datos/busquedas/<slug>.json.

Uso: python3 scripts/amazon_buscar.py "molinillo cafe manual" ["otra busqueda" ...]
"""
import json, re, sys, time, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path.home() / '.config/aromas'))
from navegador import abrir

SALIDA = Path(__file__).resolve().parent.parent / 'datos/busquedas'
SALIDA.mkdir(parents=True, exist_ok=True)

JS = r"""
() => [...document.querySelectorAll('div[data-component-type="s-search-result"][data-asin]')]
  .filter(d => d.dataset.asin && !d.querySelector('.puis-sponsored-label-text, .s-sponsored-label-text'))
  .map(d => {
    const t = d.querySelector('h2 span, h2 a span, [data-cy="title-recipe"] h2');
    const p = d.querySelector('.a-price .a-offscreen');
    const r = d.querySelector('[aria-label*="de 5 estrellas"], .a-icon-alt');
    const n = d.querySelector('[aria-label$="valoraciones"], a[href*="customerReviews"] span, span.s-underline-text');
    return {asin: d.dataset.asin, titulo: t ? t.innerText.trim() : '',
            precio: p ? p.innerText.trim() : '',
            estrellas: r ? (r.getAttribute('aria-label') || r.innerText).trim() : '',
            resenas: n ? (n.getAttribute('aria-label') || n.innerText).trim() : ''};
  })
"""

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def main(consultas):
    with abrir() as pg:
        for q in consultas:
            pg.goto('https://www.amazon.es/s?k=' + q.replace(' ', '+'), wait_until='domcontentloaded', timeout=60000)
            pg.wait_for_timeout(2500)
            res = pg.evaluate(JS)
            (SALIDA / f'{slug(q)}.json').write_text(json.dumps({'consulta': q, 'resultados': res}, ensure_ascii=False, indent=1))
            print(f'{q}: {len(res)} resultados')
            time.sleep(2)

if __name__ == '__main__':
    main(sys.argv[1:])
