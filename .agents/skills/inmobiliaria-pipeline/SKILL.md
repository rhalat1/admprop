---
name: inmobiliaria-pipeline
description: >-
  Pipeline integral y automatizado para la creación de micrositios inmobiliarios
  optimizados para móviles en Cloudflare Pages y la generación de videos Reel (9:16)
  para Instagram/TikTok con locución neural boliviana y branding Century 21 Invictus.
---

# Skill: Pipeline Integral Inmobiliario (Micrositio + Reel + Despliegue)

Este procedimiento estandariza la producción de material digital de venta de alta conversión para propiedades inmobiliarias, compuesto por:
1. **Micrositio Web Ultraligero**: Alojado en Cloudflare Pages, optimizado para smartphones, con carrusel Swiper y llamadas directas a WhatsApp.
2. **Reel / Video de Presentación (9:16)**: Video vertical para Instagram y TikTok con efectos de paneo cinemático (Ken Burns), renderizado arquitectónico y locución neural nativa boliviana (`es-BO-SofiaNeural`).
3. **Despliegue Continuo**: Sincronización con GitHub y despliegue global en Cloudflare Pages.

---

## 1. Requisitos y Entorno de Ejecución

- **Python 3.10+** con las siguientes librerías instaladas:
  ```bash
  pip install pillow opencv-python imageio imageio-ffmpeg edge-tts numpy
  ```
- **FFmpeg**: Provisto automáticamente mediante el binario de `imageio-ffmpeg`.
- **Node.js / Wrangler**: Para despliegues en Cloudflare (`npx wrangler pages deploy`).

---

## 2. Ingesta de Datos y Estructura de Carpetas

Cada propiedad reside bajo `public/{slug-propiedad}/`:

```
public/{slug-propiedad}/
├── index.html                  # Micrositio web estático
└── images/
    ├── entrada-urbanizacion.jpg   # Ingreso recortado (sin asfalto roto)
    ├── calles-pavimentadas.jpg   # Vías internas
    ├── terreno-real.jpg          # Lote real con vista de frente
    ├── plano-catastral.jpg       # Mensura / plano catastral
    ├── amenidades-*.jpg          # Piscinas, canchas, club house
    ├── asesora-foto.jpg          # Foto de la asesora (proporción 1:1)
    ├── casa-proyecto-render.jpg  # Render arquitectónico sugerido
    ├── recorrido-animado.mp4     # Clip de 4-8s de ruta en mapa
    └── reel-presentacion.mp4     # Video final compilado para Instagram
```

---

## 3. Reglas de Procesamiento de Medios (Assets)

1. **Fotografía del Asesor/a**:
   - Debe encuadrarse estrictamente en formato **cuadrado (1:1)** centrado en el rostro antes de aplicarse a cualquier máscara circular, evitando cualquier distorsión o estiramiento.
2. **Fotografía de Ingreso / Entorno**:
   - Si la foto original muestra asfalto erosionado o tierra rota en el borde inferior, recortar la imagen (generalmente los últimos 20-25% inferiores) tanto para el sitio como para la tarjeta `og-preview.jpg`.
3. **Render Arquitectónico Emocional**:
   - Usar arquitectura minimalista adaptada al tipo de lote: si el terreno es interior (no en esquina), el render no debe tener curvas de calzada perimetral. Debe mostrar volúmenes cúbicos limpios, barandas de cristal y jardín privado.

---

## 4. Guía de Generación de Video Reel (9:16)

- **Resolución**: `720x1280` píxeles (Móvil HD). Pesa entre 4 y 6 MB para carga instantánea en redes y WhatsApp.
- **Tasa de fotogramas**: 30 FPS.
- **Cinematografía (Ken Burns Pan & Scan)**:
  - Las imágenes no deben encerrarse en recuadros reducidos; deben cubrir la totalidad de la pantalla (1080x1920 o 720x1280) con un movimiento de cámara horizontal/vertical suave (paneo) y zoom leve (1.03x a 1.12x).
  - Aplicar gradientes suaves en los extremos superior e inferior para máxima legibilidad.
- **Estilo "Modo Día" (Century 21 Invictus Light Theme)**:
  - Tarjetas flotantes: Blanco cristalino translúcido (`rgba(255,255,255,0.92)`) con bordes en oro cepillado (`#BEA05F`).
  - Textos principales: Negro obsidiana (`#121212`) y oro (`#9B7837`).
- **Locución Neural y Fonética**:
  - Motor: `edge-tts` con modelo `es-BO-SofiaNeural` (femenino boliviano, natural y pausado).
  - Regla fonética de marca: Forzar tilde en la primera sílaba para la pronunciación correcta: **`Céntury 21`** (para evitar que el sintetizador diga "centurý").
  - Frase de cierre estandarizada: *"Contacta a [Nombre del Asesor] de Céntury 21 Invictus. Comenta la palabra INFO en este video o contáctala al enlace del perfil..."*.

---

## 5. Reglas del Micrositio Web

1. **Diseño Claro (Light Theme)**:
   - Fondo: `#FAF9F6` (Piedra marfil cálido) y `#FFFFFF`.
   - Acentos: `#BEAF87` y `#947D4E` (Oro de Century 21 Invictus).
   - Tipografía principal en color oscuro de alto contraste.
2. **Carrusel Swiper para Celulares**:
   - Control táctil gestual (swipe), ocultando flechas laterales en pantallas menores a 768px para evitar bloqueos visuales. Indicador de posición en badge tipo `1 / 7`.
3. **Conversión y Contacto Directo**:
   - Enlace de WhatsApp con mensaje pre-cargado: `https://wa.me/591XXXXXXXX?text=...`
   - Enlace de llamada telefónica directa: `tel:XXXXXXXX` (sin espacios ni prefijos en el href para compatibilidad total con dialers de Android/iOS).
   - Metatags Open Graph completos (`og:title`, `og:description`, `og:image`) con imagen de 1200x630.

---

## 6. Despliegue y Llaves de Acceso

- **GitHub Push**:
  ```bash
  git push https://<GITHUB_PAT>@github.com/<USUARIO>/<REPO>.git main
  ```
- **Cloudflare Pages Deploy**:
  ```powershell
  $env:CLOUDFLARE_ACCOUNT_ID="<ACCOUNT_ID>"
  $env:CLOUDFLARE_API_TOKEN="<API_TOKEN>"
  npx wrangler pages deploy public --project-name <PROYECTO> --branch main
  ```
