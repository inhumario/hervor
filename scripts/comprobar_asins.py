#!/usr/bin/env python3
"""Revisa que todos los productos enlazados en los artículos sigan vivos en amazon.es.

Refresca la ficha de cada ASIN (navegador del VPS) y avisa de los que ya no están disponibles,
han cambiado de producto o han bajado de 4,0★. Con --email manda el aviso a Mario solo si hay problemas.

Uso: python3 scripts/comprobar_asins.py [--email]
"""
import json, re, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'scripts')); sys.path.insert(0, str(Path.home() / '.config/aromas'))
from amazon_ficha import main as descargar, SALIDA

usos = {}
for f in sorted((RAIZ / 'content/articulos').glob('*.md')):
    for asin in set(re.findall(r'(?::::producto\s+|amazon:)([A-Z0-9]{10})', f.read_text())):
        usos.setdefault(asin, []).append(f.stem)

descargar(sorted(usos), forzar=True)
problemas = []
for asin, arts in sorted(usos.items()):
    p = SALIDA / f'{asin}.json'
    if not p.exists():
        problemas.append(f'{asin}: no se pudo leer la ficha ({", ".join(arts)})'); continue
    d = json.loads(p.read_text())
    disp = d.get('disponibilidad', '').lower()
    m = re.match(r'(\d,\d)', d.get('estrellas', ''))
    est = float(m.group(1).replace(',', '.')) if m else None
    if not d.get('titulo'):
        problemas.append(f'{asin}: la página ya no muestra producto ({", ".join(arts)})')
    elif 'no disponible' in disp or 'no está disponible' in disp:
        problemas.append(f'{asin}: NO DISPONIBLE — {d["titulo"][:60]} ({", ".join(arts)})')
    elif est is not None and est < 4.0:
        problemas.append(f'{asin}: ha bajado a {est}★ — {d["titulo"][:60]} ({", ".join(arts)})')

print(f'{len(usos)} productos revisados, {len(problemas)} con problemas')
for x in problemas: print(' -', x)
if problemas and '--email' in sys.argv:
    from gmail_smtp import send
    send('cuadrado.mario@aromasdete.com', f'Punto de Infusión: {len(problemas)} productos a revisar',
         'Productos de Punto de Infusión que hay que sustituir o revisar:\n\n' + '\n'.join(problemas) +
         '\n\nProyecto: ~/Claude/Code/hervor (scripts/comprobar_asins.py)')
