# Arquivo principal do site

import os
import re
import secrets
import time
import uuid
from datetime import date, datetime
from functools import wraps

import click
from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)
from markupsafe import Markup, escape
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.middleware.proxy_fix import ProxyFix

import dados
from config_site import SITE
from projetos import PROJETOS

PASTA_APP = os.path.dirname(os.path.abspath(__file__))
PASTA_UPLOADS = os.path.join(PASTA_APP, "static", "uploads")
PASTA_FOTOS = os.path.join(PASTA_APP, "static", "img", "fotos")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # limite de 8 MB por envio
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("AEPEC_HTTPS") == "1"
if os.environ.get("AEPEC_PROXY") == "1":
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)


def _chave_secreta():
    # A chave protege o login
    chave = os.environ.get("AEPEC_SECRET_KEY")
    if chave:
        return chave
    arquivo = os.path.join(dados.PASTA, ".chave")
    os.makedirs(dados.PASTA, exist_ok=True)
    if not os.path.exists(arquivo):
        with open(arquivo, "w") as f:
            f.write(secrets.token_hex(32))
    with open(arquivo) as f:
        return f.read().strip()


app.secret_key = _chave_secreta()
dados.preparar()


# ---------- Funções usadas nas páginas ----------

def foto_local(nome):
    """Procura a foto em static/img/fotos. Devolve vazio se não tiver"""
    for ext in ("jpg", "jpeg", "png", "webp"):
        if os.path.exists(os.path.join(PASTA_FOTOS, f"{nome}.{ext}")):
            return url_for("static", filename=f"img/fotos/{nome}.{ext}")
    return ""


def foto_post(post):
    return url_for("static", filename=post["imagem"]) if post.get("imagem") else ""


def tempo_relativo(iso):
    """Transforma a data em texto, por exemplo: Há 3 dias"""
    dias = (date.today() - datetime.fromisoformat(iso).date()).days
    if dias <= 0:
        return "Hoje"
    if dias == 1:
        return "Ontem"
    if dias < 7:
        return f"Há {dias} dias"
    if dias < 14:
        return "Semana passada"
    if dias < 30:
        return f"Há {dias // 7} semanas"
    if dias < 60:
        return "Mês passado"
    if dias < 365:
        return f"Há {dias // 30} meses"
    return "Há mais de um ano"


def data_br(iso, com_hora=True):
    if not iso:
        return ""
    d = datetime.fromisoformat(iso)
    return d.strftime("%d/%m/%Y às %H:%M") if com_hora else d.strftime("%d/%m/%Y")


def csrf_token():
    # Código secreto em cada formulário para impedir envios vindos de outros sites
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


@app.context_processor
def variaveis_das_paginas():
    return {
        "site": SITE,
        "foto_local": foto_local,
        "foto_post": foto_post,
        "csrf_token": csrf_token,
        "FILTROS": dados.FILTROS,
        "FORMATOS": dados.FORMATOS,
        "GALERIA_TIPOS": dados.GALERIA_TIPOS,
        "ano": date.today().year,
        "logado": session.get("admin") is True,
    }


def paragrafos(texto):
    """Linha em branco vira parágrafo novo. Enter simples vira quebra de linha"""
    blocos = [b.strip() for b in (texto or "").replace("\r\n", "\n").split("\n\n") if b.strip()]
    return Markup("".join(f"<p>{escape(b)}</p>".replace("\n", "<br>") for b in blocos))


app.jinja_env.filters["paragrafos"] = paragrafos
app.jinja_env.filters["relativo"] = tempo_relativo
app.jinja_env.filters["data_br"] = data_br


@app.before_request
def conferir_csrf():
    if request.method == "POST":
        if not session.get("csrf") or request.form.get("csrf") != session.get("csrf"):
            abort(400)

@app.after_request
def cabecalhos_de_seguranca(resposta):
    # Não deixa outro site abrir o nosso dentro de um iframe
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["Referrer-Policy"] = "same-origin"
    return resposta

