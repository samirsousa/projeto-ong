# Aqui fica tudo que lê ou grava dados do site.
# Os dados atualmente ficam em arquivos JSON dentro da pasta "dados".
# LEMBRAR: Quando colocar um banco de dados, trocar o que está dentro
# dessas funções. O resto do site não precisa mudar.

import json
import os
import threading
import uuid
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from config_site import SITE

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
ARQ_POSTS = os.path.join(PASTA, "posts.json")
ARQ_ADMIN = os.path.join(PASTA, "admin.json")
ARQ_EQUIPE = os.path.join(PASTA, "equipe.json")
ARQ_GALERIA = os.path.join(PASTA, "galeria.json")
ARQ_FOTOS_PROJETOS = os.path.join(PASTA, "fotos_projetos.json")

# Evita que duas gravações aconteçam ao mesmo tempo.
_trava = threading.Lock()

# Filtros da página "Nos acompanhe". A chave é o valor salvo, o texto é o que aparece.
FILTROS = {
    "reels": "Reels & Vídeos",
    "pedagogico": "Projetos Pedagógicos",
    "solidario": "Ações Solidárias",
}

# Formatos do post (selo em cima da foto).
FORMATOS = {
    "foto": {"nome": "Foto", "icone": "photo_camera"},
    "carrossel": {"nome": "Carrossel", "icone": "collections"},
    "reels": {"nome": "Reels", "icone": "movie"},
}

# Filtros da galeria da página inicial.
GALERIA_TIPOS = {
    "edu": "Educação",
    "esporte": "Esporte",
    "evento": "Eventos & Festas",
}

SENHA_PADRAO = "aepec2025"
EMAIL_PADRAO = "admin@aepec.org.br"


def _agora():
    return datetime.now().replace(microsecond=0)


def _ler(caminho, padrao):
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _gravar(caminho, conteudo):
    os.makedirs(PASTA, exist_ok=True)
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, ensure_ascii=False, indent=2)
    # Troca o arquivo de uma vez para não corromper se o servidor cair no meio.
    os.replace(temporario, caminho)


# ---------- Posts do Instagram ----------

def listar_posts(incluir_removidos=False):
    """Devolve os posts do mais novo para o mais antigo."""
    posts = _ler(ARQ_POSTS, [])
    if not incluir_removidos:
        posts = [p for p in posts if p.get("ativo", True)]
    return sorted(posts, key=lambda p: p["inserido_em"], reverse=True)


def adicionar_post(link, filtro, formato, tema, legenda, hashtags, imagem):
    post = {
        "id": uuid.uuid4().hex[:10],
        "link": link,
        "filtro": filtro,
        "formato": formato,
        "tema": tema,
        "legenda": legenda,
        "hashtags": hashtags,
        "imagem": imagem,
        "inserido_em": _agora().isoformat(),
        "ativo": True,
        "removido_em": None,
    }
    with _trava:
        posts = _ler(ARQ_POSTS, [])
        posts.append(post)
        _gravar(ARQ_POSTS, posts)
    return post


def mudar_visibilidade(post_id, ativo):
    """Tira o post do site (ou volta), mas ele continua no histórico."""
    with _trava:
        posts = _ler(ARQ_POSTS, [])
        for p in posts:
            if p["id"] == post_id:
                p["ativo"] = ativo
                p["removido_em"] = None if ativo else _agora().isoformat()
                _gravar(ARQ_POSTS, posts)
                return True
    return False


def link_ja_existe(link):
    return any(p["link"] == link for p in _ler(ARQ_POSTS, []))


# ---------- Acesso do administrador ----------

def dados_admin():
    return _ler(ARQ_ADMIN, None)


def conferir_login(email, senha):
    admin = dados_admin()
    if not admin:
        return False
    return email.strip().lower() == admin["email"].lower() and check_password_hash(admin["senha"], senha)


def trocar_senha(nova_senha):
    with _trava:
        admin = dados_admin()
        admin["senha"] = generate_password_hash(nova_senha)
        admin["senha_alterada_em"] = _agora().isoformat()
        _gravar(ARQ_ADMIN, admin)


def resetar_admin():
    """Volta e-mail e senha para o padrão. Usado pelo comando de recuperação."""
    _gravar(ARQ_ADMIN, {
        "email": EMAIL_PADRAO,
        "senha": generate_password_hash(SENHA_PADRAO),
        "senha_alterada_em": None,
    })


# ---------- Família AEPEC (equipe) ----------

def listar_equipe():
    return _ler(ARQ_EQUIPE, [])


def pegar_membro(membro_id):
    return next((m for m in listar_equipe() if m["id"] == membro_id), None)


def salvar_membro(membro_id, nome, cargo, area, texto, fotos):
    """Cria uma pessoa nova (membro_id vazio) ou atualiza uma que já existe."""
    with _trava:
        equipe = _ler(ARQ_EQUIPE, [])
        dados_novos = {"nome": nome, "cargo": cargo, "area": area, "texto": texto,
                       "fotos": fotos, "atualizado_em": _agora().isoformat()}
        for m in equipe:
            if m["id"] == membro_id:
                m.update(dados_novos)
                break
        else:
            dados_novos["id"] = uuid.uuid4().hex[:10]
            equipe.append(dados_novos)
        _gravar(ARQ_EQUIPE, equipe)


