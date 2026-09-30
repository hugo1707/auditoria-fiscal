(function(){
  var KEY = "af-dfe-efd-done";
  function load(){ try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch(e){ return {}; } }
  function save(d){ try { localStorage.setItem(KEY, JSON.stringify(d)); } catch(e){} }
  var done = load();
  var L = window.LESSONS || [];

  // mark links
  document.querySelectorAll("a[data-id]").forEach(function(a){
    if (done[a.dataset.id]) a.classList.add("is-done");
  });

  // lesson button
  var btn = document.querySelector(".done-btn");
  function paint(){
    if (!btn) return;
    var on = !!done[btn.dataset.id];
    btn.classList.toggle("is-done", on);
    btn.textContent = on ? "Lição concluída — toque para desfazer" : "Marcar lição como concluída";
  }
  if (btn){
    paint();
    btn.addEventListener("click", function(){
      if (done[btn.dataset.id]) delete done[btn.dataset.id]; else done[btn.dataset.id] = Date.now();
      save(done); paint();
    });
  }

  // home progress
  var fill = document.getElementById("pfill");
  var txt = document.getElementById("ptext");
  var cont = document.getElementById("continue");
  if (fill && txt){
    var n = L.filter(function(l){ return done[l.id]; }).length;
    fill.style.width = (L.length ? (100 * n / L.length) : 0) + "%";
    if (n === 0){
      txt.textContent = "Nenhuma lição concluída ainda.";
    } else if (n === L.length){
      txt.textContent = "Trilha concluída: " + n + " de " + L.length + " lições. Hora da revisão geral.";
      cont.textContent = "Rever o cronograma"; cont.href = "plano.html";
    } else {
      txt.textContent = n + " de " + L.length + " lições concluídas.";
      var next = L.find(function(l){ return !done[l.id]; });
      cont.textContent = "Continuar: " + next.code + " " + next.title;
      cont.href = "licoes/" + next.id + ".html";
    }
  }
})();