def precisa_login(funcao):
    @wraps(funcao)
    def interna(*args, **kwargs):
        if session.get("admin") is not True:
            return redirect(url_for("login"))
        return funcao(*args, **kwargs)
    return interna


# ---------- Páginas públicas ----------

@app.route("/")
def inicio():
    return render_template("inicio.html", posts=dados.listar_posts()[:6], projetos=PROJETOS,
                           fotos_projetos=dados.fotos_projetos(), galeria=dados.listar_galeria(),
                           pagina="inicio")


@app.route("/nos-acompanhe")
def nos_acompanhe():
    return render_template("nos_acompanhe.html", posts=dados.listar_posts(), pagina="instagram")


@app.route("/familia-aepec")
def familia():
    return render_template("familia.html", equipe=dados.listar_equipe(), pagina="familia")


# ---------- Login do administrador ----------

# Proteção contra brute force e adivinhos
JANELA_SEGUNDOS = 15 * 60  # tempo em que as tentativas erradas são contadas
MAX_ERROS_POR_IP = 5       # erros de um mesmo endereço antes de bloquear
MAX_ERROS_GERAL = 30       # erros somando todos os endereços (ataque vindo de vários lugares)


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if session.get("admin") is True:
        return redirect(url_for("painel"))

    erro = None
    ip = request.remote_addr or "?"
    if not dados.dados_admin():
        erro = "Nenhum administrador cadastrado. Rode no terminal: flask --app app criar-admin"
    elif request.method == "POST":
        bloqueado = (dados.contar_erros_login(JANELA_SEGUNDOS, ip) >= MAX_ERROS_POR_IP
                     or dados.contar_erros_login(JANELA_SEGUNDOS) >= MAX_ERROS_GERAL)
        if bloqueado:
            erro = "Muitas tentativas erradas. Aguarde 15 minutos e tente de novo."
        elif dados.conferir_login(request.form.get("email", ""), request.form.get("senha", "")):
            dados.limpar_erros_login(ip)
            session.clear()
            session["admin"] = True
            # "Manter conectado" deixa o login salvo por 31 dias
            session.permanent = bool(request.form.get("lembrar"))
            return redirect(url_for("painel"))
        else:
            dados.registrar_erro_login(ip)
            time.sleep(1)  # espera 1 segundo a cada erro para atrasar quem testa muitas senhas
            erro = "E-mail ou senha incorretos."
    return render_template("login.html", erro=erro, pagina="login")


@app.route("/admin/sair", methods=["POST"])
def sair():
    session.clear()
    # Volta para o login com um aviso de que saiu
    flash("Você saiu do painel.", "ok")
    return redirect(url_for("login"))


# ---------- Painel do administrador ----------

@app.route("/admin")
@precisa_login
def painel():
    todos = dados.listar_posts(incluir_removidos=True)
    return render_template(
        "admin.html",
        posts=todos,
        total_ativos=sum(1 for p in todos if p.get("ativo", True)),
        admin=dados.dados_admin(),
        equipe=dados.listar_equipe(),
        projetos=PROJETOS,
        fotos_projetos=dados.fotos_projetos(),
        galeria=dados.listar_galeria(),
        pagina="admin",
    )


PADRAO_LINK = re.compile(
    r"^(?:https?://)?(?:www\.)?instagram\.com/(?:[A-Za-z0-9_.]+/)?(p|reel|reels|tv)/([A-Za-z0-9_-]+)"
)


def arrumar_link(link):
    """Confere se é link de post do Instagram e deixa no formato padrão"""
    achou = PADRAO_LINK.match(link.strip())
    if not achou:
        return None
    tipo = "reel" if achou.group(1) in ("reel", "reels") else achou.group(1)
    return f"https://www.instagram.com/{tipo}/{achou.group(2)}/"


