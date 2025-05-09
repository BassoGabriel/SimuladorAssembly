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
janela.title("SIMULADOR DE ASSEMBLY")
janela.configure(bg="black")  # Cor de fundo da janela
janela.geometry("1024x600")  # Largura x Altura

# Criando os botões
botao1 = tk.Button(janela, text="LOAD FILE", command=botao1_clique)
botao1.place(x=10, y=0, width=70, height=30) 

botao2 = tk.Button(janela, text="NEXT INSTRUCTION", command=botao2_clique)
botao2.place(x=90, y=0, width=120, height=30)  

janela.mainloop()