def ler_codigo_assembly(caminho_arquivo):
    instrucoes = []
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                # Ignora linhas vazias, comentários e diretivas .data/.text
                if linha and not linha.startswith('#') and not linha.startswith('.'):
                    instrucoes.append(linha)
    except FileNotFoundError:
        print("Arquivo nao encontrado. Verifique o caminho.")
    return instrucoes


def identificar_instrucao(instrucao):
    partes = instrucao.replace(',', '').split()
    if not partes:
        return None

    opcode = partes[0].lower()

    tipo_r = {'add', 'sub', 'and', 'or', 'slt'}
    tipo_i = {'lw', 'sw', 'addi', 'beq', 'bne'}
    tipo_j = {'j', 'jal'}

    if opcode in tipo_r:
        return {
            'tipo': 'R',
            'opcode': opcode,
            'destino': partes[1],
            'origem1': partes[2],
            'origem2': partes[3]
        }
    elif opcode in tipo_i:
        return {
            'tipo': 'I',
            'opcode': opcode,
            'destino': partes[1],
            'origem': partes[2],
            'imediato': partes[3] if len(partes) > 3 else None
        }
    elif opcode in tipo_j:
        return {
            'tipo': 'J',
            'opcode': opcode,
            'label': partes[1]
        }
    else:
        return {
            'tipo': 'Desconhecido',
            'linha': instrucao
        }


# Caminho do seu arquivo .asm
caminho = r'C:\Users\glisb\OneDrive\Documentos\Facul\Arquitetura e Organização de Computadores\main.asm'

# Leitura
codigo = ler_codigo_assembly(caminho)

# Análise de instruções
print("Instrucoes interpretadas:\n")
for i, instr in enumerate(codigo):
    info = identificar_instrucao(instr)
    print(f"Instrução {i}: {info}")
