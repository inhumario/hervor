# Punto de Infusión (antes «Hervor») — web de afiliados de Amazon (café y té en casa)

Proyecto propio de Mario (28-09-2026). Web estática en **https://puntodeinfusion.inhumario.com**, marca propia «Punto de Infusión» (se llamó «Hervor» unas horas; carpeta, repo y servicio conservan ese nombre); cuando funcione se le compra dominio propio (basta con cambiar `url` en `config.json` y redirigir).

## Cómo se trabaja

```bash
python3 build.py              # genera dist/
python3 build.py --serve      # genera y sirve en :8088
python3 scripts/amazon_buscar.py "consulta"     # resultados de búsqueda → datos/busquedas/
python3 scripts/candidatos.py                   # filtra ≥4,3★ y ≥100 reseñas → datos/candidatos.json
python3 scripts/amazon_ficha.py ASIN [ASIN…]    # ficha del fabricante → datos/fichas/ASIN.json
python3 scripts/comprobar_asins.py              # revisa que los ASIN enlazados sigan vivos y en stock
python3 scripts/deploy_easypanel.py [deploy]    # despliegue (push a GitHub + redeploy)
```

La etiqueta de afiliado va en `config.json` → `amazon_tag` (p. ej. `puntodeinfusion-21`). Mientras esté vacía, los enlaces salen sin etiqueta.

## Formato de un artículo — `content/articulos/<slug>.md`

```markdown
---
titulo: Los mejores molinillos de café manuales
titulo_seo: Mejores molinillos de café manuales (2026)      # opcional, <title>, ≤ 65 caracteres
descripcion: Frase de 140-155 caracteres que sale en Google y como entradilla.
resumen: Una frase corta para la tarjeta de la portada.
categoria: cafe            # cafe | te | accesorios
tipo: comparativa          # comparativa | guia
fecha: 2026-09-28
faq:
  - p: ¿Pregunta real que la gente busca?
    r: Respuesta en 2-4 frases (admite markdown).
---
Introducción (2-3 párrafos cortos que responden rápido a la intención de búsqueda).

:::tabla-resumen

## Cómo hemos elegido
…

## Los X mejores …

:::producto B0C1GH2BBQ
nombre: TIMEMORE Chestnut C3S Pro
etiqueta: El mejor en general
para: Quien hace espresso y filtro y quiere un molinillo para años.
pros:
  - Cuerpo metálico y doble rodamiento…
contras:
  - Precio alto para empezar
:::

Párrafo(s) que desarrollan el producto…

## Guía de compra: qué mirar
…
```

- `:::tabla-resumen` pinta la tabla con todos los productos del artículo (en el orden en que aparecen).
- Enlace de texto a un producto: `[texto](amazon:B0C1GH2BBQ)` (sale con la etiqueta y `rel="sponsored nofollow"`).
- Enlace interno: `[texto](/slug-del-articulo/)`.

## Reglas de contenido (cumplimiento Amazon y honestidad)

1. **Nunca inventar pruebas**: nada de «lo he probado», «en nuestras pruebas», «tras un mes usándolo». La selección se basa en fichas del fabricante, opiniones de compradores y criterio del sector (Mario lleva 25 años en té y café). Se puede hablar con autoridad de *cómo se hace buen café/té* y de *qué características importan*.
2. **Nada de precios exactos, estrellas ni número de reseñas en el texto** (Amazon prohíbe mostrarlos sin su API, porque cambian). Sí rangos orientativos: «menos de 30 €», «gama media (50-100 €)».
3. **Nada de imágenes de Amazon** (hasta tener PA-API).
4. Todos los datos técnicos, sacados de `datos/fichas/ASIN.json`. Si un dato no está en la ficha, no se afirma.
5. Cada producto con contras reales: una comparativa sin contras no se la cree nadie.
6. No mencionar Aromas de Té ni enlazar a sus productos (marcas separadas).
