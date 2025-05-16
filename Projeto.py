import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# --- Leitura do arquivo .asm ---
def ler_codigo_assembly(caminho_arquivo):
    instrucoes = []
    rotulos = {}
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            linha_index = 0
            for linha in arquivo:
                linha = linha.strip()
                if not linha or linha.startswith('#') or linha.startswith('.'):
                    continue
                while ':' in linha:
                    partes = linha.split(':', 1)
                    rotulo = partes[0].strip()
                    rotulos[rotulo] = linha_index
                    linha = partes[1].strip()
                if linha:
                    instrucoes.append(linha)
                    linha_index += 1
    except FileNotFoundError:
        print("Arquivo nao encontrado. Verifique o caminho.")
    return instrucoes, rotulos

# --- Leitura do arquivo de configuração ---
def ler_configuracao_cpu(caminho_arquivo):
    config = {
        "clock_ciclo_ms": 1,
        "tempo_tipo_I": 1,
        "tempo_tipo_R": 1,
        "tempo_tipo_J": 1
    }
    try:
        with open(caminho_arquivo, "r") as f:
            for linha in f:
                if "=" in linha:
                    chave, valor = linha.strip().split("=")
                    if chave in config:
                        config[chave] = int(valor)
    except:
        print("Arquivo de configuração não encontrado. Usando valores padrão.")
    return config

# --- Parser das instruções ---
def identificar_instrucao(instrucao):
    partes = instrucao.replace(',', '').split()
    if not partes:
        return None
    opcode = partes[0].lower()
    tipo_r = {'add', 'sub'}
    tipo_i = {'lw', 'sw', 'beq'}
    tipo_j = {'j'}
    if opcode in tipo_r and len(partes) == 4:
        return {
            'tipo': 'R',
            'opcode': opcode,
            'destino': partes[1],
            'origem1': partes[2],
            'origem2': partes[3]
        }
    elif opcode in tipo_i and len(partes) >= 3:
        return {
            'tipo': 'I',
            'opcode': opcode,
            'destino': partes[1],
            'origem': partes[2],
            'imediato': partes[3] if len(partes) > 3 else '0'
        }
    elif opcode in tipo_j and len(partes) == 2:
        return {
            'tipo': 'J',
            'opcode': opcode,
            'label': partes[1]
        }
    return None

# --- Mapeamento de registradores ---
mapa_registradores = {
    '$zero': 0, '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
    '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15, '$t8': 24, '$t9': 25
}

# --- Conversões ---
def to_bin(numero, bits):
    return format(numero, f'0{bits}b')

def instrucao_tipo_r_para_bin(instrucao):
    opcode = '000000'
    rs = to_bin(mapa_registradores.get(instrucao['origem1'], 0), 5)
    rt = to_bin(mapa_registradores.get(instrucao['origem2'], 0), 5)
    rd = to_bin(mapa_registradores.get(instrucao['destino'], 0), 5)
    shamt = '00000'
    funct_map = {'add': '100000', 'sub': '100010'}
    funct = funct_map.get(instrucao['opcode'], '000000')
    binario = opcode + rs + rt + rd + shamt + funct
    hexadecimal = f"0x{int(binario, 2):08X}"
    return binario, hexadecimal

def instrucao_tipo_i_para_bin(instrucao):
    opcode_map = {'lw': '100011', 'sw': '101011', 'beq': '000100'}
    opcode = opcode_map.get(instrucao['opcode'], '000000')
    rs = to_bin(mapa_registradores.get(instrucao['origem'], 0), 5)
    rt = to_bin(mapa_registradores.get(instrucao['destino'], 0), 5)
    try:
        imediato = int(instrucao.get('imediato', '0'))
    except:
        imediato = 0
    imm = to_bin(imediato & 0xFFFF, 16)
    binario = opcode + rs + rt + imm
    hexadecimal = f"0x{int(binario, 2):08X}"
    return binario, hexadecimal

def instrucao_tipo_j_para_bin(instrucao, rotulos):
    opcode = '000010'
    label = instrucao.get('label', '')
    endereco = rotulos.get(label, 0)
    endereco_jump = endereco
    endereco_bin = to_bin(endereco_jump, 26)
    binario = opcode + endereco_bin
    hexadecimal = f"0x{int(binario, 2):08X}"
    return binario, hexadecimal

# --- Dados do simulador ---
estado_simulador = {
    'codigo': [],
    'rotulos': {},
    'PC': 0,
    'registradores': {},
    'memoria': {},
    'config': {},
    'tempo_total': 0
}

# --- Execução passo a passo ---
def executar_proxima_instrucao(saida_text):
    estado = estado_simulador
    PC = estado['PC']
    if PC >= len(estado['codigo']):
        saida_text.insert(tk.END, "Fim da execução.\n")
        mostrar_estado_final(saida_text)
        return
    linha = estado['codigo'][PC]
    instrucao = identificar_instrucao(linha)
    if instrucao:
        saida_text.insert(tk.END, f"[PC = {PC*4}] Executando: {linha}\n")
        estado['PC'] = executar(instrucao, estado['registradores'], estado['memoria'], estado['rotulos'], PC, saida_text)
        tipo = instrucao['tipo']
        tempo_instrucao = estado['config'][f"tempo_tipo_{tipo}"]
        estado['tempo_total'] += tempo_instrucao
        saida_text.insert(tk.END, f"Tempo da instrução: {tempo_instrucao} ciclos\n")
        saida_text.insert(tk.END, "-"*40 + "\n")

# --- Execução completa ---
def executar_tudo(saida_text):
    while estado_simulador['PC'] < len(estado_simulador['codigo']):
        executar_proxima_instrucao(saida_text)

