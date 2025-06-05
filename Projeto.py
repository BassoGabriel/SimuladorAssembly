import re

# --- Leitura do arquivo .asm ---
def ler_codigo_assembly(caminho_arquivo):
    instrucoes = []
    rotulos = {}
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            linha_index = 0
            for linha in arquivo:
                linha = linha.strip()
                if not linha or linha.startswith('#') or linha.startswith('.') or linha.startswith("Config_CPU"):
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
        print("Arquivo não encontrado.")
    return instrucoes, rotulos

# --- Leitura da linha de configuração dentro do .asm ---
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
                linha = linha.strip()
                if linha.startswith("Config_CPU"):
                    match = re.search(r"Config_CPU=\[\s*(\d+)(GHZ|MHZ),\s*I=(\d+),\s*J=(\d+),\s*R=(\d+)\s*\]", linha, re.IGNORECASE)
                    if match:
                        freq_valor = int(match.group(1))
                        freq_unidade = match.group(2).upper()
                        config["tempo_tipo_I"] = int(match.group(3))
                        config["tempo_tipo_J"] = int(match.group(4))
                        config["tempo_tipo_R"] = int(match.group(5))

                        ciclos_por_segundo = freq_valor * (1_000_000_000 if freq_unidade == "GHZ" else 1_000_000)
                        config["clock_ciclo_ms"] = 1000 / ciclos_por_segundo
                        print("CLOCK por ciclo:", config["clock_ciclo_ms"])
    except:
        print("Erro ao ler configuração. Usando padrão.")
    return config

# --- Mapeamento de registradores ---
mapa_registradores = {
    '$zero': 0, '$at': 1, '$v0': 2, '$v1': 3,
    '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
    '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
    '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
    '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
    '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
    '$t8': 24, '$t9': 25, '$k0': 26, '$k1': 27,
    '$gp': 28, '$sp': 29, '$fp': 30, '$ra': 31
}

# --- Parser de instruções ---
def identificar_instrucao(instrucao):
    partes = instrucao.replace(',', '').replace('(', ' ').replace(')', '').split()
    if not partes:
        return None
    opcode = partes[0].lower()
    tipo_r = {'add', 'sub'}
    tipo_i = {'lw', 'sw', 'beq'}
    tipo_j = {'j'}
    if opcode in tipo_r and len(partes) == 4:
        return {
            'tipo': 'R', 'opcode': opcode,
            'destino': partes[1], 'origem1': partes[2], 'origem2': partes[3]
        }
    elif opcode in tipo_i and len(partes) >= 3:
        return {
            'tipo': 'I', 'opcode': opcode,
            'destino': partes[1], 'origem': partes[2],
            'imediato': partes[3] if len(partes) > 3 else '0'
        }
    elif opcode in tipo_j and len(partes) == 2:
        return {
            'tipo': 'J', 'opcode': opcode,
            'label': partes[1]
        }
    return None

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
        imediato = int(instrucao['imediato'])
    except ValueError:
        imediato = 0
    imm = to_bin(imediato & 0xFFFF, 16)
    binario = opcode + rs + rt + imm
    hexadecimal = f"0x{int(binario, 2):08X}"
    return binario, hexadecimal

def instrucao_tipo_j_para_bin(instrucao, rotulos):
    opcode = '000010'
    endereco = rotulos.get(instrucao.get('label', ''), 0)
    endereco_bin = to_bin(endereco, 26)
    binario = opcode + endereco_bin
    hexadecimal = f"0x{int(binario, 2):08X}"
    return binario, hexadecimal

