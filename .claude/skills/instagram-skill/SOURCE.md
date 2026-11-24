# Origen de esta skill

- Repositorio: https://github.com/social-media-skills/instagram-skill
- Commit instalado: `840fad350ba6ac948f6536e5e4130856f6e0065a` ("Smoother first-time posting setup")
- Licencia: MIT (declarada en `SKILL.md`)
- Instalada tal cual desde `skills/instagram-skill/`, **sin** la carpeta `examples/` (11 MB de imágenes y video de ejemplo; están en el repositorio original).

## Revisión antes de instalar
- Los 8 scripts de `scripts/` son locales (Pillow y FFmpeg). Solo usan red para: descargar tipografías de Google Fonts si faltan (las dos que se necesitan ya vienen incluidas en `fonts/`) y subir archivos a una URL prefirmada de WoopSocial (`upload_parts.py`, solo al publicar).
- No leen variables de entorno ni credenciales, y no ejecutan código dinámico.
- **Publicar** requiere conectar WoopSocial, un servicio de terceros (plan gratuito: 2 cuentas; más cuentas, de pago). Es opcional: sin conectarlo, la skill entrega archivos, textos y calendario. Ver `references/woopsocial.md`.

## Actualizar
Vuelve a copiar `skills/instagram-skill/` desde el repositorio original y revisa los cambios antes de usarlos.
