from PandaCoin import PandaCoin as pc
import hashlib
import json
import time
from urllib.parse import urlparse
class Block:
    def __init__(self, index, transactions, timestamp):
        """
        Constructor de la clase `Block`.
        :param index: ID único del bloque.
        :param transactions: Lista de transacciones.
        :param timestamp: Momento en que el bloque fue generado.
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
    #create a signature
    def create_signature(self, private_key):
        """
        Crea una firma digital del bloque.
        :param private_key: Llave privada del usuario.
        """
        self.signature = private_key.sign(self.block_data.encode(), 'SHA-256')
    def compute_hash(self):
        """
        Convierte el hash del bloque en una cadena de json y devuelve el hash del mismo
        """
        self.block_data = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(self.block_data.encode()).hexdigest()
class Blockchain:
    difficulty = 2
    def __init__(self):
        """
        Constructor de la clase `Blockchain`.
        """
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.create_genesis_block()
    def create_genesis_block(self):
        """
        Crea el bloque genesis y lo añade a la cadena, tiene index 0, previous_hash 0 y un hash valido
        """
        genesis_block = Block(0, [],0,time.time())
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
    def lastBlock(self):
        """
        Devuelve el último bloque de la cadena.
        """
        return self.chain[-1]
    def add_block(self, block, proof):
        """
        Crea un nuevo bloque y lo añade a la cadena, debe comprobar que la transaccion sea valida y que el previous hash coincida con el hash del bloque anterior.
        :param proof: Proporción de la cadena de bloques.
        :param previous_hash: Hash del bloque anterior.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not self.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def new_transaction(self, sender, recipient, amount):
        """
        Añade una nueva transacción a la cadena.
        :param sender: Dirección del remitente.
        :param recipient: Dirección del destinatario.
        :param amount: Cantidad a enviar.
        """
        self.current_transactions.append(pc(sender, recipient, amount))
        return self.lastBlock().index + 1
    def proof_of_work(self, block):
        """
        Calcula la proporción de la cadena de bloques.
        :param last_proof: Proporción del bloque anterior.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def is_valid_proof(self, block, block_hash):

        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())




