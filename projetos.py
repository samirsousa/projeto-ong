# Projetos da AEPEC.

PROJETOS = [
    {"id": "educacional", "selo": "Educação", "cor": "#004aae",
     "nome": "Programa Educacional Complementar - PEC",
     "resumo": "O Programa Educacional Complementar é o programa mais importante da AEPEC. Mais de 680 crianças já foram beneficiadas pelo Programa."},
    {"id": "jovem", "selo": "Juventude", "cor": "#1d4ed8",
     "nome": "Projeto Jovem de Futuro",
     "resumo": "Implantado desde 2001, o Projeto Jovem de Futuro tem por objetivo ampliar o conhecimento dos jovens sobre o mercado de trabalho e a empregabilidade."},
    {"id": "esporte", "selo": "Esporte", "cor": "#d97706",
     "nome": "Projeto Show de Bola",
     "resumo": "O Projeto Show de Bola, é a escolinha de futsal da AEPEC, para crianças e adolescentes de 06 a 15 anos."},
    {"id": "informatica", "selo": "Inclusão Digital", "cor": "#0284c7",
     "nome": "Informática e Cidadania",
     "resumo": "A proposta do curso é democratizar o conhecimento/acesso à informática através da promoção de cursos e oficinas."},
    {"id": "biblioteca", "selo": "Leitura", "cor": "#4338ca",
     "nome": "Biblioteca Comunitária",
     "resumo": "Com cerca de 2.500 títulos, a biblioteca da AEPEC está a serviço da comunidade."},
    {"id": "natal", "selo": "Ação Solidária", "cor": "#b45309",
     "nome": "Campanha Natal com Alegria",
     "resumo": "Todos os anos, a AEPEC mobiliza uma verdadeira rede de solidariedade para promover a campanha “Natal Sem Fome“."},
]

# Fotos que vêm prontas quando site abre.
FOTOS_INICIAIS = {
    "educacional": ["img/fotos/projeto-educacional.jpg", "img/fotos/projeto-educacional-2.jpg",
                    "img/fotos/projeto-educacional-3.jpg"],
    "jovem": ["img/fotos/projeto-jovem.jpg", "img/fotos/projeto-jovem-2.jpg"],
    "esporte": ["img/fotos/projeto-esporte.jpg", "img/fotos/projeto-esporte-2.jpg"],
    "informatica": ["img/fotos/projeto-informatica.jpg"],
    "biblioteca": ["img/fotos/projeto-biblioteca.jpg"],
    "natal": ["img/fotos/projeto-natal.jpg", "img/fotos/projeto-natal-2.jpg"],
}

# Galeria da página inicial quando o site abre
# "tipo" é o filtro: edu (Educação), esporte (Esporte) ou evento (Eventos & Festas).
GALERIA_INICIAL = [
    {"foto": "img/fotos/projeto-educacional.jpg", "tipo": "edu", "titulo": "Programa Educacional Complementar", "texto": ""},
    {"foto": "img/fotos/projeto-biblioteca.jpg", "tipo": "edu", "titulo": "Biblioteca Comunitária", "texto": ""},
    {"foto": "img/fotos/projeto-informatica.jpg", "tipo": "edu", "titulo": "Informática e Cidadania", "texto": ""},
    {"foto": "img/fotos/projeto-jovem.jpg", "tipo": "edu", "titulo": "Projeto Jovem de Futuro", "texto": ""},
    {"foto": "img/fotos/projeto-esporte.jpg", "tipo": "esporte", "titulo": "Projeto Show de Bola", "texto": ""},
    {"foto": "img/fotos/projeto-natal.jpg", "tipo": "evento", "titulo": "Campanha Natal com Alegria", "texto": ""},
    {"foto": "img/fotos/projeto-educacional-2.jpg", "tipo": "edu", "titulo": "Programa Educacional Complementar", "texto": ""},
    {"foto": "img/fotos/projeto-educacional-3.jpg", "tipo": "edu", "titulo": "Programa Educacional Complementar", "texto": ""},
    {"foto": "img/fotos/projeto-jovem-2.jpg", "tipo": "edu", "titulo": "Projeto Jovem de Futuro", "texto": ""},
    {"foto": "img/fotos/projeto-esporte-2.jpg", "tipo": "esporte", "titulo": "Projeto Show de Bola", "texto": ""},
    {"foto": "img/fotos/projeto-natal-2.jpg", "tipo": "evento", "titulo": "Campanha Natal com Alegria", "texto": ""},
]
