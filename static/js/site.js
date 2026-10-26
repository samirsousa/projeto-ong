// Interações do site (menu, modo escuro, janelas, filtros).

// ---------- Modo escuro ----------
function aplicarTema(tema) {
  document.documentElement.setAttribute("data-tema", tema);
  document.querySelectorAll("[data-trocar-tema]").forEach(function (b) {
    b.setAttribute("aria-label", tema === "escuro" ? "Usar modo claro" : "Usar modo escuro");
    b.setAttribute("title", tema === "escuro" ? "Modo claro" : "Modo escuro");
  });
}

document.querySelectorAll("[data-trocar-tema]").forEach(function (botao) {
  botao.addEventListener("click", function () {
    var atual = document.documentElement.getAttribute("data-tema");
    var novo = atual === "escuro" ? "claro" : "escuro";
    aplicarTema(novo);
    try { localStorage.setItem("tema", novo); } catch (e) {}
  });
});
aplicarTema(document.documentElement.getAttribute("data-tema") || "claro");

// ---------- Menu do celular ----------
var botaoMenu = document.querySelector(".botao-menu");
var gaveta = document.getElementById("gaveta");

function fecharMenu() {
  if (!gaveta) return;
  gaveta.classList.remove("aberta");
  document.body.classList.remove("menu-aberto");
  botaoMenu.setAttribute("aria-expanded", "false");
  botaoMenu.querySelector(".icone").textContent = "menu";
}

if (botaoMenu && gaveta) {
  botaoMenu.addEventListener("click", function () {
    var abrir = !gaveta.classList.contains("aberta");
    gaveta.classList.toggle("aberta", abrir);
    document.body.classList.toggle("menu-aberto", abrir);
    botaoMenu.setAttribute("aria-expanded", abrir ? "true" : "false");
    botaoMenu.querySelector(".icone").textContent = abrir ? "close" : "menu";
  });
  // Fecha o menu ao clicar em um link
  gaveta.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", fecharMenu); });
  // Fecha se a tela ficar grande
  window.addEventListener("resize", function () { if (window.innerWidth >= 1180) fecharMenu(); });
}

// ---------- Aviso rápido no canto ----------
var timerAviso;
function mostrarAviso(texto) {
  var aviso = document.getElementById("aviso");
  if (!aviso) return;
  aviso.querySelector("span:last-child").textContent = texto;
  aviso.classList.add("visivel");
  clearTimeout(timerAviso);
  timerAviso = setTimeout(function () { aviso.classList.remove("visivel"); }, 3500);
}

// ---------- Janelas (modais) ----------
var ultimoFoco = null;

function abrirJanela(id) {
  var janela = document.getElementById(id);
  if (!janela) return;
  ultimoFoco = document.activeElement;
  janela.classList.add("aberta");
  document.body.style.overflow = "hidden";
  var fechar = janela.querySelector(".fechar");
  if (fechar) fechar.focus();
  // Na janela do vídeo, já começa a tocar
  var video = janela.querySelector("video");
  if (video) { var tocar = video.play(); if (tocar) tocar.catch(function () {}); }
}

function fecharJanela(janela) {
  janela.classList.remove("aberta");
  document.body.style.overflow = "";
  // Para o vídeo do YouTube ao fechar
  var iframe = janela.querySelector("iframe");
  if (iframe) { iframe.src = iframe.src; }
  var video = janela.querySelector("video");
  if (video) video.pause();
  if (ultimoFoco) ultimoFoco.focus();
}

document.querySelectorAll(".janela").forEach(function (janela) {
  // Clicar fora da caixa fecha
  janela.addEventListener("click", function (e) { if (e.target === janela) fecharJanela(janela); });
  janela.querySelectorAll("[data-fechar]").forEach(function (b) {
    b.addEventListener("click", function () { fecharJanela(janela); });
  });
});

