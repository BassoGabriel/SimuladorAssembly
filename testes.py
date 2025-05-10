import tkinter as tk
import pandas as pd
from pandastable import Table

#criando dados de exemplo
dados = {
    "nome": ["GABRIEL", "BIANCA", "AUGUSTO"],
    "idade": [28, 28, 1],   
}

df = pd.DataFrame(dados)

# Criando a janela principal
janela = tk.Tk()
janela.title("TABELA COM PANDAS")

# Criando o frame para a tabela
frame_tabela = tk.Frame(janela)
frame_tabela.pack(fill="both", expand=True)

tabela = Table(frame_tabela, dataframe=df, showtoolbar=True, showstatusbar=True)
tabela.show()

janela.mainloop()