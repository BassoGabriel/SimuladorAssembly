#instruções específica que precisa estar no código LI


import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

# Funções que serão chamadas ao clicar nos botões
def botao1_clique():
    #messagebox.showinfo("Botão 1", "Você clicou no Botão 1!")
    escolher_e_ler_arquivo()

def botao2_clique():
    messagebox.showinfo("Botão 2", "Você clicou no Botão 2!")

#reconhecimento de arquivos


def escolher_e_ler_arquivo():
    # Cria uma janela oculta do tkinter
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal

    # Abre a caixa de diálogo para escolher um arquivo
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione um arquivo",
        filetypes=[("Assembly Files", "*.asm*")]
    )

    # Verifica se o usuário selecionou um arquivo
    if not caminho_arquivo:
        print("Nenhum arquivo foi selecionado.")
        return

    # Lê o conteúdo do arquivo
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()

    print("Conteúdo do arquivo:")
    print(conteudo)

# Criando a janela principal
janela = tk.Tk()
janela.title("Minha Janela com Botões")
janela.geometry("300x150")  # Largura x Altura

# Criando os botões
botao1 = tk.Button(janela, text="Botão 1", command=botao1_clique)
botao1.pack(pady=10)

botao2 = tk.Button(janela, text="Botão 2", command=botao2_clique)
botao2.pack(pady=10)

janela.mainloop()