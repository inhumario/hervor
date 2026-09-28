#!/usr/bin/env python3
"""Avisa a IndexNow (Bing, Yandex…) de todas las URLs del sitemap publicado. Ejecutar tras cada deploy con contenido nuevo."""
import json, re, urllib.request
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
clave = next((RAIZ / 'static').glob('*.txt')).stem
host = 'hervor.inhumario.com'
urls = re.findall(r'<loc>([^<]+)</loc>', urllib.request.urlopen(f'https://{host}/sitemap.xml').read().decode())
req = urllib.request.Request('https://api.indexnow.org/indexnow', method='POST', headers={'Content-Type': 'application/json'},
    data=json.dumps({'host': host, 'key': clave, 'keyLocation': f'https://{host}/{clave}.txt', 'urlList': urls}).encode())
print(len(urls), 'URLs →', urllib.request.urlopen(req).status)
