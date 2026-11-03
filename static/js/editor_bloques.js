/* Editor visual de artículos por bloques (Alpine.js).
   Cada cambio se guarda en el servidor y la respuesta trae la vista previa ya renderizada
   con las mismas plantillas de la página pública. */
function editorArticulo(cfg) {
  const leer = (id) => JSON.parse(document.getElementById(id).textContent);
  const csrf = () => (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
  const tipos = leer('datos-tipos');
  const nombres = Object.fromEntries(tipos.map((t) => [t.tipo, t.nombre]));

  return {
    bloques: leer('datos-bloques'),
    tipos,
    cats: leer('datos-cats'),
    titulo: cfg.titulo,
    publicado: cfg.publicado,
    portada: cfg.portada,
    activo: null,
    insertarDespues: null,
    vista: 'editar',
    estado: 'Todos los cambios guardados',
    estadoClase: 'text-slate-400',

    nombreTipo(t) { return nombres[t] || t; },

    async pedir(ruta, cuerpo, esArchivo = false) {
      this.estado = 'Guardando…'; this.estadoClase = 'text-amber-500';
      try {
        const r = await fetch(cfg.base + ruta, {
          method: 'POST',
          headers: esArchivo ? { 'X-CSRFToken': csrf() } : { 'X-CSRFToken': csrf(), 'Content-Type': 'application/json' },
          body: esArchivo ? cuerpo : JSON.stringify(cuerpo || {}),
          credentials: 'same-origin',
        });
        const data = await r.json().catch(() => ({ ok: false, error: `Error ${r.status}` }));
        if (!r.ok || !data.ok) throw new Error(data.error || `Error ${r.status}`);
        if (data.preview !== undefined) this.pintar(data.preview);
        this.estado = 'Guardado ✓'; this.estadoClase = 'text-emerald-600';
        return data;
      } catch (e) {
        this.estado = 'No se pudo guardar: ' + e.message; this.estadoClase = 'text-red-600';
        throw e;
      }
    },

    pintar(html) {
      const el = document.getElementById('vista-previa');
      el.innerHTML = html;
      if (window.MathJax && MathJax.typesetPromise) MathJax.typesetPromise([el]).catch(() => {});
      if (this.activo) this.resaltar(this.activo);
    },

    resaltar(id) {
      document.querySelectorAll('#vista-previa [data-bloque]').forEach((n) => {
        n.classList.toggle('editor-resaltado', String(n.dataset.bloque) === String(id));
      });
    },

    guardarMeta() {
      if (!this.titulo.trim()) { this.estado = 'El título no puede quedar vacío'; this.estadoClase = 'text-red-600'; return; }
      return this.pedir('meta/', { titulo: this.titulo, publicado: this.publicado, categorias: this.cats });
    },

    toggleCat(id) {
      this.cats = this.cats.includes(id) ? this.cats.filter((c) => c !== id) : [...this.cats, id];
      this.guardarMeta();
    },

    guardar(b) { return this.pedir(`bloque/${b.id}/`, { datos: b.datos }).catch(() => {}); },

    async agregar(tipo, despuesDe = null) {
      const data = await this.pedir('agregar/', { tipo, despues_de: despuesDe }).catch(() => null);
      if (!data) return;
      this.bloques = data.bloques;
      this.insertarDespues = null;
      this.activo = data.bloque.id;
      this.$nextTick(() => { this.resaltar(data.bloque.id); });
    },

    async borrar(b, i) {
      if (!confirm(`¿Eliminar este bloque (${this.nombreTipo(b.tipo)})?`)) return;
      await this.pedir(`bloque/${b.id}/borrar/`).then(() => this.bloques.splice(i, 1)).catch(() => {});
    },

    async mover(i, delta) {
      const j = i + delta;
      if (j < 0 || j >= this.bloques.length) return;
      const copia = [...this.bloques];
      [copia[i], copia[j]] = [copia[j], copia[i]];
      this.bloques = copia;
      await this.pedir('reordenar/', { ids: copia.map((b) => b.id) }).catch(() => {});
    },

    async subirImagen(b, ev) {
      const archivo = ev.target.files[0];
      if (!archivo) return;
      const fd = new FormData();
      fd.append('imagen', archivo);
      fd.append('datos', JSON.stringify(b.datos));
      const data = await this.pedir(`bloque/${b.id}/`, fd, true).catch(() => null);
      if (data) b.imagen = data.bloque.imagen;
      ev.target.value = '';
    },

    async subirPortada(ev) {
      const archivo = ev.target.files[0];
      if (!archivo) return;
      const fd = new FormData(); fd.append('imagen', archivo);
      const data = await this.pedir('portada/', fd, true).catch(() => null);
      if (data) this.portada = data.portada;
      ev.target.value = '';
    },

    async quitarPortada() {
      const fd = new FormData(); fd.append('quitar', '1');
      const data = await this.pedir('portada/', fd, true).catch(() => null);
      if (data) this.portada = '';
    },
  };
}
