from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from psycopg2 import Timestamp
import json
import requests
from Blockchain import Blockchain
from Blockchain import Block
from PandaCoin import PandaCoin as pc
import time
#iniciamos la app

app = Flask(__name__)
#iniciamos el objeto blockchain
blockchain = Blockchain()
#metodo de flask para declarar puntos de acceso
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    values["timestamp"]=time.time()
    Blockchain.new_transaction(values)
    response = {'message: Transaction will be added to Block'}
    return jsonify(response), 201
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data), "chain": chain_data})
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    return "Block #{} is mined.".format(result)
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)
peers = set()
# Punto de acceso para añadir nuevos compañeros a la red.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # La dirección del nodo compañero.
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400
    # Añadir el nodo a la lista de compañeros.
    peers.add(node_address)
    # Retornar el blockhain al nuevo nodo registrado para que pueda sincronizar.
    return get_chain()
@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internamente llama al punto de acceso `/register_node`
    para registrar el nodo actual con el nodo remoto especificado
    en la petición, y sincronizar el blockchain asimismo con el
    nodo remoto. 
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400
    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}
    # Hacer una petición para registrarse en el nodo remoto y obtener
    # información.
    response = requests.post(node_address + "/register_node", data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        global blockchain
        global peers
        # Actualizar la cadena y los compañeros.
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # si algo sale mal, pasárselo a la respuesta de la API
        return response.content, response.status_code

def create_chain_from_dump(chain_dump):
    blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"],block_data["previous_hash"])
        proof = block_data['hash']
        if idx > 0:
            added = blockchain.add_block(block, proof)
            if not added:
                raise Exception("The chain dump is tampered!!")
        else:  # el bloque es un bloque génesis, no necesita verificación
            blockchain.chain.append(block)
    return blockchain
def consensus():
    """
    Nuestro simple algoritmo de consenso. Si una cadena válida más larga es
    encontrada, la nuestra es reemplazada por ella.
    """
    global blockchain
    longest_chain = None
    current_len = len(blockchain)
    for node in peers:
        response = requests.get('http://{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain
    if longest_chain:
        blockchain = longest_chain
        return True
    return False
@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"], block_data["timestamp", block_data["previous_hash"]])
    proof = block_data['hash']
    added = blockchain.add_block(block, proof)
    if not added:
        return "The block was discarded by the node", 400
    return "Block added to the chain", 201
def announce_new_block(block):
    for peer in peers:
        url = "http://{}/add_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))