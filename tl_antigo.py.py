import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import hashlib
import sqlite3
import random
import string
import io
import os

# Configuração do banco de dados SQLite
db_file = "usuarios.db"
conexao = sqlite3.connect(db_file)
cursor = conexao.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  usuario TEXT UNIQUE NOT NULL,
                  senha TEXT NOT NULL)''')
conexao.commit()
print("Tabela de usuários criada ou já existe.")  # Verificação da criação da tabela

# Verificar se o arquivo do banco de dados foi criado
if os.path.exists(db_file):
    print(f"O arquivo do banco de dados foi encontrado em: {os.path.abspath(db_file)}")
else:
    print("O arquivo do banco de dados não foi encontrado.")

# Função para gerar o hash da senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

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

def gerar_captcha_imagem():
    global imagem_certa
    imagem_certa = gerar_texto_captcha()
    
    img_buffer = io.BytesIO()
    gerar_imagem_captcha(imagem_certa).save(img_buffer, format="PNG")
    img_buffer.seek(0)
    img_tk = ImageTk.PhotoImage(Image.open(img_buffer))
    
    label_captcha.config(image=img_tk)
    label_captcha.image = img_tk

def verificar_captcha():
    if entrada_captcha.get() == imagem_certa:
        messagebox.showinfo("CAPTCHA", "Você não é um robô!")
        return True
    else:
        messagebox.showerror("CAPTCHA", "Texto incorreto. Tente novamente.")
        return False

# Função para verificar login no banco de dados
def verificar_login():
    if not verificar_captcha():
        return
    
    usuario = entrada_usuario.get()
    senha = hash_senha(entrada_senha.get())

    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    if cursor.fetchone():
        messagebox.showinfo("Login", "Login bem-sucedido!")
        entrada_usuario.delete(0, tk.END)
        entrada_senha.delete(0, tk.END)
    else:
        messagebox.showerror("Login", "Usuário ou senha incorretos.")

# Função para registrar um novo usuário no banco de dados
def registrar_usuario():
    def salvar_usuario():
        novo_usuario = entrada_novo_usuario.get()
        nova_senha = hash_senha(entrada_nova_senha.get())
        
        if not novo_usuario or not nova_senha:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return
        
        try:
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (novo_usuario, nova_senha))
            conexao.commit()
            messagebox.showinfo("Registro", f"Usuário '{novo_usuario}' registrado com sucesso!")
            janela_registro.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário já existe.")

    janela_registro = tk.Toplevel(janela)
    janela_registro.title("Registrar Novo Usuário")

    tk.Label(janela_registro, text="Novo Usuário:").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(janela_registro, text="Nova Senha:").grid(row=1, column=0, padx=10, pady=10)

    entrada_novo_usuario = tk.Entry(janela_registro)
    entrada_novo_usuario.grid(row=0, column=1, padx=10, pady=10)

    entrada_nova_senha = tk.Entry(janela_registro, show='*')
    entrada_nova_senha.grid(row=1, column=1, padx=10, pady=10)

    botao_salvar = tk.Button(janela_registro, text="Salvar", command=salvar_usuario)
    botao_salvar.grid(row=2, columnspan=2, pady=10)

# Função para recuperar senha (esboço)
def recuperar_senha():
    messagebox.showinfo("Recuperar Senha", "Funcionalidade em desenvolvimento.")

# Criação da janela principal
janela = tk.Tk()
janela.title("Tela de Login")

# Definindo a tela cheia
janela.attributes('-fullscreen', True)
janela.bind('<Escape>', lambda event: janela.attributes('-fullscreen', False))

# Carregar a imagem de fundo usando caminho relativo
imagem_fundo = Image.open("Prancheta.jpg")  # Usando caminho relativo para a imagem
imagem_fundo = imagem_fundo.resize((janela.winfo_screenwidth(), janela.winfo_screenheight()), Image.LANCZOS)
foto_fundo = ImageTk.PhotoImage(imagem_fundo)

# Criar um Label para a imagem de fundo
label_fundo = tk.Label(janela, image=foto_fundo)
label_fundo.place(x=0, y=0, relwidth=1, relheight=1)

# Configuração do layout
frame = tk.Frame(janela, bg='#4e4e4e', bd=5, relief='raised')
frame.place(relx=0.5, rely=0.5, anchor='center')  # Centraliza o frame

# Labels sem cor de fundo
tk.Label(frame, text="Usuário:", bg='#4e4e4e', fg='white').grid(row=0, column=0, padx=10, pady=10)
tk.Label(frame, text="Senha:", bg='#4e4e4e', fg='white').grid(row=1, column=0, padx=10, pady=10)

entrada_usuario = tk.Entry(frame)
entrada_usuario.grid(row=0, column=1, padx=10, pady=10)

entrada_senha = tk.Entry(frame, show='*')
entrada_senha.grid(row=1, column=1, padx=10, pady=10)

botao_login = tk.Button(frame, text="Login", command=verificar_login)
botao_login.grid(row=2, columnspan=2, pady=10)

botao_registrar = tk.Button(frame, text="Registrar Novo Usuário", command=registrar_usuario)
botao_registrar.grid(row=3, columnspan=2, pady=10)

botao_recuperar = tk.Button(frame, text="Recuperar Senha", command=recuperar_senha)
botao_recuperar.grid(row=7, columnspan=2, pady=10)

# Frame para o CAPTCHA (dentro do frame principal)
label_captcha = tk.Label(frame)
label_captcha.grid(row=4, columnspan=2, pady=10)

entrada_captcha = tk.Entry(frame)
entrada_captcha.grid(row=5, columnspan=2, pady=10)

botao_verificar_captcha = tk.Button(frame, text="Verificar CAPTCHA", command=verificar_captcha)
botao_verificar_captcha.grid(row=6, columnspan=2, pady=10)

# Gerar a imagem do CAPTCHA ao iniciar
gerar_captcha_imagem()

# Iniciar o loop da interface gráfica
janela.mainloop()

# Fechar a conexão com o banco de dados ao final
conexao.close()
