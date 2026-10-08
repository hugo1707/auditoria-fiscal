(function(){
  // Tudo fica no localStorage deste navegador. Três chaves:
  //   done  -> { idDaLicao: timestamp }
  //   notes -> { idDaLicao: "texto" }
  //   check -> { idDaLicao: { indice: true } }
  var KEYS = { done: "af2-done", notes: "af2-notes", check: "af2-check" };
  function load(k){ try { return JSON.parse(localStorage.getItem(KEYS[k])) || {}; } catch(e){ return {}; } }
  function save(k, d){ try { localStorage.setItem(KEYS[k], JSON.stringify(d)); return true; } catch(e){ return false; } }
  var done = load("done"), notes = load("notes"), check = load("check");
  var L = window.LESSONS || [];

  // links com marca de concluída (índice e cronograma)
  document.querySelectorAll("a[data-id]").forEach(function(a){
    if (done[a.dataset.id]) a.classList.add("is-done");
  });

  var art = document.querySelector("article.lesson");
  if (art){
    var id = art.dataset.id;

    // botão de concluir
    var btn = art.querySelector(".done-btn");
    function paint(){
      var on = !!done[id];
      btn.classList.toggle("is-done", on);
      btn.textContent = on ? "Lição concluída — toque para desfazer" : "Marcar lição como concluída";
    }
    paint();
    btn.addEventListener("click", function(){
      if (done[id]) delete done[id]; else done[id] = Date.now();
      save("done", done); paint();
    });

    // anotações
    var note = document.getElementById("note");
    if (note){
      note.value = notes[id] || "";
      var t;
      note.addEventListener("input", function(){
        clearTimeout(t);
        t = setTimeout(function(){
          if (note.value.trim()) notes[id] = note.value; else delete notes[id];
          save("notes", notes);
        }, 300);
      });
    }

    // lista de domínio
    var mine = check[id] || {};
    art.querySelectorAll("input[data-check]").forEach(function(c){
      c.checked = !!mine[c.dataset.check];
      c.addEventListener("change", function(){
        var cur = check[id] || {};
        if (c.checked) cur[c.dataset.check] = true; else delete cur[c.dataset.check];
        if (Object.keys(cur).length) check[id] = cur; else delete check[id];
        save("check", check);
      });
    });
  }

  // progresso na página inicial
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

  // cópia de segurança (só na página inicial)
  var exp = document.getElementById("exp"), imp = document.getElementById("imp"), rst = document.getElementById("rst");
  var msg = document.getElementById("bmsg");
  function say(s){ if (msg) msg.textContent = s; }
  if (exp){
    exp.addEventListener("click", function(){
      var blob = new Blob([JSON.stringify({ v: 2, done: done, notes: notes, check: check }, null, 1)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "auditoria-fiscal-progresso.json";
      document.body.appendChild(a); a.click(); a.remove();
      say("Cópia exportada.");
    });
    imp.addEventListener("change", function(){
      var f = imp.files && imp.files[0];
      if (!f) return;
      var r = new FileReader();
      r.onload = function(){
        try {
          var d = JSON.parse(r.result);
          if (!d || d.v !== 2) throw new Error("formato");
          save("done", d.done || {}); save("notes", d.notes || {}); save("check", d.check || {});
          say("Cópia importada. Recarregando…");
          setTimeout(function(){ location.reload(); }, 400);
        } catch(e){ say("Arquivo inválido: use uma cópia exportada por esta página."); }
      };
      r.readAsText(f);
    });
    rst.addEventListener("click", function(){
      if (!confirm("Apagar progresso, anotações e marcações deste navegador?")) return;
      try { localStorage.removeItem(KEYS.done); localStorage.removeItem(KEYS.notes); localStorage.removeItem(KEYS.check); } catch(e){}
      location.reload();
    });
  }
})();
