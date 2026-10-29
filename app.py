import json
import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# As tarefas ficam salvas neste arquivo, ao lado do app.py
ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tarefas.json')


# ---------- Funções de apoio ----------

def carregar_tarefas():
    """Lê as tarefas do arquivo JSON (ou devolve uma lista vazia)."""
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_tarefas():
    """Grava a lista de tarefas no arquivo JSON."""
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        json.dump(tarefas, f, ensure_ascii=False, indent=2)


def buscar_tarefa(tarefa_id):
    """Procura uma tarefa pelo id. Devolve None se não encontrar."""
    for tarefa in tarefas:
        if tarefa['id'] == tarefa_id:
            return tarefa
    return None


tarefas = carregar_tarefas()


# ---------- Rotas ----------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tarefas', methods=['GET'])
def listar_tarefas():
    return jsonify(tarefas)


@app.route('/tarefas', methods=['POST'])
def adicionar_tarefa():
    dados = request.get_json(silent=True) or {}

    texto = str(dados.get('texto', '')).strip()
    if not texto:
        return jsonify({'erro': 'Digite uma tarefa.'}), 400

    # Cada tarefa ganha um id único (o maior id atual + 1)
    novo_id = max((t['id'] for t in tarefas), default=0) + 1

    tarefa = {
        'id': novo_id,
        'texto': texto,
        'feito': False,
        'data': datetime.now().strftime('%d/%m/%Y')
    }

    tarefas.append(tarefa)
    salvar_tarefas()
    return jsonify(tarefa), 201


@app.route('/tarefas/<int:tarefa_id>', methods=['PUT'])
def atualizar_tarefa(tarefa_id):
    tarefa = buscar_tarefa(tarefa_id)
    if tarefa is None:
        return jsonify({'erro': 'Tarefa não encontrada.'}), 404

    dados = request.get_json(silent=True) or {}
    tarefa['feito'] = bool(dados.get('feito', tarefa['feito']))
    salvar_tarefas()
    return jsonify(tarefa)


@app.route('/tarefas/<int:tarefa_id>', methods=['DELETE'])
def remover_tarefa(tarefa_id):
    tarefa = buscar_tarefa(tarefa_id)
    if tarefa is None:
        return jsonify({'erro': 'Tarefa não encontrada.'}), 404

    tarefas.remove(tarefa)
    salvar_tarefas()
    return jsonify({'mensagem': 'Tarefa removida!'})


@app.route('/tarefas', methods=['DELETE'])
def limpar_tarefas():
    tarefas.clear()
    salvar_tarefas()
    return jsonify({'mensagem': 'Todas as tarefas foram removidas!'})


if __name__ == '__main__':
    app.run(debug=True)
