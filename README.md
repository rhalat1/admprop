# RHA Inmobiliaria: Motor de Micrositios y Generador de Activos

Plataforma integral y automatizada para la creación de micrositios inmobiliarios optimizados para dispositivos móviles, generador de contenido multi-canal (Instagram Reels 9:16, carruseles 4:5, TikTok) y servidor MCP para asistentes de inteligencia artificial (Claude, ChatGPT, Grok).

---

## 📌 Documentación Clave del Proyecto

* **[PLAN_SAAS.md](PLAN_SAAS.md)**: Plan maestro de arquitectura de la plataforma SaaS (Modelo Híbrido VPS + Cloudflare Pages/R2, motor agnóstico, ingesta de estilos de asesores, hub de revisión visual y asistente de descubrimiento MCP).
* **[DOCUMENTACION_SISTEMA_Y_ARQUITECTURA.md](DOCUMENTACION_SISTEMA_Y_ARQUITECTURA.md)**: Especificación técnica detallada del pipeline inmobiliario, locución neural boliviana, animación de rutas y rendering de Reels en 9:16.
* **[ROADMAP.md](ROADMAP.md)**: Historial de hitos completados y fases de evolución.

---

## 🌐 Micrositios Activos (Cloudflare Pages)

* **Terreno Bella Flor (Urubó):** [https://admprop.pages.dev/urubo-bella-flor/](https://admprop.pages.dev/urubo-bella-flor/)
* **Servicio Cohosting Airbnb:** [https://admprop.pages.dev/](https://admprop.pages.dev/)

---

## 🏗️ Decisiones de Arquitectura Confirmadas

1. **Modelo Híbrido:**
   * **VPS Privado:** Aloja el backend SaaS (Node.js/Fastify, PostgreSQL, Drizzle ORM, colas BullMQ/Redis para renderizado de video y el Servidor MCP).
   * **Cloudflare Pages / CDN:** Despliegue estático automatizado de los micrositios para garantizar tiempos de carga móviles ultrarrápidos (<200 ms) y tolerancia absoluta a viralidad con 0% de sobrecarga para el VPS.
2. **Multimedia en Cloudflare R2:** Almacenamiento compatible con S3 para imágenes en formato WebP y videos MP4 optimizados sin costos de transferencia por visitas.
3. **Servidor MCP para Asistentes de IA:** Permite que usuarios de ChatGPT, Claude y Grok consulten benchmarks reales del mercado de Santa Cruz y reciban recomendaciones personalizadas con derivación directa al WhatsApp del asesor.
