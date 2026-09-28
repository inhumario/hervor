#!/usr/bin/env python3
"""Filtra datos/busquedas/*.json → datos/candidatos.json (≥4,3★ y ≥100 reseñas, sin duplicados)."""
import json, re
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent

def num_resenas(s):
    s = s.strip('()').replace('\xa0', ' ').replace('.', '')
    m = re.match(r'([\d,]+)\s*mil', s)
    if m: return int(float(m.group(1).replace(',', '.')) * 1000)
    m = re.search(r'\d+', s)
    return int(m.group()) if m else 0

def estrellas(s):
    m = re.match(r'(\d,\d)', s)
    return float(m.group(1).replace(',', '.')) if m else 0

salida = {}
for f in sorted((RAIZ / 'datos/busquedas').glob('*.json')):
    d = json.loads(f.read_text()); vistos = set(); lista = []
    for r in d['resultados']:
        if r['asin'] in vistos: continue
        vistos.add(r['asin'])
        e, n = estrellas(r['estrellas']), num_resenas(r['resenas'])
        if e >= 4.3 and n >= 100:
            lista.append({'asin': r['asin'], 'titulo': r['titulo'][:140], 'precio': r['precio'].replace('\xa0', ' '), 'estrellas': e, 'resenas': n})
    salida[d['consulta']] = lista[:14]
(RAIZ / 'datos/candidatos.json').write_text(json.dumps(salida, ensure_ascii=False, indent=1))
for q, l in salida.items(): print(f'{q}: {len(l)}')