def salvar_foto(arquivo, quadrada=False):
    """Salva a foto enviada, já reduzida para não pesar no site.
    quadrada=True corta no meio em formato quadrado (fotos da equipe)"""
    try:
        foto = Image.open(arquivo.stream)
        foto.load()
    except (UnidentifiedImageError, OSError):
        return None
    # Fotos de celular às vezes vêm deitadas então esse código corrige
    foto = ImageOps.exif_transpose(foto).convert("RGB")
    if quadrada:
        foto = ImageOps.fit(foto, (600, 600), centering=(0.5, 0.4))
    else:
        foto.thumbnail((1200, 1200))
    os.makedirs(PASTA_UPLOADS, exist_ok=True)
    nome = f"{uuid.uuid4().hex[:12]}.jpg"
    foto.save(os.path.join(PASTA_UPLOADS, nome), "JPEG", quality=85, optimize=True)
    return f"uploads/{nome}"


@app.route("/admin/posts", methods=["POST"])
@precisa_login
def novo_post():
    f = request.form
    link = arrumar_link(f.get("link", ""))
    filtro = f.get("filtro", "")
    formato = f.get("formato", "")

    problemas = []
    if not link:
        problemas.append("O link precisa ser de um post do Instagram (ex.: https://www.instagram.com/p/ABC123/).")
    elif dados.link_ja_existe(link):
        problemas.append("Esse post já foi cadastrado. Veja no histórico.")
    if filtro not in dados.FILTROS:
        problemas.append("Escolha o tipo do post.")
    if formato not in dados.FORMATOS:
        problemas.append("Escolha o formato do post.")

    caminho_foto = ""
    arquivo = request.files.get("imagem")
    if not problemas and arquivo and arquivo.filename:
        caminho_foto = salvar_foto(arquivo)
        if not caminho_foto:
            problemas.append("A imagem enviada não é válida. Use JPG, PNG ou WEBP.")

    if problemas:
        for p in problemas:
            flash(p, "erro")
        return redirect(url_for("painel") + "#novo-post")

    # Deixa cada hashtag começando com #
    tags = " ".join("#" + t.lstrip("#") for t in f.get("hashtags", "").split() if t.strip("#"))

    dados.adicionar_post(
        link=link,
        filtro=filtro,
        formato=formato,
        tema=f.get("tema", "").strip()[:60],
        legenda=f.get("legenda", "").strip()[:600],
        hashtags=tags[:300],
        imagem=caminho_foto,
    )
    flash("Post adicionado. Ele já aparece na página Nos acompanhe.", "ok")
    return redirect(url_for("painel") + "#historico")


@app.route("/admin/posts/<int:post_id>/<acao>", methods=["POST"])
@precisa_login
def visibilidade_post(post_id, acao):
    if acao not in ("remover", "restaurar"):
        abort(404)
    if dados.mudar_visibilidade(post_id, ativo=(acao == "restaurar")):
        flash("Post tirado do site." if acao == "remover" else "Post voltou para o site.", "ok")
    return redirect(url_for("painel") + "#historico")


@app.route("/admin/senha", methods=["POST"])
@precisa_login
def mudar_senha():
    f = request.form
    admin = dados.dados_admin()
    if not dados.conferir_login(admin["email"], f.get("atual", "")):
        flash("A senha atual está errada.", "erro")
    elif len(f.get("nova", "")) < 8:
        flash("A nova senha precisa ter pelo menos 8 caracteres.", "erro")
    elif f.get("nova") != f.get("confirmar"):
        flash("A confirmação não é igual à nova senha.", "erro")
    else:
        dados.trocar_senha(f["nova"])
        flash("Senha alterada.", "ok")
    return redirect(url_for("painel") + "#seguranca")


# ---------- Família AEPEC (equipe) no painel ----------

def apagar_arquivo_foto(caminho):
    """Apaga do disco só as fotos enviadas pelo painel (pasta uploads)"""
    if caminho and caminho.startswith("uploads/"):
        arquivo = os.path.join(PASTA_APP, "static", caminho)
        if os.path.exists(arquivo):
            os.remove(arquivo)


