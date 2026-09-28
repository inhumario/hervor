#!/usr/bin/env python3
"""QA de contenido antes de publicar: reglas de Amazon, enlaces internos y ASIN con ficha."""
import re, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
arts = {f.stem: f.read_text() for f in (RAIZ / 'content/articulos').glob('*.md')}
paginas = {'quienes-somos', 'como-elegimos', 'afiliacion', 'aviso-legal', 'privacidad', 'cookies', 'cafe', 'te', 'accesorios', ''}
fallos = 0
for slug, t in sorted(arts.items()):
    cuerpo = t.split('\n---\n', 1)[-1]
    avisos = []
    for pat, msg in [(r'(?<!debajo de )(?<!menos de )(?<!más de )(?<!partir de )(?<!\d-)(?<!\d y )(?<!entre )\b\d+(?:[.,]\d+)?\s?€(?!\s*y)', 'precio exacto (usa rangos: menos de X €)'), (r'\d[\d.,]*\s*(?:estrellas|reseñas|opiniones|valoraciones)', 'cifra de estrellas/reseñas'),
                     (r'(?<!no )\b(?:lo he|los he|la he|hemos) probad', 'prueba fingida'), (r'aromas de t[eé]', 'mención a Aromas'),
                     (r'\bsumérgete\b|en el mundo actual|sin duda alguna', 'muletilla de IA')]:
        for m in re.finditer(pat, t, re.I):
            avisos.append(f'{msg}: «{t[max(0, m.start()-30):m.end()+20].replace(chr(10), " ")}»')
    for l in re.findall(r'\]\(/([a-z0-9-]*)/?(?:#[^)]*)?\)', t):
        if l not in arts and l not in paginas:
            avisos.append(f'enlace interno roto: /{l}/')
    for a in set(re.findall(r'(?::::producto\s+|amazon:)([A-Z0-9]{10})', t)):
        if not (RAIZ / f'datos/fichas/{a}.json').exists():
            avisos.append(f'ASIN sin ficha descargada: {a}')
    n = len(re.findall(r':::producto', t)); w = len(cuerpo.split())
    print(f'{"OK " if not avisos else "!! "}{slug}: {n} productos, {w} palabras')
    for x in avisos: print('    -', x)
    fallos += sum(1 for x in avisos if not x.startswith('ASIN sin ficha'))
sys.exit(1 if fallos else 0)
