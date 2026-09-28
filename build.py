#!/usr/bin/env python3
"""Genera la web estática de Hervor en dist/.

    python3 build.py            # construye dist/
    python3 build.py --serve    # construye y sirve en http://localhost:8088

Contenido en content/articulos/*.md (frontmatter YAML + markdown) y content/paginas/*.md.
Formato de los artículos en README.md. La etiqueta de afiliado sale de config.json
(`amazon_tag`); si está vacía, los enlaces van a Amazon sin etiqueta.
"""
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import markdown
import yaml

RAIZ = Path(__file__).resolve().parent
DIST = RAIZ / 'dist'
CFG = json.loads((RAIZ / 'config.json').read_text())
URL = CFG['url'].rstrip('/')
TAG = CFG.get('amazon_tag', '').strip()
CATEGORIAS = CFG['categorias']
AVISO_AFILIADO = ('Como Afiliado de Amazon, obtengo ingresos por las compras adscritas '
                  'que cumplen los requisitos aplicables.')


# ─── utilidades ────────────────────────────────────────────────────────────────

def esc(s):
    return html.escape(str(s or ''), quote=True)


def enlace_amazon(asin):
    return f'https://www.amazon.es/dp/{asin}' + (f'?tag={TAG}' if TAG else '')


def fecha_es(d):
    meses = 'enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre'.split()
    d = d if isinstance(d, date) else date.fromisoformat(str(d))
    return f'{d.day} de {meses[d.month - 1]} de {d.year}'


def leer_md(ruta):
    texto = ruta.read_text(encoding='utf-8')
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', texto, re.S)
    if not m:
        raise SystemExit(f'{ruta}: falta el frontmatter')
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        raise SystemExit(f'{ruta}: frontmatter YAML inválido (¿dos puntos sin comillas?): {e}')
    meta.setdefault('slug', ruta.stem)
    return meta, m.group(2)


def md(texto):
    return markdown.markdown(texto, extensions=['tables', 'sane_lists', 'attr_list', 'toc'],
                             extension_configs={'toc': {'permalink': False}})


# ─── bloques de producto ───────────────────────────────────────────────────────

BLOQUE = re.compile(r'^:::producto\s+([A-Z0-9]{10})\s*\n(.*?)^:::\s*$', re.M | re.S)


def texto_item(x):
    """Un pro/contra con «: » dentro lo parsea YAML como diccionario: se recompone."""
    if isinstance(x, dict):
        return '; '.join(f'{k}: {v}' for k, v in x.items())
    return str(x)


def tarjeta(asin, p, n):
    pros = ''.join(f'<li>{esc(texto_item(x))}</li>' for x in p.get('pros', []))
    contras = ''.join(f'<li>{esc(texto_item(x))}</li>' for x in p.get('contras', []))
    etiqueta = f'<span class="badge">{esc(p["etiqueta"])}</span>' if p.get('etiqueta') else ''
    valor = f'<p class="valoracion">★ {esc(p["valoracion"])} en Amazon</p>' if p.get('valoracion') else ''
    para = f'<p class="para"><strong>Para quién:</strong> {esc(p["para"])}</p>' if p.get('para') else ''
    return f'''
<section class="producto" id="p-{asin}">
  <div class="producto-cab">
    <span class="num">{n}</span>
    <div>{etiqueta}<h3>{esc(p["nombre"])}</h3>{valor}</div>
  </div>
  {para}
  <div class="proscontras">
    <div class="pros"><h4>A favor</h4><ul>{pros}</ul></div>
    <div class="contras"><h4>En contra</h4><ul>{contras}</ul></div>
  </div>
  <a class="btn" href="{enlace_amazon(asin)}" rel="sponsored nofollow noopener" target="_blank">Ver precio en Amazon</a>
</section>'''


