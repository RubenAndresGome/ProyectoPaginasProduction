# Documentación Técnica del Proyecto: ProyectoPaginas

## 1. Resumen del Proyecto

Este documento detalla la arquitectura y los flujos de trabajo del proyecto `ProyectoPaginas`. El proyecto, iniciado a partir de un curso de Django (Udemy, por Víctor Robles), ha sido extendido significativamente para incluir un sistema de plantillas dinámicas, un blog con funcionalidades avanzadas y una estructura de frontend basada en Tailwind CSS.

El objetivo de esta documentación es servir como referencia técnica para entender las decisiones de diseño y facilitar el mantenimiento y la expansión futura del proyecto.

---

## 2. Arquitectura de Aplicaciones

El proyecto está dividido en varias aplicaciones Django, cada una con una responsabilidad clara:

-   **`mainapp`**: La aplicación principal, probablemente originaria del curso. Contiene vistas para páginas estáticas (`index`, `hola_mundo`, `contacto`) y un CRUD básico para un modelo `Article` (diferente del blog).
-   **`blog`**: Un sistema de blog dedicado y robusto. Es completamente independiente y gestiona sus propios artículos (`Articulo_Page`) y categorías.
-   **`pages`**: El corazón del sistema de gestión de contenido (CMS). Esta app permite la creación de páginas dinámicas de dos maneras diferentes, lo que la convierte en la más compleja y potente.
-   **`theme`**: Una aplicación de soporte que contiene las plantillas base (`base.html`, `base_pura.html`) y otros elementos de diseño globales.

---

## 3. Flujos de Lógica Clave

### 3.1. Flujo de la App `blog`

-   **Modelos**: `Articulo_Page` para las publicaciones y `Categoria` para agruparlas. El modelo `Categoria` incluye un campo `slug` autogenerado para URLs amigables.
-   **Vista Principal (`lista_publicaciones`)**: Es una vista única que maneja el listado, la búsqueda y el filtrado.
    -   Utiliza `request.GET.get('q')` para obtener el término de búsqueda y `request.GET.get('cat')` para el slug de la categoría.
    -   Construye consultas dinámicas con `Q(title__icontains=...) | Q(content__icontains=...)` para la búsqueda textual.
    -   Filtra por `categoria__slug` para las categorías.
    -   Pasa el `queryset` filtrado y la lista completa de `categorias` a la plantilla.
-   **Plantillas**:
    -   `lista_publicaciones.html`: La plantilla principal que contiene el formulario de búsqueda/filtrado.
    -   `_card_publicacion.html`: Un fragmento reutilizable (`include`) que renderiza una sola "card" de artículo, promoviendo el código DRY (Don't Repeat Yourself).
    -   `detalle_publicacion.html`: Muestra un único post.
-   **URLs**: Utiliza un `app_name = 'blog'` para crear un **namespace**. Esto obliga a usar `{% url 'blog:nombre_de_la_ruta' %}` en las plantillas, evitando colisiones de nombres.

### 3.2. Flujo de la App `pages` (El Mini-CMS)

Esta app implementa dos patrones de diseño distintos:

**Patrón 1: Páginas Genéricas con Selector de Layout (Modelo `Page`)**

-   **Modelo `Page`**: Un modelo simple con `title`, `slug`, `content` (CKEditor) y un campo clave: `template`.
-   **Campo `template`**: Es un `CharField` con `choices`, que se muestra como un menú desplegable en el admin. Permite al usuario elegir qué plantilla usar para esa página (ej. "Página Estándar", "Página Limpia").
-   **Vista `page_detail`**: Una vista genérica que recibe un `slug`, busca la `Page` correspondiente y la renderiza usando la plantilla almacenada en el campo `page.template`.
-   **Este patrón es ideal para páginas de contenido simple** donde solo cambia el contenido principal (ej. "Política de Privacidad", "Sobre Nosotros").

**Patrón 2: Páginas de Molde Específico (Modelo `Home1Page`)**

-   **Modelo `Home1Page`**: Un modelo altamente específico que no tiene un campo de "contenido" genérico. En su lugar, tiene campos para cada elemento editable del layout `home-1.html` (ej. `hero_title`, `card1_image`, `about_text_paragraph1`, etc.).
-   **Plantilla (`home_1_page.html`)**: Una plantilla en `pages/templates/pages/moldes_pages/` que está cableada para usar las variables de un objeto `Home1Page`.
-   **Vista (`home_1_page_detail`) y URL**: Una vista y una URL dedicadas (`/home1/<slug>/`) que solo funcionan para este tipo de página.
-   **Este patrón es ideal para páginas complejas y estructuradas** (como una landing page) donde el usuario no escribe HTML, sino que rellena un formulario detallado en el admin. Es más restrictivo pero más seguro y fácil de usar para un no-desarrollador.

---

## 4. Flujo de Enrutamiento de URL (Resolución de `NoReverseMatch`)

El orden de inclusión de las URLs en `ProyectoPaginas/urls.py` es **crítico**.

```python
# ProyectoPaginas/urls.py
- urlpatterns = [
-    path('admin/', admin.site.urls),
-    path('', include('mainapp.urls')),
-    path('', include('blog.urls')),      # <-- Más específico
-    path('', include('pages.urls')),     # <-- Más genérico
- ]
```

1.  **`blog.urls` se procesa ANTES que `pages.urls`**: Esto es fundamental. La URL `/publicaciones/` de `blog.urls` es una cadena fija. La URL `<slug:slug>/` de `pages.urls` es un comodín que podría capturar "publicaciones". Al poner `blog.urls` primero, nos aseguramos de que `/publicaciones/` siempre sea manejado por la vista `lista_publicaciones` del blog.
2.  **`pages.urls` actúa como "catch-all"**: Al estar al final, la ruta `<slug:slug>/` de `pages` captura cualquier otra URL que no haya coincidido antes, permitiendo que las páginas dinámicas del modelo `Page` funcionen correctamente.

### Namespaces de URL

-   Los errores `NoReverseMatch` se solucionaron al añadir `app_name = 'nombre_app'` en los archivos `urls.py` de `mainapp` y `blog`.
-   Esto obliga a que todas las etiquetas `{% url %}` en las plantillas usen la sintaxis `{% url 'nombre_app:nombre_ruta' %}`.
-   Esta práctica es esencial en proyectos con múltiples aplicaciones para evitar ambigüedades y colisiones en los nombres de las rutas.

---

## 5. Conclusiones y Próximos Pasos

El proyecto ha evolucionado de una aplicación simple a un sistema híbrido que combina un blog funcional con un CMS de dos niveles. La clave para extenderlo es seguir los patrones establecidos:

-   Para añadir un nuevo "molde de página", se debe seguir el **Patrón 2** de la app `pages`: crear un nuevo modelo, una nueva plantilla, una nueva vista y una nueva URL.
-   Para añadir funcionalidades al blog, se debe trabajar dentro de la app `blog`.
-   Siempre se debe prestar atención al orden de las URLs y al uso de namespaces.
-   Cualquier cambio en `models.py` **requiere** la ejecución de `makemigrations` y `migrate`.