# --- Mostrar estado final ---
def mostrar_estado_inicial(saida_text):
    saida_text.insert(tk.END, "--- Registradores Iniciais ---\n")
    todos_registradores = {
        '$zero': 0, '$at': 1, '$v0': 2, '$v1': 3,
        '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
        '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
        '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
        '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
        '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
        '$t8': 24, '$t9': 25, '$k0': 26, '$k1': 27,
        '$gp': 28, '$sp': 29, '$fp': 30, '$ra': 31
    }
    for nome, numero in todos_registradores.items():
        val = estado_simulador['registradores'].get(nome, 0)
        saida_text.insert(tk.END, f"{nome:>5} ({numero:>2}): 0x{val:08X}\n")

    saida_text.insert(tk.END, "\n--- Memória Inicial ---\n")
    for endereco, valor in estado_simulador['memoria'].items():
        saida_text.insert(tk.END, f"{endereco:>10}: 0x{valor:08X}\n")
    
    saida_text.insert(tk.END, "-" * 50 + "\n\n")



# --- Carregar programa ---
def carregar_programa(saida_text):
    caminho_asm = filedialog.askopenfilename(filetypes=[("Assembly Files", "*.asm")])
    if not caminho_asm:
        return
    try:
        codigo, rotulos = ler_codigo_assembly(caminho_asm)
        config = ler_configuracao_cpu("config_cpu.txt")
        registradores = {
            '$t0': 0, '$t1': 0, '$t2': 0, '$t3': 0, '$t4': 0,
            '$t5': 0, '$t6': 0, '$t7': 0, '$t8': 0, '$t9': 0
        }
        memoria = {'valor1': 5, 'valor2': 10, 'resultado': 0}
        estado_simulador.update({
            'codigo': codigo,
            'rotulos': rotulos,
            'PC': 0,
            'registradores': registradores,
            'memoria': memoria,
            'config': config,
            'tempo_total': 0
        })
        saida_text.delete(1.0, tk.END)
        saida_text.insert(tk.END, "Programa carregado com sucesso.\nClique em 'Próxima Instrução' ou 'Executar Tudo' para iniciar.\n")
        mostrar_estado_inicial(saida_text)

    except Exception as e:
        messagebox.showerror("Erro", str(e))

# --- Resto do código (função executar igual ao original) ---
def executar(instrucao, registradores, memoria, rotulos, pc_atual, saida_text):
    tipo = instrucao['tipo']
    opcode = instrucao['opcode']
    proximo_pc = pc_atual + 1

    if tipo == 'R':
        rd = instrucao['destino']
        rs = instrucao['origem1']
        rt = instrucao['origem2']
        if opcode == 'add':
            registradores[rd] = registradores[rs] + registradores[rt]
        elif opcode == 'sub':
            registradores[rd] = registradores[rs] - registradores[rt]
        saida_text.insert(tk.END, f"{opcode.upper()} {rd} = {registradores[rd]}\n")
        binario, hexadecimal = instrucao_tipo_r_para_bin(instrucao)
        saida_text.insert(tk.END, f"Binario: {binario}\nHex:     {hexadecimal}\n")

    elif tipo == 'I':
        rt = instrucao['destino']
        rs = instrucao['origem']
        if opcode == 'lw':
            if rs in memoria:
                registradores[rt] = memoria[rs]
                saida_text.insert(tk.END, f"LW {rt} <- MEM[{rs}] = {registradores[rt]}\n")
        elif opcode == 'sw':
            if rs in memoria:
                memoria[rs] = registradores[rt]
                saida_text.insert(tk.END, f"SW MEM[{rs}] <- {rt} = {memoria[rs]}\n")
        elif opcode == 'beq':
            if registradores[rt] == registradores[rs]:
                label = instrucao['imediato']
                if label in rotulos:
                    saida_text.insert(tk.END, f"BEQ: {rt} == {rs}, saltando para {label}\n")
                    proximo_pc = rotulos[label]
                else:
                    saida_text.insert(tk.END, f"Erro: label '{label}' não encontrado.\n")
            else:
                saida_text.insert(tk.END, f"BEQ: {rt} != {rs}, nao salta.\n")
        binario, hexadecimal = instrucao_tipo_i_para_bin(instrucao)
        saida_text.insert(tk.END, f"Binario: {binario}\nHex:     {hexadecimal}\n")

    elif tipo == 'J':
        label = instrucao['label']
        if label in rotulos:
            saida_text.insert(tk.END, f"J: saltando para {label}\n")
            proximo_pc = rotulos[label]
        else:
            saida_text.insert(tk.END, f"Erro: label '{label}' não encontrado.\n")
        binario, hexadecimal = instrucao_tipo_j_para_bin(instrucao, rotulos)
        saida_text.insert(tk.END, f"Binario: {binario}\nHex:     {hexadecimal}\n")

    return proximo_pc

# --- Janela principal ---
janela = tk.Tk()
janela.title("Simulador Assembly")
janela.geometry("800x600")

frame_topo = tk.Frame(janela)
frame_topo.pack(pady=10)

saida_text = scrolledtext.ScrolledText(janela, width=95, height=30)
saida_text.pack(padx=10, pady=10)

botao_carregar = tk.Button(frame_topo, text="Carregar .ASM", command=lambda: carregar_programa(saida_text))
botao_carregar.pack(side=tk.LEFT, padx=5)

botao_proxima = tk.Button(frame_topo, text="Próxima Instrução", command=lambda: executar_proxima_instrucao(saida_text))
botao_proxima.pack(side=tk.LEFT, padx=5)

botao_executar_tudo = tk.Button(frame_topo, text="Executar Tudo", command=lambda: executar_tudo(saida_text))
botao_executar_tudo.pack(side=tk.LEFT, padx=5)

janela.mainloop()