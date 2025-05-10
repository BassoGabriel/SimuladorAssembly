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
                if linha.endswith(':'):
                    rotulo = linha[:-1]
                    rotulos[rotulo] = linha_index
                else:
                    instrucoes.append(linha)
                    linha_index += 1
    except FileNotFoundError:
        print("Arquivo nao encontrado. Verifique o caminho.")
    return instrucoes, rotulos

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
            'imediato': partes[3] if len(partes) > 3 else None
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

# --- Execução de instruções ---
def executar(instrucao, registradores, memoria, rotulos, pc_atual):
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
        print(f"{opcode.upper()} {rd} = {registradores[rd]}")
        binario, hexadecimal = instrucao_tipo_r_para_bin(instrucao)
        print(f"Binario: {binario}")
        print(f"Hex:     {hexadecimal}")

    elif tipo == 'I':
        rt = instrucao['destino']
        rs = instrucao['origem']
        if opcode == 'lw':
            if rs in memoria:
                registradores[rt] = memoria[rs]
                print(f"LW {rt} <- MEM[{rs}] = {registradores[rt]}")
        elif opcode == 'sw':
            if rs in memoria:
                memoria[rs] = registradores[rt]
                print(f"SW MEM[{rs}] <- {rt} = {memoria[rs]}")
        elif opcode == 'beq':
            if registradores[rt] == registradores[rs]:
                label = instrucao['imediato']
                if label in rotulos:
                    print(f"BEQ: {rt} == {rs}, saltando para {label}")
                    proximo_pc = rotulos[label]
                else:
                    print(f"Erro: label '{label}' não encontrado.")
            else:
                print(f"BEQ: {rt} != {rs}, nao salta.")

    elif tipo == 'J':
        label = instrucao['label']
        if label in rotulos:
            print(f"J: saltando para {label}")
            proximo_pc = rotulos[label]
        else:
            print(f"Erro: label '{label}' não encontrado.")

    return proximo_pc

# --- Inicializações ---
registradores = {
    '$t0': 0, '$t1': 0, '$t2': 0, '$t3': 0, '$t4': 0,
    '$t5': 0, '$t6': 0, '$t7': 0, '$t8': 0, '$t9': 0
}
memoria = {
    'valor1': 5,
    'valor2': 10,
    'resultado': 0
}

# --- Caminho do .asm ---
caminho = r'C:\Users\glisb\OneDrive\Documentos\Facul\Arquitetura e Organização de Computadores\main.asm'

# --- Leitura e execução ---
codigo, rotulos = ler_codigo_assembly(caminho)
PC = 0
tempo_total = 0
ciclo_por_instrucao = 1

print("\n--- Execucao passo a passo ---\n")
while PC < len(codigo):
    linha = codigo[PC]
    instrucao = identificar_instrucao(linha)
    if instrucao:
        print(f"[PC = {PC*4}] Executando: {linha}")
        PC = executar(instrucao, registradores, memoria, rotulos, PC)
        tempo_total += ciclo_por_instrucao
    else:
        PC += 1

# --- Resultado final ---
print("\n--- Estado final dos registradores ---")
for reg, val in registradores.items():
    print(f"{reg}: {val}")

print("\n--- Estado final da memoria ---")
for var, val in memoria.items():
    print(f"{var}: {val}")

print(f"\nTempo total de execucao (em ciclos): {tempo_total}")