def apagar_membro(membro_id):
    """Tira a pessoa da lista. Devolve as fotos dela para o site poder apagar os arquivos."""
    with _trava:
        equipe = _ler(ARQ_EQUIPE, [])
        membro = next((m for m in equipe if m["id"] == membro_id), None)
        if membro:
            equipe.remove(membro)
            _gravar(ARQ_EQUIPE, equipe)
            return membro.get("fotos", [])
    return []


def mover_membro(membro_id, para_cima):
    """Troca a pessoa de lugar com a de cima ou a de baixo."""
    with _trava:
        equipe = _ler(ARQ_EQUIPE, [])
        posicao = next((i for i, m in enumerate(equipe) if m["id"] == membro_id), None)
        if posicao is None:
            return
        outra = posicao - 1 if para_cima else posicao + 1
        if 0 <= outra < len(equipe):
            equipe[posicao], equipe[outra] = equipe[outra], equipe[posicao]
            _gravar(ARQ_EQUIPE, equipe)


# ---------- Fotos dos projetos ----------

def fotos_projetos():
    return _ler(ARQ_FOTOS_PROJETOS, {})


def adicionar_fotos_projeto(projeto_id, caminhos):
    with _trava:
        todas = _ler(ARQ_FOTOS_PROJETOS, {})
        todas.setdefault(projeto_id, []).extend(caminhos)
        _gravar(ARQ_FOTOS_PROJETOS, todas)


def remover_foto_projeto(projeto_id, posicao):
    """Tira a foto da lista e devolve o caminho dela."""
    with _trava:
        todas = _ler(ARQ_FOTOS_PROJETOS, {})
        lista = todas.get(projeto_id, [])
        if 0 <= posicao < len(lista):
            caminho = lista.pop(posicao)
            _gravar(ARQ_FOTOS_PROJETOS, todas)
            return caminho
    return None


def mover_foto_projeto(projeto_id, posicao, para_frente):
    """Troca a foto de lugar com a do lado. "para_frente" vai em direção à primeira."""
    with _trava:
        todas = _ler(ARQ_FOTOS_PROJETOS, {})
        lista = todas.get(projeto_id, [])
        outra = posicao - 1 if para_frente else posicao + 1
        if 0 <= posicao < len(lista) and 0 <= outra < len(lista):
            lista[posicao], lista[outra] = lista[outra], lista[posicao]
            _gravar(ARQ_FOTOS_PROJETOS, todas)


# ---------- Galeria da página inicial ----------

def listar_galeria():
    return _ler(ARQ_GALERIA, [])


def adicionar_galeria(foto, tipo, titulo, texto):
    with _trava:
        galeria = _ler(ARQ_GALERIA, [])
        galeria.append({"id": uuid.uuid4().hex[:10], "foto": foto, "tipo": tipo,
                        "titulo": titulo, "texto": texto, "inserido_em": _agora().isoformat()})
        _gravar(ARQ_GALERIA, galeria)


def editar_galeria(item_id, tipo, titulo, texto, foto_nova=None):
    """Atualiza a foto. Se trocar a imagem, devolve o caminho da antiga."""
    with _trava:
        galeria = _ler(ARQ_GALERIA, [])
        for item in galeria:
            if item["id"] == item_id:
                antiga = None
                item.update({"tipo": tipo, "titulo": titulo, "texto": texto})
                if foto_nova:
                    antiga, item["foto"] = item["foto"], foto_nova
                _gravar(ARQ_GALERIA, galeria)
                return antiga
    return None


def apagar_galeria(item_id):
    """Tira a foto da galeria e devolve o caminho dela."""
    with _trava:
        galeria = _ler(ARQ_GALERIA, [])
        item = next((i for i in galeria if i["id"] == item_id), None)
        if item:
            galeria.remove(item)
            _gravar(ARQ_GALERIA, galeria)
            return item["foto"]
    return None


def mover_galeria(item_id, para_cima):
    with _trava:
        galeria = _ler(ARQ_GALERIA, [])
        posicao = next((i for i, g in enumerate(galeria) if g["id"] == item_id), None)
        if posicao is None:
            return
        outra = posicao - 1 if para_cima else posicao + 1
        if 0 <= outra < len(galeria):
            galeria[posicao], galeria[outra] = galeria[outra], galeria[posicao]
            _gravar(ARQ_GALERIA, galeria)


# ---------- Primeira execução ----------

def preparar():
    """Cria os arquivos na primeira vez que o site roda."""
    os.makedirs(PASTA, exist_ok=True)
    if not os.path.exists(ARQ_ADMIN):
        resetar_admin()
    if not os.path.exists(ARQ_POSTS):
        _gravar(ARQ_POSTS, [])  # começa vazio: o site mostra "Posts em breve!"
    if not os.path.exists(ARQ_FOTOS_PROJETOS) or not os.path.exists(ARQ_GALERIA):
        from projetos import FOTOS_INICIAIS, GALERIA_INICIAL
        if not os.path.exists(ARQ_FOTOS_PROJETOS):
            _gravar(ARQ_FOTOS_PROJETOS, FOTOS_INICIAIS)
        if not os.path.exists(ARQ_GALERIA):
            agora = _agora().isoformat()
            _gravar(ARQ_GALERIA, [dict(g, id=uuid.uuid4().hex[:10], inserido_em=agora) for g in GALERIA_INICIAL])
    if not os.path.exists(ARQ_EQUIPE):
        from equipe_inicial import EQUIPE_INICIAL
        agora = _agora().isoformat()
        _gravar(ARQ_EQUIPE, [dict(m, id=uuid.uuid4().hex[:10], atualizado_em=agora) for m in EQUIPE_INICIAL])
