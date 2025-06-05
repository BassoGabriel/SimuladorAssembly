from flask import Flask, jsonify, render_template
from Projeto import (
    ler_codigo_assembly, ler_configuracao_cpu, identificar_instrucao,
    instrucao_tipo_r_para_bin, instrucao_tipo_i_para_bin, instrucao_tipo_j_para_bin,
    executar
)

app = Flask(__name__)

# Estado global
estado = {
    'codigo': [],
    'rotulos': {},
    'PC': 0,
    'registradores': {},
    'memoria': {},
    'config': {},
    'tempo_total': 0,
    'tempo_total_ms': 0.0,
    'etapas': [],
    'etapa_atual': 0
}

def inicializar():
    caminho = "main.asm"
    estado['codigo'], estado['rotulos'] = ler_codigo_assembly(caminho)
    estado['config'] = ler_configuracao_cpu(caminho)
    estado['PC'] = 0
    estado['tempo_total'] = 0
    estado['tempo_total_ms'] = 0.0
    estado['etapa_atual'] = 0
    estado['etapas'] = []
    estado['registradores'] = {
        "$zero": 0, "$at": 0, "$v0": 0, "$v1": 0,
        "$a0": 0, "$a1": 0, "$a2": 0, "$a3": 0,
        "$t0": 0, "$t1": 0, "$t2": 0, "$t3": 0,
        "$t4": 0, "$t5": 0, "$t6": 0, "$t7": 0,
        "$s0": 0, "$s1": 0, "$s2": 0, "$s3": 0,
        "$s4": 0, "$s5": 0, "$s6": 0, "$s7": 0,
        "$t8": 0, "$t9": 0, "$k0": 0, "$k1": 0,
        "$gp": 0, "$sp": 0, "$fp": 0, "$ra": 0
    }
    # Inicializa 256 bytes de memória simulada (endereços de 0x00000000 a 0x000000FC, de 4 em 4)
    estado['memoria'] = {f"0x{i:08X}": 0 for i in range(0, 256, 4)}

# Exemplo de preenchimento com valores iniciais (opcional)
    estado['memoria']["0x00000000"] = 5
    estado['memoria']["0x00000004"] = 10
    estado['memoria']["0x00000008"] = 0


    # Executar e armazenar as etapas
    while estado['PC'] < len(estado['codigo']):
        linha = estado['codigo'][estado['PC']]
        instrucao = identificar_instrucao(linha)
        if instrucao:
            tipo = instrucao['tipo']
            if tipo == 'R':
                binario, hexa = instrucao_tipo_r_para_bin(instrucao)
            elif tipo == 'I':
                binario, hexa = instrucao_tipo_i_para_bin(instrucao)
            elif tipo == 'J':
                binario, hexa = instrucao_tipo_j_para_bin(instrucao, estado['rotulos'])
            else:
                binario, hexa = "", ""

            tempo = estado['config'][f"tempo_tipo_{tipo}"]
            estado['tempo_total'] += tempo
            estado['tempo_total_ms'] = estado['tempo_total'] * estado['config']['clock_ciclo_ms']

            etapa = {
                "pc": estado['PC'] * 4,
                "linha": linha,
                "binario": binario,
                "hex": hexa,
                "tempo_instrucao": tempo,
                "tempo_total": estado['tempo_total'],
                "tempo_total_ms": estado['tempo_total_ms'],
                "registradores": estado['registradores'].copy(),
                "memoria": estado['memoria'].copy()
            }

            estado['etapas'].append(etapa)

            estado['PC'] = executar(instrucao, estado['registradores'], estado['memoria'], estado['rotulos'], estado['PC'])
        else:
            estado['PC'] += 1

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/resultado_final")
def resultado_final():
    if estado['etapas']:
        ultimo = estado['etapas'][-1]
        tempo_total = ultimo['tempo_total']
        tempo_total_ms = ultimo['tempo_total_ms']
    else:
        tempo_total = estado['tempo_total']
        tempo_total_ms = estado['tempo_total'] * estado['config']['clock_ciclo_ms']

    return jsonify({
        "etapas": estado['etapas'],
        "registradores_finais": estado['registradores'],
        "memoria_final": estado['memoria'],
        "tempo_total": tempo_total,
        "tempo_total_ms": tempo_total_ms
    })

@app.route("/passo_a_passo")
def passo_a_passo():
    if estado['etapa_atual'] < len(estado['etapas']):
        etapa = estado['etapas'][estado['etapa_atual']]
        estado['etapa_atual'] += 1

        # Atualiza tempo total dinamicamente
        estado['tempo_total'] = etapa['tempo_total']
        estado['tempo_total_ms'] = etapa['tempo_total_ms']

        return jsonify(etapa)
    else:
        return jsonify({"fim": True})

@app.route("/resetar")
def resetar():
    inicializar()
    return jsonify({"ok": True})

if __name__ == "__main__":
    inicializar()
    app.run(debug=True)
