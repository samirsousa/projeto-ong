# Site AEPEC - Espaço Pequeno Cidadão

Site feito em Python (Flask) com HTML, CSS, JavaScript e (banco de dados ainda não escolhido)

## Páginas

| `/` | Página inicial |
| `/nos-acompanhe` | Página do Instagram |
| `/familia-aepec` | Página da equipe (Família AEPEC) |
| `/admin/login` | Login do administrador |
| `/admin` | Painel do administrador |

## Acesso do administrador

- E-mail: `admin@aepec.org.br`
- Senha inicial: `aepec2025`

**LEMBRAR DE TROCAR a senha no painel antes de colocar o site no ar.**

Se esquecere a senha, rode no terminal:

```
flask --app app resetar-senha
```

Isso volta o acesso para o e-mail e a senha acima.

## Onde mudar as coisas

| O que | Onde |
|---|---|
| Telefone, e-mail, PIX, endereço, números do Instagram, vídeo do YouTube | `config_site.py` |
| Texto completo de cada projeto | `templates/projetos/` (um arquivo por projeto) |
| Nome e resumo dos projetos | `projetos.py` |
| Fotos dos projetos e da galeria | pelo painel do administrador |
| Equipe da Família AEPEC | pelo painel do administrador (adicionar, editar, excluir e mudar a ordem) |
| Cores do site (claro e escuro) | começo do arquivo `static/css/estilo.css` |
| Logo | `static/img/logo.png` e `static/img/logo-360.png` |
| Ícone da aba | `static/img/favicon.ico` |

## Trocar as fotos

Pelo painel do administrador (`/admin`):

- **Fotos dos projetos:** adicionar, tirar e mudar a ordem. A primeira foto é a do cartão.
- **Galeria:** adicionar, editar (filtro, título, descrição, trocar a foto), tirar e mudar a ordem.
- **Família AEPEC:** foto de cada pessoa.

Projeto sem foto mostra uma imagem preta escrita "Em breve".

O fundo do bloco do vídeo fica em `static/img/fotos/video-capa.jpg`.

## Vídeo institucional

O vídeo fica em `static/video/institucional.mp4` e a capa em `static/video/capa.jpg`.


## Onde ficam os dados

Na pasta `dados/` :

- `posts.json`: posts do Instagram e o histórico
- `admin.json`: e-mail e senha (a senha fica protegida, não dá para ler)
- `equipe.json`: pessoas da Família AEPEC
- `galeria.json` e `fotos_projetos.json`: fotos da galeria e dos projetos

As fotos enviadas pelo painel ficam em `static/uploads/`.
