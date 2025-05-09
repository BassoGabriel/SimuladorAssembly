#instruções específica que precisa estar no código LI


#reconhecimento de arquivos
import tkinter as tk
from tkinter import filedialog

def escolher_e_ler_arquivo():
    # Cria uma janela oculta do tkinter
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal

    # Abre a caixa de diálogo para escolher um arquivo
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione um arquivo",
        filetypes=[("Todos os arquivos", "*.*"), ("Arquivos de texto", "*.txt")]
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

escolher_e_ler_arquivo()