def procesar_cuerpo(cuerpo):
    """Sustituye bloques :::producto, :::tabla-resumen y enlaces amazon:ASIN."""
    productos = []

    def sub(m):
        asin, datos = m.group(1), yaml.safe_load(m.group(2)) or {}
        productos.append((asin, datos))
        return f'\n<!--PRODUCTO{len(productos) - 1}-->\n'

    cuerpo = BLOQUE.sub(sub, cuerpo)
    cuerpo = re.sub(r'\]\(amazon:([A-Z0-9]{10})\)', lambda m: f']({enlace_amazon(m.group(1))}){{: rel="sponsored nofollow noopener" target="_blank"}}', cuerpo)
    cuerpo = cuerpo.replace(':::tabla-resumen', '<!--TABLA-->')
    h = md(cuerpo)
    for i, (asin, p) in enumerate(productos):
        h = h.replace(f'<!--PRODUCTO{i}-->', tarjeta(asin, p, i + 1))
    if productos:
        filas = ''.join(
            f'<tr><td>{i + 1}</td><td><a href="#p-{a}">{esc(p["nombre"])}</a></td>'
            f'<td>{esc(p.get("etiqueta", ""))}</td>'
            f'<td><a class="btn btn-sm" href="{enlace_amazon(a)}" rel="sponsored nofollow noopener" target="_blank">Ver en Amazon</a></td></tr>'
            for i, (a, p) in enumerate(productos))
        tabla = (f'<div class="tabla-wrap"><table class="resumen"><thead><tr><th>#</th><th>Producto</th>'
                 f'<th>Destaca por</th><th></th></tr></thead><tbody>{filas}</tbody></table></div>')
        h = h.replace('<p><!--TABLA--></p>', tabla).replace('<!--TABLA-->', tabla)
    return h, productos


# ─── plantilla ─────────────────────────────────────────────────────────────────

def pagina(titulo, descripcion, ruta, contenido, schema=None, tipo_og='website', indexar=True):
    canon = URL + ruta
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'
                 for s in (schema or []))
    nav = ''.join(f'<a href="/{c["slug"]}/">{esc(c["nombre"])}</a>' for c in CATEGORIAS)
    robots = '' if indexar else '<meta name="robots" content="noindex">'
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(descripcion)}">
<link rel="canonical" href="{canon}">
{robots}
<meta property="og:type" content="{tipo_og}">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descripcion)}">
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="Hervor">
<meta property="og:locale" content="es_ES">
<meta property="og:image" content="{URL}/static/og.png">
<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="Hervor" href="/feed.xml">
<link rel="preload" href="/static/fuentes/inter-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/static/estilo.css?v={CFG.get('version', '1')}">
{ld}
</head>
<body>
<header class="cab">
  <div class="contenedor cab-in">
    <a class="logo" href="/"><img src="/static/favicon.svg" alt="" width="28" height="28">Hervor</a>
    <input type="checkbox" id="menu" hidden><label for="menu" class="menu-btn" aria-label="Menú">☰</label>
    <nav>{nav}<a href="/sobre-hervor/">Quiénes somos</a></nav>
  </div>
</header>
<main>
{contenido}
</main>
<footer class="pie">
  <div class="contenedor">
    <p class="pie-marca"><strong>Hervor</strong> · Café y té en casa, bien hechos.</p>
    <p class="pie-aviso">{AVISO_AFILIADO} Los precios y la disponibilidad cambian; el precio válido es el que marca Amazon al comprar.</p>
    <p class="pie-links"><a href="/sobre-hervor/">Quiénes somos</a><a href="/como-elegimos/">Cómo elegimos</a><a href="/afiliacion/">Afiliación</a><a href="/aviso-legal/">Aviso legal</a><a href="/privacidad/">Privacidad</a><a href="/cookies/">Cookies</a></p>
  </div>
</footer>
</body>
</html>'''


def escribir(ruta, contenido):
    destino = DIST / ruta.strip('/') / 'index.html' if not ruta.endswith('.html') else DIST / ruta.strip('/')
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(contenido, encoding='utf-8')


def tarjeta_articulo(a):
    cat = next(c for c in CATEGORIAS if c['slug'] == a['categoria'])
    return f'''<a class="tarjeta" href="/{a["slug"]}/">
  <span class="tarjeta-cat">{esc(cat["nombre"])}</span>
  <h3>{esc(a["titulo"])}</h3>
  <p>{esc(a["resumen"])}</p>
  <span class="tarjeta-mas">Leer →</span>
