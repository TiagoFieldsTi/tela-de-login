from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import string
import io
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # A chave secreta para usar o sistema de flash messages

# Configuração do banco de dados SQLite
db_file = "usuarios.db"

# Função para gerar uma string aleatória para o CAPTCHA
def gerar_texto_captcha(tamanho=6):
    letras_numeros = string.ascii_letters + string.digits
    return ''.join(random.choice(letras_numeros) for _ in range(tamanho))

# Função para gerar imagem CAPTCHA colorida com texto aleatório
def gerar_imagem_captcha(texto):
    largura, altura = 150, 60
    imagem = Image.new("RGB", (largura, altura), (255, 255, 255))
    draw = ImageDraw.Draw(imagem)
    font = ImageFont.load_default()

    for i, char in enumerate(texto):
        x = 10 + i * 20 + random.randint(-5, 5)
        y = random.randint(5, 15)
        cor_texto = (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150))
        draw.text((x, y), char, fill=cor_texto, font=font)
    
    for _ in range(5):
        start = (random.randint(0, largura), random.randint(0, altura))
        end = (random.randint(0, largura), random.randint(0, altura))
        cor_linha = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
        draw.line([start, end], fill=cor_linha, width=2)
    
    return imagem

# Função para verificar login no banco de dados
def verificar_login(usuario, senha):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], senha):  # Comparar senha usando o hash
        return True
    else:
        return False

# Função para registrar um novo usuário no banco de dados
def registrar_usuario(usuario, senha):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, generate_password_hash(senha)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Rota para a página inicial (login)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        captcha = request.form["captcha"]

        if verificar_login(usuario, senha):
            flash("Login bem-sucedido!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha incorretos.", "danger")

    return render_template("index.html")

# Rota para o dashboard (página após login)
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# Rota para registrar um novo usuário
@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if registrar_usuario(usuario, senha):
            flash(f"Usuário '{usuario}' registrado com sucesso!", "success")
            return redirect(url_for("index"))
        else:
            flash("Erro ao registrar o usuário. O nome de usuário pode já existir.", "danger")

    return render_template("registrar.html")

# Gerar CAPTCHA para a tela de login
@app.route("/captcha")
def captcha():
    texto_captcha = gerar_texto_captcha()
    img = gerar_imagem_captcha(texto_captcha)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io.read(), 200, {'Content-Type': 'image/png'}

if __name__ == "__main__":
    app.run(debug=True)
