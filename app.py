from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from services.suggestions import gerar_sugestao
from services.classifier import classificar_email
import PyPDF2
import os

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remetente = db.Column(db.String(120))
    assunto = db.Column(db.String(255))
    conteudo = db.Column(db.Text)
    categoria = db.Column(db.String(100))

@app.route('/')
def index():
    emails = Email.query.all()
    return render_template('index.html', emails=emails, sugerir=gerar_sugestao)

@app.route('/processar-email', methods=['POST'])
def processar_email():
    texto_final = ""

    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename != "":
        filename = secure_filename(arquivo.filename)

        if filename.lower().endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(arquivo)
            for page in pdf_reader.pages:
                texto_final += page.extract_text()

        elif filename.lower().endswith(".txt"):
            texto_final = arquivo.read().decode("utf-8")

    texto_digitado = request.form.get("conteudo")
    if texto_digitado:
        texto_final += "\n" + texto_digitado

    if texto_final.strip() == "":
        return "Nenhum conteúdo enviado!", 400
    categoria = classificar_email("Arquivo enviado", texto_final)

    sugestao = gerar_sugestao(categoria)

    novo = Email(
        remetente="(Upload)",
        assunto="Processado automaticamente",
        conteudo=texto_final,
        categoria=categoria
    )

    db.session.add(novo)
    db.session.commit()

    return render_template(
        "resultado.html",
        categoria=categoria,
        sugestao=sugestao,
        conteudo=texto_final
    )

@app.route('/salvar-email', methods=['POST'])
def salvar_email():
    remetente = request.form.get('remetente')
    assunto = request.form.get('assunto')
    conteudo = request.form.get('conteudo')

    categoria = classificar_email(assunto, conteudo)

    novo = Email(
        remetente=remetente,
        assunto=assunto,
        conteudo=conteudo,
        categoria=categoria
    )

    db.session.add(novo)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