</a>'''


# ─── build ─────────────────────────────────────────────────────────────────────

def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(RAIZ / 'static', DIST / 'static')
    for clave in (RAIZ / 'static').glob('*.txt'):  # clave de IndexNow: tiene que ir en la raíz
        shutil.copy(clave, DIST / clave.name)

    articulos = []
    for f in sorted((RAIZ / 'content/articulos').glob('*.md')):
        meta, cuerpo = leer_md(f)
        if meta.get('borrador'):
            continue
        meta['html'], meta['productos'] = procesar_cuerpo(cuerpo)
        meta.setdefault('actualizado', meta['fecha'])
        articulos.append(meta)
    articulos.sort(key=lambda a: (str(a['actualizado']), a['titulo']), reverse=True)
    autor = CFG['autor']
    persona = {'@type': 'Person', 'name': autor['nombre'], 'url': URL + '/sobre-hervor/'}
    organizacion = {'@type': 'Organization', 'name': 'Hervor', 'url': URL + '/',
                    'logo': URL + '/static/favicon.svg'}

    for a in articulos:
        ruta = f'/{a["slug"]}/'
        cat = next(c for c in CATEGORIAS if c['slug'] == a['categoria'])
        faq = a.get('faq') or []
        faq_html = ''
        if faq:
            faq_html = '<section class="faq"><h2 id="preguntas-frecuentes">Preguntas frecuentes</h2>' + ''.join(
                f'<details><summary>{esc(q["p"])}</summary>{md(q["r"])}</details>' for q in faq) + '</section>'
        relacionados = [r for r in articulos if r['slug'] != a['slug'] and r['categoria'] == a['categoria']][:3]
        if len(relacionados) < 3:
            relacionados += [r for r in articulos if r['slug'] != a['slug'] and r not in relacionados][:3 - len(relacionados)]
        aviso = (f'<p class="aviso-art">Este artículo contiene enlaces de afiliado: si compras a través de ellos, '
                 f'Hervor puede llevarse una pequeña comisión sin que tú pagues más. '
                 f'<a href="/afiliacion/">Cómo funciona</a>.</p>') if a['productos'] else ''
        contenido = f'''
<article class="contenedor articulo">
  <nav class="migas"><a href="/">Inicio</a> › <a href="/{cat["slug"]}/">{esc(cat["nombre"])}</a></nav>
  <h1>{esc(a["titulo"])}</h1>
  <p class="entradilla">{esc(a["descripcion"])}</p>
  <p class="meta">Por <a href="/sobre-hervor/">{esc(autor["nombre"])}</a> · Actualizado el {fecha_es(a["actualizado"])}</p>
  {aviso}
  <div class="cuerpo">{a["html"]}</div>
  {faq_html}
  <aside class="autor">
    <strong>{esc(autor["nombre"])}</strong>
    <p>{esc(autor["bio_corta"])}</p>
  </aside>
</article>
<section class="contenedor relacionados"><h2>Sigue leyendo</h2><div class="rejilla">{''.join(tarjeta_articulo(r) for r in relacionados)}</div></section>'''
        schema = [{
            '@context': 'https://schema.org', '@type': 'Article', 'headline': a['titulo'],
            'description': a['descripcion'], 'datePublished': str(a['fecha']),
            'dateModified': str(a['actualizado']), 'author': persona, 'publisher': organizacion,
            'mainEntityOfPage': URL + ruta, 'inLanguage': 'es-ES'},
            {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': URL + '/'},
                {'@type': 'ListItem', 'position': 2, 'name': cat['nombre'], 'item': f'{URL}/{cat["slug"]}/'},
                {'@type': 'ListItem', 'position': 3, 'name': a['titulo'], 'item': URL + ruta}]}]
        if faq:
            schema.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
                {'@type': 'Question', 'name': q['p'], 'acceptedAnswer': {'@type': 'Answer', 'text': q['r']}}
                for q in faq]})
        escribir(ruta, pagina(a.get('titulo_seo', a['titulo']), a['descripcion'], ruta, contenido, schema, 'article'))

    # categorías
    for c in CATEGORIAS:
        lista = [a for a in articulos if a['categoria'] == c['slug']]
        contenido = f'''<section class="contenedor portada-cat"><h1>{esc(c["nombre"])}</h1><p class="entradilla">{esc(c["descripcion"])}</p>
