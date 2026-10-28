# Aqui fica tudo que lê ou grava dados do site
# Os dados ficam no banco SQLite "dados/aepec.db"
# As tabelas estão descritas no arquivo schema.sql

import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

PASTA_APP = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(PASTA_APP, "dados")
ARQ_BANCO = os.path.join(PASTA, "aepec.db")
ARQ_SCHEMA = os.path.join(PASTA_APP, "schema.sql")

# Filtros da página "Nos acompanhe". A chave é o valor salvo e o texto é o que aparece
FILTROS = {
    "reels": "Reels e vídeos",
    "pedagogico": "Projetos pedagógicos",
    "solidario": "Ações solidárias",
}

# Formatos do post (selo em cima da foto)
FORMATOS = {
    "foto": {"nome": "Foto", "icone": "photo_camera"},
    "carrossel": {"nome": "Carrossel", "icone": "collections"},
    "reels": {"nome": "Reels", "icone": "movie"},
}

# Filtros da galeria da página inicial
GALERIA_TIPOS = {
    "edu": "Educação",
    "esporte": "Esporte",
    "evento": "Eventos e festas",
}


def _agora():
    return datetime.now().replace(microsecond=0).isoformat()


@contextmanager
def _conectar():
    """Abre o banco, salva tudo no final e fecha. Se der erro, desfaz o que foi feito"""
    con = sqlite3.connect(ARQ_BANCO, timeout=10)
    con.row_factory = sqlite3.Row  # permite ler as colunas pelo nome
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _proxima_posicao(con, tabela, onde="", valores=()):
    """Número para colocar um item novo no fim da lista"""
    linha = con.execute(f"SELECT COALESCE(MAX(posicao), -1) + 1 FROM {tabela} {onde}", valores).fetchone()
    return linha[0]


def _trocar_com_vizinho(con, tabela, item_id, para_cima, onde="", valores=()):
    """Troca a posição do item com a do item de cima ou de baixo"""
    ids = [linha["id"] for linha in con.execute(f"SELECT id FROM {tabela} {onde} ORDER BY posicao", valores)]
    if item_id not in ids:
        return
    i = ids.index(item_id)
    j = i - 1 if para_cima else i + 1
    if 0 <= j < len(ids):
        ids[i], ids[j] = ids[j], ids[i]
        for posicao, id_ in enumerate(ids):
            con.execute(f"UPDATE {tabela} SET posicao = ? WHERE id = ?", (posicao, id_))


# ---------- Posts do Instagram ----------

def _post(linha):
    post = dict(linha)
    post["ativo"] = bool(post["ativo"])
    return post


def listar_posts(incluir_removidos=False):
    """Devolve os posts do mais novo para o mais antigo"""
    sql = "SELECT * FROM posts"
    if not incluir_removidos:
        sql += " WHERE ativo = 1"
    sql += " ORDER BY inserido_em DESC, id DESC"
    with _conectar() as con:
        return [_post(linha) for linha in con.execute(sql)]


