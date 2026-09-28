# Hervor — web de afiliados de Amazon (café y té en casa)

Proyecto propio de Mario (desde 2026-09-28). Web estática **https://hervor.inhumario.com** con marca propia «Hervor»: comparativas y guías de cafeteras, molinillos, hervidores, teteras y accesorios con enlaces de afiliado a Amazon.es. Cuando haya tracción, dominio propio (cambiar `url` en `config.json`).

## Empieza siempre por
1. `README.md` — comandos, formato de artículos y **reglas de contenido** (cumplimiento del Programa de Afiliados de Amazon: nada de precios exactos, estrellas ni imágenes de Amazon; nada de «lo he probado»).
2. `ESTADO.md` — qué está hecho, qué falta y qué depende de Mario.
3. Memoria: `~/Claude/Memoria/hervor/MEMORY.md`.

## Reglas fijas
- Marca separada de Aromas de Té y de Inhumario: no mencionar ni enlazar Aromas; Inhumario solo pone el subdominio.
- Titular legal: Mario Cuadrado López (autónomo, NIF en aviso legal), no Aromas de Té S.L.
- Publicar = `python3 scripts/deploy_easypanel.py deploy "mensaje"` (push a GitHub inhumario/hervor + redeploy EasyPanel travelia/hervor).
- Datos de producto siempre de `datos/fichas/` (scripts/amazon_ficha.py), nunca de memoria.
