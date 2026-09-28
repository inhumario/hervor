# Hervor — estado (28-09-2026)

## Hecho

- Web estática generada con `build.py` (Python → HTML), diseño propio responsive (paleta verde, Fraunces + Inter autoalojadas, sin cookies ni peticiones a terceros).
- Fichas de producto sin imágenes ni precios (cumplimiento Amazon sin PA-API), tabla resumen automática, FAQ con datos estructurados, migas, Article/Breadcrumb/FAQPage schema, sitemap, robots, RSS, 404.
- Páginas: Quiénes somos, Cómo elegimos, Afiliación (texto obligatorio de Amazon), Aviso legal, Privacidad y Cookies.
- Artículos de lanzamiento en `content/articulos/` (comparativas y guías de café, té y accesorios) con productos reales de amazon.es: ≥4,3★, ≥100 opiniones y ficha descargada.
- Despliegue: GitHub `inhumario/hervor` → EasyPanel `travelia/hervor` → https://hervor.inhumario.com.
- Vigilante semanal de productos (`scripts/comprobar_asins.py --email`, cron los lunes) que avisa por email si un producto se agota, desaparece o baja de 4★.

## Depende de Mario: alta en Afiliados de Amazon (10-15 min)

Hay que hacerla con tu identidad (acepta el contrato y la entrevista fiscal), así que no la hace el agente.

1. Entra en **https://afiliados.amazon.es** → «Registrarse». Mejor con **tu cuenta personal** de Amazon, no con la de vendedor de Aromas.
2. **Beneficiario**: Mario Cuadrado López, Calle Marchanilla 3, 45100 Sonseca (Toledo). Teléfono móvil tuyo (te llama o manda un PIN).
3. **Sitios web**: `https://hervor.inhumario.com`. Apps: ninguna.
4. **Perfil**:
   - ID de tienda preferido: **hervor-21** (si está cogido, `hervorcafe-21`).
   - ¿De qué tratan tus sitios web?: «Guías y comparativas de cafeteras, molinillos, hervidores, teteras y accesorios para preparar café y té en casa.»
   - Temas: Hogar y cocina (y Alimentación si lo pide).
   - Tipo de sitio: blog / sitio de comparativas.
   - Cómo generas tráfico: SEO (búsqueda orgánica).
   - Cómo generas ingresos: afiliación.
   - Cómo creas los enlaces: editor HTML / herramientas propias.
   - Visitantes únicos al mes: menos de 500.
   - Motivo: «Monetizar recomendaciones de equipo para café y té.»
5. **Después** (puede ser otro día, pero antes del primer pago): Información fiscal (persona física, residente en España, NIF) y método de pago (IBAN).
6. **Pásame el ID de tienda** (xxxx-21): lo pongo en `config.json` y redespliego. Hasta entonces los enlaces funcionan pero no generan comisión.

⚠️ Desde el alta hay **180 días para conseguir 3 ventas**; si no, Amazon cierra la cuenta (se puede volver a pedir). Conviene darse de alta cuando la web ya tenga contenido indexado, o sea ahora.

### A tener en cuenta en lo fiscal (tú lo dominas; solo lo dejo apuntado)

- Las comisiones las paga **Amazon Europe Core S.à r.l. (Luxemburgo)**: servicio B2B intracomunitario, que probablemente requiera ROI (036) y declarar en el 349. Amazon emite autofacturas.
- Encaje en tu alta de autónomo actual (epígrafe IAE de publicidad/intermediación) y en el IRPF como rendimiento de actividad.

## Siguiente fase (cuando haya tag)

1. **Indexación**: dar de alta la propiedad en Google Search Console y enviar el sitemap (el token de GSC es de Aromas; necesita verificación por DNS del subdominio, que ya controlamos).
2. **Ritmo de publicación**: 2 artículos nuevos por semana (búsquedas long-tail: «mejor cafetera italiana para inducción», «tetera para té matcha», «molinillo para espresso barato»…).
3. **Con 3 ventas → PA-API**: imágenes y precios en vivo en las fichas, que suben mucho la conversión.
4. **Dominio propio** cuando el tráfico lo justifique: cambiar `url` en `config.json`, añadir dominio en EasyPanel y redirección 301 desde el subdominio.