def adicionar_post(link, filtro, formato, tema, legenda, hashtags, imagem):
    with _conectar() as con:
        con.execute(
            """INSERT INTO posts (link, filtro, formato, tema, legenda, hashtags, imagem, inserido_em)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (link, filtro, formato, tema, legenda, hashtags, imagem, _agora()),
        )


def mudar_visibilidade(post_id, ativo):
    """Tira o post do site (ou volta), mas ele continua no histórico"""
    with _conectar() as con:
        mudou = con.execute(
            "UPDATE posts SET ativo = ?, removido_em = ? WHERE id = ?",
            (int(ativo), None if ativo else _agora(), post_id),
        ).rowcount
    return mudou > 0


def link_ja_existe(link):
    with _conectar() as con:
        return con.execute("SELECT 1 FROM posts WHERE link = ?", (link,)).fetchone() is not None


# ---------- Acesso do administrador ----------

def dados_admin():
    with _conectar() as con:
        linha = con.execute("SELECT * FROM admin WHERE id = 1").fetchone()
    return dict(linha) if linha else None


def conferir_login(email, senha):
    admin = dados_admin()
    if not admin:
        return False
    return email.strip().lower() == admin["email"].lower() and check_password_hash(admin["senha"], senha)


def trocar_senha(nova_senha):
    with _conectar() as con:
        con.execute("UPDATE admin SET senha = ?, senha_alterada_em = ? WHERE id = 1",
                    (generate_password_hash(nova_senha), _agora()))


def definir_admin(email, senha):
    """Cria o administrador ou troca o e-mail e a senha dele. Usado pelo comando criar-admin"""
    with _conectar() as con:
        con.execute(
            """INSERT INTO admin (id, email, senha) VALUES (1, ?, ?)
               ON CONFLICT (id) DO UPDATE SET email = excluded.email, senha = excluded.senha,
                                              senha_alterada_em = NULL""",
            (email.strip().lower(), generate_password_hash(senha)),
        )


def registrar_erro_login(ip):
    with _conectar() as con:
        con.execute("INSERT INTO tentativas_login (ip, quando) VALUES (?, ?)", (ip, time.time()))
        # Apaga as tentativas com mais de um dia, para a tabela não crescer sem parar
        con.execute("DELETE FROM tentativas_login WHERE quando < ?", (time.time() - 86400,))


def contar_erros_login(segundos, ip=None):
    """Quantas tentativas erradas nos últimos "segundos". Sem ip, conta de todos"""
    desde = time.time() - segundos
    with _conectar() as con:
        if ip:
            linha = con.execute("SELECT COUNT(*) FROM tentativas_login WHERE ip = ? AND quando > ?", (ip, desde))
        else:
            linha = con.execute("SELECT COUNT(*) FROM tentativas_login WHERE quando > ?", (desde,))
        return linha.fetchone()[0]


def limpar_erros_login(ip):
    with _conectar() as con:
        con.execute("DELETE FROM tentativas_login WHERE ip = ?", (ip,))


# ---------- Família AEPEC (equipe) ----------

def listar_equipe():
    with _conectar() as con:
        equipe = [dict(linha, fotos=[]) for linha in con.execute("SELECT * FROM equipe ORDER BY posicao")]
        por_id = {m["id"]: m for m in equipe}
        for foto in con.execute("SELECT membro_id, caminho FROM equipe_fotos ORDER BY posicao"):
            por_id[foto["membro_id"]]["fotos"].append(foto["caminho"])
    return equipe


def pegar_membro(membro_id):
    return next((m for m in listar_equipe() if m["id"] == membro_id), None)


def salvar_membro(membro_id, nome, cargo, area, texto, fotos):
    """Cria uma pessoa nova (membro_id vazio) ou atualiza uma que já existe"""
    with _conectar() as con:
        if membro_id:
            con.execute("UPDATE equipe SET nome = ?, cargo = ?, area = ?, texto = ?, atualizado_em = ? WHERE id = ?",
                        (nome, cargo, area, texto, _agora(), membro_id))
        else:
            membro_id = con.execute(
                "INSERT INTO equipe (nome, cargo, area, texto, posicao, atualizado_em) VALUES (?, ?, ?, ?, ?, ?)",
                (nome, cargo, area, texto, _proxima_posicao(con, "equipe"), _agora()),
            ).lastrowid
        # As fotos são gravadas de novo, na ordem nova
        con.execute("DELETE FROM equipe_fotos WHERE membro_id = ?", (membro_id,))
        con.executemany("INSERT INTO equipe_fotos (membro_id, posicao, caminho) VALUES (?, ?, ?)",
                        [(membro_id, i, caminho) for i, caminho in enumerate(fotos)])


def apagar_membro(membro_id):
    """Tira a pessoa da lista. Devolve as fotos dela para o site poder apagar os arquivos"""
    with _conectar() as con:
        fotos = [linha["caminho"] for linha in
                 con.execute("SELECT caminho FROM equipe_fotos WHERE membro_id = ?", (membro_id,))]
        con.execute("DELETE FROM equipe WHERE id = ?", (membro_id,))
    return fotos


def mover_membro(membro_id, para_cima):
    with _conectar() as con:
        _trocar_com_vizinho(con, "equipe", membro_id, para_cima)


# ---------- Fotos dos projetos ----------

def fotos_projetos():
    """Devolve {"jovem": ["foto1.jpg", "foto2.jpg"], ...}. A primeira é a do cartão"""
    todas = {}
    with _conectar() as con:
        for linha in con.execute("SELECT projeto_id, caminho FROM projeto_fotos ORDER BY posicao"):
            todas.setdefault(linha["projeto_id"], []).append(linha["caminho"])
    return todas


def adicionar_fotos_projeto(projeto_id, caminhos):
    with _conectar() as con:
        inicio = _proxima_posicao(con, "projeto_fotos", "WHERE projeto_id = ?", (projeto_id,))
        con.executemany("INSERT INTO projeto_fotos (projeto_id, posicao, caminho) VALUES (?, ?, ?)",
                        [(projeto_id, inicio + i, c) for i, c in enumerate(caminhos)])


def _ids_fotos_projeto(con, projeto_id):
    return [linha["id"] for linha in
            con.execute("SELECT id FROM projeto_fotos WHERE projeto_id = ? ORDER BY posicao", (projeto_id,))]


def remover_foto_projeto(projeto_id, posicao):
    """Tira a foto da lista e devolve o caminho dela. "posicao" começa em 0"""
    with _conectar() as con:
        ids = _ids_fotos_projeto(con, projeto_id)
        if not 0 <= posicao < len(ids):
            return None
        caminho = con.execute("SELECT caminho FROM projeto_fotos WHERE id = ?", (ids[posicao],)).fetchone()[0]
        con.execute("DELETE FROM projeto_fotos WHERE id = ?", (ids[posicao],))
    return caminho


def mover_foto_projeto(projeto_id, posicao, para_frente):
    """Troca a foto de lugar com a do lado. "para_frente" vai em direção à primeira"""
    with _conectar() as con:
        ids = _ids_fotos_projeto(con, projeto_id)
        if 0 <= posicao < len(ids):
            _trocar_com_vizinho(con, "projeto_fotos", ids[posicao], para_frente,
                                "WHERE projeto_id = ?", (projeto_id,))


# ---------- Galeria da página inicial ----------

def listar_galeria():
    with _conectar() as con:
        return [dict(linha) for linha in con.execute("SELECT * FROM galeria ORDER BY posicao")]


def adicionar_galeria(foto, tipo, titulo, texto):
    with _conectar() as con:
        con.execute("INSERT INTO galeria (foto, tipo, titulo, texto, posicao, inserido_em) VALUES (?, ?, ?, ?, ?, ?)",
                    (foto, tipo, titulo, texto, _proxima_posicao(con, "galeria"), _agora()))


def editar_galeria(item_id, tipo, titulo, texto, foto_nova=None):
    """Atualiza a foto. Se trocar a imagem, devolve o caminho da antiga"""
    with _conectar() as con:
        linha = con.execute("SELECT foto FROM galeria WHERE id = ?", (item_id,)).fetchone()
        if not linha:
            return None
        con.execute("UPDATE galeria SET tipo = ?, titulo = ?, texto = ?, foto = ? WHERE id = ?",
                    (tipo, titulo, texto, foto_nova or linha["foto"], item_id))
    return linha["foto"] if foto_nova else None


def apagar_galeria(item_id):
    """Tira a foto da galeria e devolve o caminho dela"""
    with _conectar() as con:
        linha = con.execute("SELECT foto FROM galeria WHERE id = ?", (item_id,)).fetchone()
        con.execute("DELETE FROM galeria WHERE id = ?", (item_id,))
    return linha["foto"] if linha else None


def mover_galeria(item_id, para_cima):
    with _conectar() as con:
        _trocar_com_vizinho(con, "galeria", item_id, para_cima)


# ---------- Primeira execução ----------

def preparar():
    """Cria as tabelas. Na primeira vez, também coloca a equipe e as fotos iniciais"""
    os.makedirs(PASTA, exist_ok=True)
    banco_novo = not os.path.exists(ARQ_BANCO)
    with _conectar() as con, open(ARQ_SCHEMA, encoding="utf-8") as arquivo:
        con.executescript(arquivo.read())
    if banco_novo:
        _colocar_dados_iniciais()


def _colocar_dados_iniciais():
    from equipe_inicial import EQUIPE_INICIAL
    from projetos import FOTOS_INICIAIS, GALERIA_INICIAL

    for m in EQUIPE_INICIAL:
        salvar_membro(None, m["nome"], m["cargo"], m["area"], m["texto"], m["fotos"])
    for projeto_id, caminhos in FOTOS_INICIAIS.items():
        adicionar_fotos_projeto(projeto_id, caminhos)
    for g in GALERIA_INICIAL:
        adicionar_galeria(g["foto"], g["tipo"], g["titulo"], g["texto"])