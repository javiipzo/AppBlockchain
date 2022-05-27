import hashlib
import os
import sys
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from psycopg2 import Timestamp
import json
import requests
from Blockchain import Blockchain
from Blockchain import Block
from PandaCoin import PandaCoin as pc
from app import app
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []
def fetch_posts():
    """
    Función para obtener la cadena desde un nodo blockchain,
    procesar la información y almacenarla localmente.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)
        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],reverse=True)

@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Punto de acceso para crear una nueva transacción vía nuestra
    aplicación.
    """
    post_content = request.form["content"]
    author = request.form["author"]
    post_object = {
        'author': author,
        'content': post_content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,json=post_object,headers={'Content-type': 'application/json'})

    return redirect('/')
app.run(debug=True)


