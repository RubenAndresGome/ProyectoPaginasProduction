/* Easter egg: código Konami (↑↑↓↓←→←→BA) o escribir "hola" fuera de un campo de texto
   lleva a /hola-mundo/. */
(function () {
  const destino = "/hola-mundo/";
  const konami = ["ArrowUp","ArrowUp","ArrowDown","ArrowDown","ArrowLeft","ArrowRight","ArrowLeft","ArrowRight","b","a"];
  let k = 0, texto = "";
  document.addEventListener("keydown", function (e) {
    const t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    const key = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    k = key === konami[k] ? k + 1 : (key === konami[0] ? 1 : 0);
    texto = (texto + (key.length === 1 ? key : "")).slice(-4);
    if (k === konami.length || texto === "hola") { window.location.href = destino; }
  });
})();