document.addEventListener("keydown", function (e) {
  if (e.key !== "Escape") return;
  var aberta = document.querySelector(".janela.aberta");
  if (aberta) fecharJanela(aberta);
  else fecharMenu();
});

document.querySelectorAll("[data-abrir]").forEach(function (b) {
  b.addEventListener("click", function (e) {
    e.preventDefault();
    abrirJanela(b.getAttribute("data-abrir"));
  });
});

// Janela de informações (projetos e formas de ajudar)
document.querySelectorAll("[data-info]").forEach(function (b) {
  b.addEventListener("click", function () {
    var info = document.getElementById("info-" + b.getAttribute("data-info"));
    if (!info) return;
    document.getElementById("info-titulo").textContent = info.getAttribute("data-titulo");
    document.getElementById("info-texto").innerHTML = info.innerHTML;
    // A caixa do PIX só aparece na doação financeira
    document.getElementById("info-pix").classList.toggle("oculto", info.getAttribute("data-pix") !== "sim");
    // Textos longos (projetos) usam uma janela mais larga
    var caixa = document.querySelector("#janela-info .janela-caixa");
    caixa.classList.toggle("janela-texto", info.getAttribute("data-largo") === "sim");
    caixa.scrollTop = 0;
    abrirJanela("janela-info");
  });
});

// Foto ampliada da galeria
document.querySelectorAll("[data-ampliar]").forEach(function (b) {
  b.addEventListener("click", function () {
    var titulo = b.getAttribute("data-titulo") || b.querySelector("img").alt || "Foto da Galeria";
    var texto = b.getAttribute("data-texto") || "";
    document.getElementById("foto-titulo").textContent = titulo;
    document.getElementById("foto-img").src = b.querySelector("img").src;
    document.getElementById("foto-img").alt = titulo;
    document.getElementById("foto-texto").textContent = texto;
    // Sem descrição, esconde o espaço do texto
    document.getElementById("foto-texto").parentNode.classList.toggle("oculto", !texto);
    abrirJanela("janela-foto");
  });
});

// ---------- Copiar chave PIX ----------
function copiarTexto(texto) {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(texto);
  }
  // Jeito antigo, para navegadores sem a função nova
  return new Promise(function (ok, falha) {
    var campo = document.createElement("textarea");
    campo.value = texto;
    campo.style.position = "fixed";
    campo.style.opacity = "0";
    document.body.appendChild(campo);
    campo.select();
    try { document.execCommand("copy") ? ok() : falha(); } catch (e) { falha(); }
    document.body.removeChild(campo);
  });
}

document.querySelectorAll("[data-copiar]").forEach(function (b) {
  b.addEventListener("click", function () {
    var chave = b.getAttribute("data-copiar");
    copiarTexto(chave).then(function () {
      mostrarAviso("Chave PIX copiada: " + chave);
    }, function () {
      mostrarAviso("Não deu para copiar. A chave é: " + chave);
    });
  });
});

// ---------- Filtros (galeria do início e posts do Instagram) ----------
function ligarFiltros(grupo) {
  var botoes = grupo.querySelectorAll("[data-filtro]");
  var alvo = document.getElementById(grupo.getAttribute("data-alvo"));
  if (!alvo) return;
  botoes.forEach(function (botao) {
    botao.addEventListener("click", function () {
      botoes.forEach(function (b) { b.classList.remove("ativo", "ativa"); b.setAttribute("aria-pressed", "false"); });
      botao.classList.add(botao.classList.contains("aba") ? "ativa" : "ativo");
      botao.setAttribute("aria-pressed", "true");
      alvo.setAttribute("data-filtro-atual", botao.getAttribute("data-filtro"));
      atualizarLista(alvo, true);
    });
  });
}

