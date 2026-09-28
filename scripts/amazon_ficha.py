#!/usr/bin/env python3
"""Descarga la ficha de uno o varios ASIN de amazon.es (navegador del VPS) → datos/fichas/<ASIN>.json
con título, marca, viñetas del fabricante, tabla técnica, valoración y disponibilidad.
Si la ficha ya existe no la vuelve a pedir (usa --forzar para refrescar).

Uso: python3 scripts/amazon_ficha.py B0C1GH2BBQ B0CMPXHCNC ...
"""
import asyncio, json, sys, time, urllib.request
from pathlib import Path

SALIDA = Path(__file__).resolve().parent.parent / 'datos/fichas'
SALIDA.mkdir(parents=True, exist_ok=True)

JS = r"""
() => {
  const t = s => (document.querySelector(s)?.innerText || '').trim();
  const filas = {};
  document.querySelectorAll('#productDetails_techSpec_section_1 tr, #productDetails_detailBullets_sections1 tr, #productOverview_feature_div tr, table.prodDetTable tr').forEach(tr => {
    const k = tr.querySelector('th, td:first-child'), v = tr.querySelector('td:last-child');
    if (k && v && k !== v) filas[k.innerText.trim()] = v.innerText.trim().replace(/\s+/g, ' ');
  });
  document.querySelectorAll('#detailBullets_feature_div li').forEach(li => {
    const p = li.innerText.split(':'); if (p.length > 1) filas[p[0].replace(/[^\w\sáéíóúñÁÉÍÓÚÑ]/g,'').trim()] = p.slice(1).join(':').trim();
  });
  return {
    titulo: t('#productTitle'),
    marca: t('#bylineInfo'),
    vinetas: [...document.querySelectorAll('#feature-bullets li span.a-list-item')].map(x => x.innerText.trim()).filter(Boolean),
    detalles: filas,
    estrellas: (document.querySelector('#acrPopover')?.getAttribute('title') || ''),
    resenas: t('#acrCustomerReviewText'),
    precio: t('.priceToPay .a-offscreen') || t('#corePrice_feature_div .a-offscreen'),
    disponibilidad: t('#availability'),
  };
}
"""

CDP = 'http://127.0.0.1:9222'


def _http(path, method='GET'):
    req = urllib.request.Request(CDP + path, method=method)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


async def _descargar(asins):
    # CDP directo a una pestaña propia: connect_over_cdp de Playwright enumera todas las pestañas
    # del navegador compartido y se cuelga cuando alguna no responde (pasó el 28-09-2026).
    import websockets
    t = _http('/json/new?about:blank', 'PUT')
    try:
        async with websockets.connect(t['webSocketDebuggerUrl'], max_size=50_000_000, open_timeout=60) as ws:
            n = [0]

            async def cmd(method, params=None):
                n[0] += 1
                await ws.send(json.dumps({'id': n[0], 'method': method, 'params': params or {}}))
                while True:
                    m = json.loads(await asyncio.wait_for(ws.recv(), 90))
                    if m.get('id') == n[0]:
                        return m

            for a in asins:
                try:
                    await cmd('Page.navigate', {'url': f'https://www.amazon.es/dp/{a}'})
                    for _ in range(40):
                        await asyncio.sleep(1)
                        r = await cmd('Runtime.evaluate', {'expression': 'document.readyState + "|" + !!document.querySelector("#productTitle")', 'returnByValue': True})
                        v = r['result']['result'].get('value', '')
                        if v.endswith('true') and not v.startswith('loading'):
                            break
                    await asyncio.sleep(2)
                    r = await cmd('Runtime.evaluate', {'expression': f'({JS})()', 'returnByValue': True})
                    d = r['result']['result']['value']; d['asin'] = a
                    (SALIDA / f'{a}.json').write_text(json.dumps(d, ensure_ascii=False, indent=1))
                    print(f'{a}: {d["titulo"][:70] or "SIN TÍTULO"} | {d["disponibilidad"][:30]}', flush=True)
                except Exception as e:
                    print(f'{a}: ERROR {type(e).__name__}: {str(e)[:80]}', flush=True)
                await asyncio.sleep(1.5)
    finally:
        try:
            _http('/json/close/' + t['id'])
        except Exception:
            pass


def main(asins, forzar=False):
    pendientes = [a for a in asins if forzar or not (SALIDA / f'{a}.json').exists()]
    if not pendientes:
        print('todas en caché'); return
    asyncio.run(_descargar(pendientes))

if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(args, '--forzar' in sys.argv)
