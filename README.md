# Site AEPEC - Espaço Pequeno Cidadão

Site da AEPEC (Associação Espaço Pequeno Cidadão), ONG de São Gonçalo (RJ) que atende crianças, jovens e famílias com educação no contraturno, alimentação, esporte e informática.

O site mostra a história e os projetos da ONG, a equipe (Família AEPEC), fotos, os posts do Instagram e como doar. A equipe da AEPEC atualiza esse conteúdo por um painel do administrador, sem precisar mexer no código.

## Créditos - Time por trás dos códigos

| Função | Nome |
|---|---|
| Coordenador do grupo | Kaleo Accacio Pereira Lemos |
| Programadores | Samir Firmino Martins de Sousa, Guilherme Amorim Pereira de Araujo, Kaleo Accacio Pereira Lemos |
| Professora | Theresa Prado Gondim |
| Monitor | Daniel Oliveira |

## Tecnologias

| Tecnologia | Uso no projeto |
|---|---|
| Python 3 e Flask | Servidor, rotas e login |
| Jinja | Modelos HTML que recebem os dados do Python |
| SQLite | Banco de dados (um arquivo só, já vem com o Python) |
| Pillow | Reduz e ajusta as fotos enviadas pelo painel |
| HTML, CSS e JavaScript | Visual, modo escuro, menu do celular, filtros e animações |
| Git e GitHub | Controle de versões |

## O que o site tem

- Página inicial com os projetos, os números da AEPEC, o vídeo institucional, a galeria com filtros e as formas de doar (a chave PIX copia com um clique)
- Página Nos acompanhe, com os posts do Instagram separados por tipo
- Página Família AEPEC, com foto e apresentação de cada pessoa da equipe
- Modo claro e modo escuro
- Layout para celular, tablet e computador
- Painel do administrador para cadastrar posts, fotos, galeria e equipe
- Login que bloqueia por 15 minutos depois de várias senhas erradas

## Páginas

| Endereço | Página |
|---|---|
| `/` | Página inicial |
| `/nos-acompanhe` | Posts do Instagram |
| `/familia-aepec` | Equipe (Família AEPEC) |
| `/admin/login` | Login do administrador |
| `/admin` | Painel do administrador |

## Como rodar

Precisa de Python 3.10 ou mais novo e do Git. No GitHub Codespaces os dois já vêm instalados.

```
git clone <endereço do repositório>
cd projeto-ong
pip install -r requirements.txt
flask --app app criar-admin
python app.py
```

O `criar-admin` só precisa rodar na primeira vez. Ele pede o e-mail e a senha do administrador (mínimo de 8 caracteres). Para trocar uma senha esquecida, rode o mesmo comando de novo.

Depois abra `http://127.0.0.1:5000` no navegador. No Codespaces, use a aba Ports e clique no globo da porta 5000. Para desligar o site, aperte Ctrl + C no terminal.

## Como usar o painel

O link do painel fica no rodapé do site, em "Acesso Administrativo (Restrito)". Entre com o e-mail e a senha criados pelo `criar-admin`.

Nos posts do Instagram, cole o link do post, escolha o tipo e o formato e, se quiser, envie uma foto de capa. Um post tirado do site continua no histórico e pode voltar a qualquer momento.

Nas fotos dos projetos e na galeria dá para adicionar, tirar e mudar a ordem. A primeira foto de cada projeto aparece no cartão da página inicial, e projeto sem foto mostra uma imagem preta escrita "Em breve". Na galeria também dá para editar o filtro, o título e a descrição.

Na Família AEPEC dá para adicionar, editar, excluir e mudar a ordem das pessoas. Cada pessoa pode ter até duas fotos (a segunda é para duplas).

## Estrutura do projeto

```
projeto-ong/
├── app.py             rotas e páginas do site
├── dados.py           tudo que lê e grava no banco de dados
├── schema.sql         tabelas do banco
├── config_site.py     telefone, e-mail, PIX, endereço, Instagram
├── projetos.py        nome e resumo dos projetos
├── equipe_inicial.py  equipe que entra no banco na primeira vez
├── requirements.txt   bibliotecas do Python
├── templates/         páginas HTML
│   ├── partes/        cabeçalho, rodapé e cartão de post
│   └── projetos/      texto completo de cada projeto
└── static/
    ├── css/           estilo do site
    ├── js/            interações do site e do painel
    ├── img/           logo, ícones e fotos
    ├── video/         vídeo institucional
    └── uploads/       fotos enviadas pelo painel
```

## Onde ficam os dados

O banco SQLite fica em `dados/aepec.db`. Ele é criado na primeira vez que o site roda, já com a equipe e as fotos iniciais. As tabelas estão em `schema.sql`:

| Tabela | O que guarda |
|---|---|
| `admin` | e-mail e senha do administrador (a senha é salva como hash) |
| `posts` | posts do Instagram, inclusive os que saíram do site |
| `equipe` e `equipe_fotos` | pessoas da Família AEPEC e as fotos delas |
| `projeto_fotos` | fotos de cada projeto |
| `galeria` | fotos da galeria da página inicial |
| `tentativas_login` | senhas erradas, usadas no bloqueio do login |

As fotos enviadas pelo painel ficam em `static/uploads/`. As pastas `dados/` e `static/uploads/` estão no `.gitignore` e não vão para o GitHub.

## Onde mudar as coisas

| O que | Onde |
|---|---|
| Telefone, e-mail, PIX, endereço, números do Instagram e vídeo | `config_site.py` |
| Texto completo de cada projeto | `templates/projetos/` (um arquivo por projeto) |
| Nome e resumo dos projetos | `projetos.py` |
| Cores do site (claro e escuro) | começo de `static/css/estilo.css` |
| Logo | `static/img/logo.png` e `static/img/logo-360.png` |
| Ícone da aba | `static/img/favicon.ico` |
| Vídeo institucional | `static/video/institucional.mp4` (capa em `static/video/capa.jpg`) |