# --- Execução de instruções ---
def executar(instrucao, registradores, memoria, rotulos, pc_atual):
    tipo = instrucao['tipo']
    opcode = instrucao['opcode']
    proximo_pc = pc_atual + 1

    if tipo == 'R':
        rd, rs, rt = instrucao['destino'], instrucao['origem1'], instrucao['origem2']
        if opcode == 'add':
            registradores[rd] = registradores[rs] + registradores[rt]
        elif opcode == 'sub':
            registradores[rd] = registradores[rs] - registradores[rt]

    elif tipo == 'I':
        rt = instrucao['destino']
        rs = instrucao['origem']
        if opcode in {'lw', 'sw'}:
            try:
                offset = int(instrucao['imediato'])
            except ValueError:
                offset = 0
            base = registradores.get(rs, 0)
            endereco = base + offset
            endereco_hex = f"0x{endereco:08X}"
            if opcode == 'lw':
                registradores[rt] = memoria.get(endereco_hex, 0)
            elif opcode == 'sw':
                memoria[endereco_hex] = registradores[rt]
        elif opcode == 'beq':
            if registradores[rt] == registradores[rs]:
                label = instrucao['imediato']
                if label in rotulos:
                    proximo_pc = rotulos[label]

    elif tipo == 'J':
        label = instrucao['label']
        if label in rotulos:
            proximo_pc = rotulos[label]

    return proximo_pc

# --- Execução completa ---
def executar_tudo(estado):
    saida = []
    while estado['PC'] < len(estado['codigo']):
        linha = estado['codigo'][estado['PC']]
        instrucao = identificar_instrucao(linha)
        if instrucao:
            etapa = {
                'pc': estado['PC'] * 4,
                'linha': linha,
                'tempo_instrucao': estado['config'][f"tempo_tipo_{instrucao['tipo']}"],
                'registradores': estado['registradores'].copy(),
                'memoria': estado['memoria'].copy()
            }
            tipo = instrucao['tipo']
            if tipo == 'R':
                etapa['binario'], etapa['hex'] = instrucao_tipo_r_para_bin(instrucao)
            elif tipo == 'I':
                etapa['binario'], etapa['hex'] = instrucao_tipo_i_para_bin(instrucao)
            elif tipo == 'J':
                etapa['binario'], etapa['hex'] = instrucao_tipo_j_para_bin(instrucao, estado['rotulos'])

            estado['tempo_total'] += etapa['tempo_instrucao']
            estado['PC'] = executar(instrucao, estado['registradores'], estado['memoria'], estado['rotulos'], estado['PC'])
            saida.append(etapa)
        else:
            estado['PC'] += 1

    return {
        'etapas': saida,
        'registradores_finais': estado['registradores'],
        'memoria_final': estado['memoria'],
        'tempo_total': estado['tempo_total'],
        'tempo_total_ms': estado['tempo_total'] * estado['config']['clock_ciclo_ms']
    }

# --- Execução local para testes ---
if __name__ == "__main__":
    caminho = "main.asm"
    codigo, rotulos = ler_codigo_assembly(caminho)
    config = ler_configuracao_cpu(caminho)

    estado = {
        'codigo': codigo,
        'rotulos': rotulos,
        'PC': 0,
        'registradores': {
            '$zero': 0, '$at': 0, '$v0': 0, '$v1': 0,
            '$a0': 0, '$a1': 0, '$a2': 0, '$a3': 0,
            '$t0': 0, '$t1': 0, '$t2': 0, '$t3': 0,
            '$t4': 0, '$t5': 0, '$t6': 0, '$t7': 0,
            '$s0': 0, '$s1': 0, '$s2': 0, '$s3': 0,
            '$s4': 0, '$s5': 0, '$s6': 0, '$s7': 0,
            '$t8': 0, '$t9': 0, '$k0': 0, '$k1': 0,
            '$gp': 0, '$sp': 0, '$fp': 0, '$ra': 0
        },
        'memoria': {
            '0x00000000': 5, '0x00000004': 10, '0x00000008': 0
        },
        'config': config,
        'tempo_total': 0
    }

    estado['registradores']['$s0'] = 0  # base para acessar memória

    resultado = executar_tudo(estado)
    for etapa in resultado['etapas']:
        print(f"[PC={etapa['pc']}] {etapa['linha']} - {etapa['binario']} ({etapa['hex']}) - Tempo: {etapa['tempo_instrucao']} ciclos")

    print("\n--- Estado final dos registradores ---")
    for reg, val in resultado['registradores_finais'].items():
        print(f"{reg}: {val}")

    print("\n--- Estado final da memória ---")
    for var, val in resultado['memoria_final'].items():
        print(f"{var}: {val}")

    print(f"\nTempo total de execução: {resultado['tempo_total']} ciclos (~{resultado['tempo_total_ms']:.9f} ms)")