@app.route("/admin/equipe/nova", methods=["GET", "POST"])
@app.route("/admin/equipe/<int:membro_id>", methods=["GET", "POST"])
@precisa_login
def editar_membro(membro_id=None):
    membro = dados.pegar_membro(membro_id) if membro_id else None
    if membro_id and not membro:
        abort(404)

    if request.method == "POST":
        f = request.form
        nome = f.get("nome", "").strip()[:80]
        texto = f.get("texto", "").replace("\r\n", "\n").strip()[:4000]
        fotos = list(membro["fotos"]) if membro else []
        problemas = []
        if not nome:
            problemas.append("Coloque o nome da pessoa.")

        # Duas vagas de foto: a segunda serve para duplas (ex.: Tias Ana e Marilza)
        for vaga in (0, 1):
            arquivo = request.files.get(f"foto{vaga}")
            tirar = f.get(f"tirar{vaga}")
            if problemas:
                break
            if arquivo and arquivo.filename:
                nova = salvar_foto(arquivo, quadrada=True)
                if not nova:
                    problemas.append("Uma das fotos não é válida. Use JPG, PNG ou WEBP.")
                    break
                if vaga < len(fotos):
                    apagar_arquivo_foto(fotos[vaga])
                    fotos[vaga] = nova
                else:
                    fotos.append(nova)
            elif tirar and vaga < len(fotos):
                apagar_arquivo_foto(fotos[vaga])
                fotos[vaga] = None
        fotos = [x for x in fotos if x]

        if problemas:
            for p in problemas:
                flash(p, "erro")
            return render_template("admin_membro.html", membro=membro, form=f, pagina="admin")

        dados.salvar_membro(membro_id, nome, f.get("cargo", "").strip()[:80],
                            f.get("area", "").strip()[:80], texto, fotos)
        flash(f"{nome} foi salvo(a) na Família AEPEC.", "ok")
        return redirect(url_for("painel") + "#familia")

    return render_template("admin_membro.html", membro=membro, form=None, pagina="admin")


@app.route("/admin/equipe/<int:membro_id>/excluir", methods=["POST"])
@precisa_login
def excluir_membro(membro_id):
    membro = dados.pegar_membro(membro_id)
    for foto in dados.apagar_membro(membro_id):
        apagar_arquivo_foto(foto)
    if membro:
        flash(f"{membro['nome']} foi tirado(a) da Família AEPEC.", "ok")
    return redirect(url_for("painel") + "#familia")


@app.route("/admin/equipe/<int:membro_id>/mover/<direcao>", methods=["POST"])
@precisa_login
def mover_membro(membro_id, direcao):
    if direcao not in ("cima", "baixo"):
        abort(404)
    dados.mover_membro(membro_id, para_cima=(direcao == "cima"))
    return redirect(url_for("painel") + "#familia")


# ---------- Fotos dos projetos e galeria no painel ----------

IDS_PROJETOS = {p["id"] for p in PROJETOS}


@app.route("/admin/projetos/<projeto_id>/fotos", methods=["POST"])
@precisa_login
def adicionar_fotos_projeto(projeto_id):
    if projeto_id not in IDS_PROJETOS:
        abort(404)
    novas, erros = [], 0
    for arquivo in request.files.getlist("fotos"):
        if arquivo and arquivo.filename:
            caminho = salvar_foto(arquivo)
            if caminho:
                novas.append(caminho)
            else:
                erros += 1
    if novas:
        dados.adicionar_fotos_projeto(projeto_id, novas)
        flash(f"{len(novas)} foto(s) adicionada(s) ao projeto.", "ok")
    if erros:
        flash(f"{erros} arquivo(s) não eram imagens válidas (use JPG, PNG ou WEBP).", "erro")
    if not novas and not erros:
        flash("Escolha pelo menos uma foto.", "erro")
    return redirect(url_for("painel") + f"#projeto-{projeto_id}")


