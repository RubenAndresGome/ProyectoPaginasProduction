// Solo carpetas del proyecto (nunca .venv/node_modules: hace lento el escaneo)
const apps = ["theme", "mainapp", "pages", "blog", "login_and_reg", "entrenador", "perfil", "mensajes"];
module.exports = {
  content: [
    ...apps.map((a) => `./${a}/templates/**/*.html`),
    ...apps.map((a) => `./${a}/**/*.py`),
    "./static/js/**/*.js",
  ],
  darkMode: "class",
  theme: { extend: { fontFamily: { sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"] } } },
  plugins: [],
};
