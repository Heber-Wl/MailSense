from services.model import carregar_modelo
import re

vectorizer, modelo = carregar_modelo()

def regras_simples(texto):
    texto = texto.lower().strip()

    improdutivo_keywords = [
        "bom dia", "boa tarde", "boa noite",
        "parabéns", "feliz aniversário",
        "agradeço", "agradecimento", "obrigado", "obrigada", "obg",
        "promoção", "promocao", "oferta", "desconto",
        "shopee", "shoppe",
        "desabafo", "desabafar",
        "felicitações", "felicitacoes",
        "perder tempo",
        "teste"
    ]

    produtivo_keywords = [
        "erro", "bug", "falha",
        "não funciona", "nao funciona",
        "problema", "acesso", "suporte", "sistema",
        "pendente", "chamado",
        "solicito", "solicitação", "solicitacao",
        "preciso", "necessito", "urgente",
        "como faço", "como faco",
        "dúvida", "duvida"
    ]

    if any(p in texto for p in improdutivo_keywords):
        return "Improdutivo"
    
    if any(p in texto for p in produtivo_keywords):
        return "Produtivo"

    return None

def texto_sem_sentido(texto):
    t = texto.lower().strip()

    palavras = t.split()

    if len(palavras) <= 3:
        return True

    sem_vogal = sum(1 for p in palavras if not any(v in p for v in "aeiou"))
    if sem_vogal / len(palavras) >= 0.7:
        return True

    palavras_reais = [
        "erro","problema","acesso","urgente","solicito","sistema",
        "falha","bug","nao","não","duvida", "como","chamado","sac"
    ]

    if all(len(p) <= 4 for p in palavras):
        if not any(real in t for real in palavras_reais):
            return True

    if re.fullmatch(r"[bcdfghjklmnpqrstvwxyz ]+", t):
        return True

    if t in ["asdf", "asdfgh", "qwerty", "zxcvb", "hahaha", "kkkk", "kkkkkk"]:
        return True

    return False

def classificar_email(assunto, conteudo):
    texto = f"{assunto} {conteudo}".strip().lower()

    regra = regras_simples(texto)
    if regra:
        return regra

    if texto_sem_sentido(texto):
        return "Improdutivo"

    X = vectorizer.transform([texto])
    categoria = modelo.predict(X)[0]

    return categoria

def prever_categoria(texto_completo):
    X = vectorizer.transform([texto_completo])
    return modelo.predict(X)[0]