@app.route("/admin/projetos/<projeto_id>/fotos/<int:posicao>/<acao>", methods=["POST"])
@precisa_login
def mexer_foto_projeto(projeto_id, posicao, acao):
    if projeto_id not in IDS_PROJETOS or acao not in ("remover", "antes", "depois"):
        abort(404)
    if acao == "remover":
        apagar_arquivo_foto(dados.remover_foto_projeto(projeto_id, posicao))
        flash("Foto tirada do projeto.", "ok")
    else:
        dados.mover_foto_projeto(projeto_id, posicao, para_frente=(acao == "antes"))
    return redirect(url_for("painel") + f"#projeto-{projeto_id}")


def _campos_galeria(f):
    tipo = f.get("tipo", "")
    if tipo not in dados.GALERIA_TIPOS:
        return None
    return tipo, f.get("titulo", "").strip()[:80], f.get("texto", "").strip()[:300]


@app.route("/admin/galeria", methods=["POST"])
@precisa_login
def adicionar_galeria():
    campos = _campos_galeria(request.form)
    arquivo = request.files.get("foto")
    if not campos:
        flash("Escolha o filtro da foto.", "erro")
    elif not arquivo or not arquivo.filename:
        flash("Escolha a foto.", "erro")
    else:
        caminho = salvar_foto(arquivo)
        if not caminho:
            flash("A imagem enviada não é válida. Use JPG, PNG ou WEBP.", "erro")
        else:
            dados.adicionar_galeria(caminho, *campos)
            flash("Foto adicionada à galeria.", "ok")
    return redirect(url_for("painel") + "#galeria")


@app.route("/admin/galeria/<int:item_id>", methods=["POST"])
@precisa_login
def editar_galeria(item_id):
    campos = _campos_galeria(request.form)
    if not campos:
        flash("Escolha o filtro da foto.", "erro")
        return redirect(url_for("painel") + "#galeria")
    nova = None
    arquivo = request.files.get("foto")
    if arquivo and arquivo.filename:
        nova = salvar_foto(arquivo)
        if not nova:
            flash("A imagem enviada não é válida. Use JPG, PNG ou WEBP.", "erro")
            return redirect(url_for("painel") + "#galeria")
    apagar_arquivo_foto(dados.editar_galeria(item_id, *campos, foto_nova=nova))
    flash("Foto da galeria atualizada.", "ok")
    return redirect(url_for("painel") + "#galeria")


@app.route("/admin/galeria/<int:item_id>/excluir", methods=["POST"])
@precisa_login
def excluir_galeria(item_id):
    apagar_arquivo_foto(dados.apagar_galeria(item_id))
    flash("Foto tirada da galeria.", "ok")
    return redirect(url_for("painel") + "#galeria")


@app.route("/admin/galeria/<int:item_id>/mover/<direcao>", methods=["POST"])
@precisa_login
def mover_galeria(item_id, direcao):
    if direcao not in ("cima", "baixo"):
        abort(404)
    dados.mover_galeria(item_id, para_cima=(direcao == "cima"))
    return redirect(url_for("painel") + "#galeria")


# ---------- Erros ----------

@app.errorhandler(404)
def nao_encontrada(e):
    return render_template("erro.html", codigo=404, mensagem="Página não encontrada."), 404


@app.errorhandler(400)
def pedido_invalido(e):
    return render_template("erro.html", codigo=400, mensagem="O formulário expirou. Volte e tente de novo."), 400


@app.errorhandler(413)
def arquivo_grande(e):
    flash("A imagem é muito grande. O limite é 8 MB.", "erro")
    return redirect(request.referrer or url_for("painel"))


# ---------- Comando para criar o administrador ----------

@app.cli.command("criar-admin")
@click.option("--email", prompt="E-mail do administrador")
@click.password_option("--senha", prompt="Senha (mínimo 8 caracteres)", confirmation_prompt="Repita a senha")
def comando_criar_admin(email, senha):
    """Cria o administrador ou troca o e-mail e a senha dele"""
    if len(senha) < 8:
        raise click.BadParameter("a senha precisa ter pelo menos 8 caracteres", param_hint="--senha")
    dados.definir_admin(email, senha)
    click.echo(f"Administrador salvo: {email.strip().lower()}")


if __name__ == "__main__":
    app.run(debug=True)
