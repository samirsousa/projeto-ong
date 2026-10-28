// Interações do painel do administrador

var form = document.getElementById("form-post");

// ---------- Prévia do post enquanto preenche ----------
function texto(id) { return document.getElementById(id); }

function atualizarPrevia() {
  var filtro = form.querySelector('input[name="filtro"]:checked');
  var formato = form.querySelector('input[name="formato"]:checked');
  var tema = texto("tema").value.trim();
  var legenda = texto("legenda").value.trim();
  var tags = texto("hashtags").value.trim().split(/\s+/).filter(Boolean)
    .map(function (t) { return "#" + t.replace(/^#+/, ""); }).join(" ");

  texto("previa-tema").textContent = tema || (filtro ? window.FILTROS[filtro.value] : "");
  texto("previa-legenda").textContent = legenda || "A legenda aparece aqui.";
  texto("previa-legenda").style.color = legenda ? "" : "var(--texto-3)";
  texto("previa-tags").textContent = tags;
  texto("conta-legenda").textContent = texto("legenda").value.length;
  if (formato) {
    texto("previa-formato").textContent = window.FORMATOS[formato.value].nome;
    texto("previa-formato-icone").textContent = window.FORMATOS[formato.value].icone;
  }
}

form.addEventListener("input", atualizarPrevia);
form.addEventListener("change", atualizarPrevia);
form.addEventListener("reset", function () {
  setTimeout(function () { mostrarFoto(null); texto("link-aviso").textContent = ""; atualizarPrevia(); }, 0);
});

// ---------- Link do Instagram ----------
// Confere o link e marca o formato "Reels" quando o link é de reels
var padraoLink = /^(?:https?:\/\/)?(?:www\.)?instagram\.com\/(?:[A-Za-z0-9_.]+\/)?(p|reel|reels|tv)\/([A-Za-z0-9_-]+)/;

texto("link").addEventListener("input", function () {
  var valor = this.value.trim();
  var aviso = texto("link-aviso");
  if (!valor) { aviso.textContent = ""; return; }
  var achou = valor.match(padraoLink);
  if (!achou) {
    aviso.textContent = "Esse link não parece ser de um post do Instagram.";
    aviso.style.color = "var(--erro)";
    return;
  }
  aviso.textContent = "Link de post válido.";
  aviso.style.color = "var(--ok)";
  if (achou[1] === "reel" || achou[1] === "reels") {
    form.querySelector('input[name="formato"][value="reels"]').checked = true;
    var reels = form.querySelector('input[name="filtro"][value="reels"]');
    if (reels) reels.checked = true;
    atualizarPrevia();
  }
});

// ---------- Foto de capa ----------
var campoFoto = texto("imagem");
var caixaFoto = texto("envio-foto");
var textoOriginal = texto("envio-texto").innerHTML;

function mostrarFoto(arquivo) {
  var img = texto("previa-foto");
  if (!arquivo) {
    img.classList.add("oculto");
    texto("previa-sem-foto").classList.remove("oculto");
    texto("envio-texto").innerHTML = textoOriginal;
    return;
  }
  if (arquivo.size > 8 * 1024 * 1024) {
    alert("A imagem passa de 8 MB. Escolha uma menor.");
    campoFoto.value = "";
    mostrarFoto(null);
    return;
  }
  img.src = URL.createObjectURL(arquivo);
  img.classList.remove("oculto");
  texto("previa-sem-foto").classList.add("oculto");
  texto("envio-texto").innerHTML = "<strong>" + arquivo.name.replace(/[<>&]/g, "") + "</strong><br><small>Clique para trocar</small>";
}

campoFoto.addEventListener("change", function () { mostrarFoto(campoFoto.files[0] || null); });
["dragenter", "dragover"].forEach(function (ev) {
  caixaFoto.addEventListener(ev, function () { caixaFoto.classList.add("arrastando"); });
});
["dragleave", "drop"].forEach(function (ev) {
  caixaFoto.addEventListener(ev, function () { caixaFoto.classList.remove("arrastando"); });
});

// ---------- Busca no histórico ----------
var tabela = texto("tabela-historico");
function filtrarHistorico() {
  if (!tabela) return;
  var busca = texto("busca").value.trim().toLowerCase();
  var tipo = texto("filtro-tipo").value;
  var estado = texto("filtro-estado").value;
  var achados = 0;
  tabela.querySelectorAll("tbody tr").forEach(function (linha) {
    var mostra = (!busca || linha.getAttribute("data-busca").indexOf(busca) !== -1) &&
      (!tipo || linha.getAttribute("data-tipo") === tipo) &&
      (!estado || linha.getAttribute("data-estado") === estado);
    linha.classList.toggle("oculto", !mostra);
    if (mostra) achados++;
  });
  texto("historico-vazio").classList.toggle("oculto", achados > 0);
}
["busca", "filtro-tipo", "filtro-estado"].forEach(function (id) {
  texto(id).addEventListener("input", filtrarHistorico);
});

// ---------- Força da nova senha ----------
var nova = texto("nova"), confirmar = texto("confirmar");
function conferirSenha() {
  var s = nova.value, pontos = 0;
  if (s.length >= 8) pontos++;
  if (s.length >= 12) pontos++;
  if (/[a-z]/.test(s) && /[A-Z]/.test(s)) pontos++;
  if (/\d/.test(s)) pontos++;
  if (/[^A-Za-z0-9]/.test(s)) pontos++;
  var niveis = [["0%", "var(--erro)", "Use pelo menos 8 caracteres. Misture letras, números e símbolos."],
    ["25%", "var(--erro)", "Senha fraca."], ["50%", "#f59e0b", "Senha razoável."],
    ["75%", "#84cc16", "Senha boa."], ["100%", "var(--ok)", "Senha forte."]];
  var n = s.length < 8 ? niveis[s ? 1 : 0] : niveis[Math.min(4, Math.max(1, pontos - 1))];
  texto("forca-barra").style.width = n[0];
  texto("forca-barra").style.background = n[1];
  texto("forca-texto").textContent = n[2];

  var c = texto("confere-texto");
  if (!confirmar.value) { c.textContent = ""; return; }
  var igual = confirmar.value === s;
  c.textContent = igual ? "As senhas são iguais." : "As senhas ainda não são iguais.";
  c.style.color = igual ? "var(--ok)" : "var(--erro)";
}
nova.addEventListener("input", conferirSenha);
confirmar.addEventListener("input", conferirSenha);
texto("form-senha").addEventListener("submit", function (e) {
  if (nova.value !== confirmar.value) {
    e.preventDefault();
    confirmar.focus();
    conferirSenha();
  }
});

atualizarPrevia();

// ---------- Fotos dos projetos e galeria ----------
// Mostra o nome do arquivo escolhido no botão
document.querySelectorAll(".escolher-arquivo input[type=file]").forEach(function (campo) {
  campo.addEventListener("change", function () {
    var aviso = campo.parentNode.querySelector("[data-texto-arquivo]");
    if (!aviso) return;
    var n = campo.files.length;
    aviso.textContent = n === 0 ? "Escolher foto" : n === 1 ? campo.files[0].name : n + " fotos escolhidas";
  });
});
// Abre e fecha o formulário de editar foto da galeria
document.querySelectorAll("[data-editar]").forEach(function (botao) {
  botao.addEventListener("click", function () {
    document.getElementById(botao.getAttribute("data-editar")).classList.toggle("oculto");
  });
});
