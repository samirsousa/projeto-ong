# Site AEPEC - Espaço Pequeno Cidadão

Site institucional da **AEPEC (Associação Espaço Pequeno Cidadão)**, uma ONG de São Gonçalo (RJ) que atende crianças, jovens e famílias com educação no contraturno, alimentação, esporte e informática.

O site apresenta a história e os projetos da ONG, a equipe (Família AEPEC), uma galeria de fotos, os posts do Instagram e as formas de doar. Também tem um painel do administrador onde a equipe da ONG atualiza o conteúdo sem mexer no código.

## Créditos - Time por trás dos códigos

| Função | Nome |
|---|---|
| Coordenador do grupo | Kaleo Accacio Pereira Lemos |
| Programadores | Samir Firmino Martins de Sousa, Guilherme Amorim Pereira de Araujo, Kaleo Accacio Pereira Lemos |
| Professora | Theresa Prado Gondim |
| Monitor | Daniel Oliveira |

## Tecnologias utilizadas

| Tecnologia | Para que serve |
|---|---|
| Python 3 | Linguagem do servidor |
| Flask | Framework que cria as páginas e as rotas do site |
| Jinja | Modelos HTML que recebem os dados do Python |
| SQLite | Banco de dados (um arquivo só, já vem com o Python) |
| Pillow | Reduz e ajusta as fotos enviadas pelo painel |
| HTML, CSS e JavaScript | Visual, modo escuro, menu do celular, filtros e animações |
| Git e GitHub | Controle de versões do código |

## Funcionalidades

- Página inicial com a história, os projetos, a galeria com filtros, o vídeo institucional e as formas de doar (com a chave PIX para copiar)
- Página "Nos Acompanhe" com os posts do Instagram, separados por filtro
- Página "Família AEPEC" com as fotos e a apresentação de cada pessoa da equipe
- Modo claro e modo escuro
- Layout que se adapta do celular ao monitor
- Painel do administrador para:
  - adicionar e tirar posts do Instagram (com histórico e data de inserção)
  - adicionar, editar, excluir e mudar a ordem das pessoas da equipe
  - adicionar, tirar e mudar a ordem das fotos dos projetos e da galeria
  - trocar a senha
- Login protegido: bloqueia por 15 minutos depois de várias senhas erradas

## Páginas

| Endereço | Página |
|---|---|
| `/` | Página inicial |
| `/nos-acompanhe` | Página do Instagram |
| `/familia-aepec` | Página da equipe (Família AEPEC) |
| `/admin/login` | Login do administrador |
| `/admin` | Painel do administrador |

### O que precisa ter instalado

- Python 3.10 ou mais novo
- Git

## Como usar o painel

Entre em `/admin/login` com o e-mail e a senha criados no passo 3. O link de acesso fica no rodapé do site.

- **Posts do Instagram:** cole o link do post, escolha o filtro e o formato e, se quiser, envie uma imagem de capa. O post tirado do site continua no histórico e pode voltar.
- **Fotos dos projetos:** adicionar, tirar e mudar a ordem. A primeira foto é a do cartão.
- **Galeria:** adicionar, editar (filtro, título, descrição e foto), tirar e mudar a ordem.
- **Família AEPEC:** adicionar, editar, excluir e mudar a ordem das pessoas. Cada pessoa pode ter até duas fotos.
- **Segurança:** trocar a senha.

Projeto sem foto mostra uma imagem preta escrita "Em breve".

## Estrutura do projeto

```
projeto-ong/
├── app.py             rotas e páginas do site
├── dados.py           tudo que lê e grava no banco de dados
├── schema.sql         tabelas do banco
├── config_site.py     telefone, e-mail, PIX, endereço, Instagram
├── projetos.py        nome e resumo dos projetos
├── equipe_inicial.py  equipe que vem pronta na primeira vez
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

Os dados ficam no banco SQLite `dados/aepec.db`. Ele é criado sozinho na primeira vez que o site roda, já com a equipe e as fotos iniciais. As tabelas estão descritas em `schema.sql`:

| Tabela | O que guarda |
|---|---|
| `admin` | e-mail e senha do administrador (a senha fica protegida, não dá para ler) |
| `posts` | posts do Instagram e o histórico |
| `equipe` e `equipe_fotos` | pessoas da Família AEPEC e as fotos delas |
| `projeto_fotos` | fotos de cada projeto |
| `galeria` | fotos da galeria da página inicial |
| `tentativas_login` | senhas erradas, para bloquear quem tenta adivinhar |

As fotos enviadas pelo painel ficam em `static/uploads/`. A pasta `dados/` e a pasta `uploads/` não vão para o GitHub.

## Onde mudar as coisas

| O que | Onde |
|---|---|
| Telefone, e-mail, PIX, endereço, números do Instagram, vídeo | `config_site.py` |
| Texto completo de cada projeto | `templates/projetos/` (um arquivo por projeto) |
| Nome e resumo dos projetos | `projetos.py` |
| Cores do site (claro e escuro) | começo do arquivo `static/css/estilo.css` |
| Logo | `static/img/logo.png` e `static/img/logo-360.png` |
| Ícone da aba | `static/img/favicon.ico` |
| Vídeo institucional | `static/video/institucional.mp4` (capa em `static/video/capa.jpg`) |