// Mostra só os itens do filtro escolhido, respeitando o limite de "carregar mais"
function atualizarLista(lista, voltarAoInicio) {
  var filtro = lista.getAttribute("data-filtro-atual") || "todos";
  var porVez = parseInt(lista.getAttribute("data-por-vez") || "0", 10);
  if (voltarAoInicio) lista.setAttribute("data-limite", porVez || 9999);
  var limite = parseInt(lista.getAttribute("data-limite") || "9999", 10);
  var visiveis = 0, total = 0;
  lista.querySelectorAll("[data-tipo]").forEach(function (item) {
    var combina = filtro === "todos" || item.getAttribute("data-tipo") === filtro;
    if (combina) total++;
    var mostrar = combina && visiveis < limite;
    if (mostrar) visiveis++;
    item.classList.toggle("oculto", !mostrar);
  });
  var vazio = lista.querySelector(".vazio-filtro");
  if (vazio) vazio.classList.toggle("oculto", total > 0);
  var mais = document.querySelector('[data-carregar="' + lista.id + '"]');
  if (mais) mais.classList.toggle("oculto", visiveis >= total);
}

document.querySelectorAll("[data-alvo]").forEach(ligarFiltros);

document.querySelectorAll("[data-carregar]").forEach(function (botao) {
  var lista = document.getElementById(botao.getAttribute("data-carregar"));
  atualizarLista(lista, true);
  botao.addEventListener("click", function () {
    var porVez = parseInt(lista.getAttribute("data-por-vez"), 10);
    lista.setAttribute("data-limite", parseInt(lista.getAttribute("data-limite"), 10) + porVez);
    atualizarLista(lista, false);
  });
});

// ---------- Mostrar ou esconder senha ----------
document.querySelectorAll("[data-ver-senha]").forEach(function (b) {
  b.addEventListener("click", function () {
    var campo = document.getElementById(b.getAttribute("data-ver-senha"));
    var mostrar = campo.type === "password";
    campo.type = mostrar ? "text" : "password";
    b.querySelector(".icone").textContent = mostrar ? "visibility_off" : "visibility";
    b.setAttribute("aria-label", mostrar ? "Esconder senha" : "Mostrar senha");
  });
});

// ---------- Troca de página suave (navegadores sem transição nativa) ----------
// Sempre na mesma aba, só links do próprio site, sem ser âncora da mesma página
document.addEventListener("click", function (e) {
  if (!document.documentElement.classList.contains("sem-vt")) return;
  if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  var link = e.target.closest && e.target.closest("a[href]");
  if (!link || link.target === "_blank" || link.hasAttribute("download")) return;
  var destino = new URL(link.href, location.href);
  if (destino.origin !== location.origin) return;
  if (destino.pathname === location.pathname && destino.hash) return;
  e.preventDefault();
  document.body.classList.add("saindo");
  setTimeout(function () { location.href = destino.href; }, 180);
});
// Ao voltar pelo botão do navegador, a página não pode ficar apagada
window.addEventListener("pageshow", function () { document.body.classList.remove("saindo"); });

// ---------- Cartões aparecem ao rolar a página ----------
var paraRevelar = document.querySelectorAll("[data-revelar]");
if ("IntersectionObserver" in window) {
  var observador = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (entrada) {
      if (entrada.isIntersecting) {
        var el = entrada.target;
        el.classList.add("revelado");
        observador.unobserve(el);
        // Tira o atraso
        setTimeout(function () { el.style.transitionDelay = ""; }, 900 + Number(el.dataset.atraso || 0));
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
  paraRevelar.forEach(function (el) {
    // Pequeno atraso para os cartões aparecerem um depois do outro
    if (el.dataset.atraso) el.style.transitionDelay = el.dataset.atraso + "ms";
    observador.observe(el);
  });
} else {
  paraRevelar.forEach(function (el) { el.classList.add("revelado"); });
}

// ---------- Cor do selo de cada projeto (vem do projetos.py) ----------
document.querySelectorAll("[data-cor]").forEach(function (el) {
  el.style.background = el.dataset.cor;
});