<div class="rejilla">{''.join(tarjeta_articulo(a) for a in lista)}</div></section>'''
        escribir(f'/{c["slug"]}/', pagina(f'{c["nombre"]} — Hervor', c['descripcion'], f'/{c["slug"]}/', contenido))

    # portada
    bloques = ''.join(
        f'<section class="contenedor"><h2 class="sec">{esc(c["nombre"])}</h2><div class="rejilla">'
        + ''.join(tarjeta_articulo(a) for a in [x for x in articulos if x['categoria'] == c['slug']][:6])
        + f'</div><p class="ver-todo"><a href="/{c["slug"]}/">Todo sobre {esc(c["nombre"].lower())} →</a></p></section>'
        for c in CATEGORIAS if any(x['categoria'] == c['slug'] for x in articulos))
    portada = f'''
<section class="hero"><div class="contenedor">
  <p class="hero-kicker">Café y té en casa</p>
  <h1>Lo que de verdad importa para hacer buen café y buen té</h1>
  <p>Guías claras y comparativas honestas de cafeteras, molinillos, hervidores y teteras. Sin tecnicismos de más, sin relleno y diciendo también lo que no nos gusta.</p>
  <a class="btn" href="/como-elegimos/">Cómo elegimos los productos</a>
</div></section>
{bloques}'''
    escribir('/', pagina(CFG['titulo'], CFG['descripcion'], '/', portada,
                         [{'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Hervor', 'url': URL + '/',
                           'inLanguage': 'es-ES', 'publisher': organizacion}]))

    # páginas fijas
    for f in sorted((RAIZ / 'content/paginas').glob('*.md')):
        meta, cuerpo = leer_md(f)
        contenido = f'<article class="contenedor articulo"><h1>{esc(meta["titulo"])}</h1><div class="cuerpo">{md(cuerpo)}</div></article>'
        escribir(f'/{meta["slug"]}/', pagina(f'{meta["titulo"]} — Hervor', meta['descripcion'], f'/{meta["slug"]}/',
                                             contenido, indexar=not meta.get('noindex')))

    # 404
    (DIST / '404.html').write_text(pagina('Página no encontrada — Hervor', 'No existe esta página.', '/404.html',
                                          '<section class="contenedor articulo"><h1>Aquí no hay nada</h1><p>La página no existe o ha cambiado de sitio. <a href="/">Volver a la portada</a>.</p></section>',
                                          indexar=False), encoding='utf-8')

    # sitemap, robots, feed
    urls = ['/'] + [f'/{c["slug"]}/' for c in CATEGORIAS] + [f'/{a["slug"]}/' for a in articulos] + \
           [f'/{leer_md(f)[0]["slug"]}/' for f in sorted((RAIZ / 'content/paginas').glob('*.md')) if not leer_md(f)[0].get('noindex')]
    mod = {f'/{a["slug"]}/': a['actualizado'] for a in articulos}
    (DIST / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'<url><loc>{URL}{u}</loc>' + (f'<lastmod>{mod[u]}</lastmod>' if u in mod else '') + '</url>\n' for u in urls) +
        '</urlset>\n', encoding='utf-8')
    (DIST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n', encoding='utf-8')
    items = ''.join(
        f'<item><title>{esc(a["titulo"])}</title><link>{URL}/{a["slug"]}/</link><guid>{URL}/{a["slug"]}/</guid>'
        f'<description>{esc(a["descripcion"])}</description><pubDate>{date.fromisoformat(str(a["fecha"])).strftime("%a, %d %b %Y 08:00:00 +0200")}</pubDate></item>'
        for a in articulos[:20])
    (DIST / 'feed.xml').write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Hervor</title><link>{URL}/</link>'
        f'<description>{esc(CFG["descripcion"])}</description><language>es-es</language>{items}</channel></rss>', encoding='utf-8')

    print(f'dist/: {len(articulos)} artículos, {len(urls)} URLs en el sitemap' + ('' if TAG else '  (SIN etiqueta de afiliado)'))


if __name__ == '__main__':
    main()
    if '--serve' in sys.argv:
        import http.server, functools
        http.server.ThreadingHTTPServer(('0.0.0.0', 8088), functools.partial(
            http.server.SimpleHTTPRequestHandler, directory=str(DIST))).serve_forever()
