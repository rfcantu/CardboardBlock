import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):

    # Initalize the blockchain
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        # Create the seed block
        self.new_block(previous_hash=1, proof=100)
    
    '''
    Create a new block in the blockchain
    @param proof: The proof given by the Proof Of Work algorithm
    @param previous_hash: Hash of previous Block
    @return: new block
    '''
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    '''
    Creates a new transaction to go in the next mined block 
    @param sender: Address of the sender
    @param recipient: Address of the recipient
    @param amount: Amount
    @return: The index of the Block that will hold this transaction
    '''
    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        
        return self.last_block['index'] + 1
    
    '''
    Create SHA-256 hash of a Block
    '''
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    '''
    Proof Of Work Algorithm:
    Find a number p such that hash(pp') contains leading 3 zeroes, where p is the previous p 
    p is the previous oriidm and p' is the new proof
    '''
    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    '''
    Validate the proof: Does hash(last_proof, proof) contain 4 leading zeroes?
    '''
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    '''
    Add a new node to the list of nodes
    '''
    def register_node(self, address):
        parsed_url = urlparse(address)
        self.node.add(parsed_url.netloc)

    '''
    Determine if a given blockchain is valid
    '''
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1
         
        while current_index < len(chain):
            print(f'{last_block}')
            print(f'{block}')
            print("\n------------\n")
            # Check if the has of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True
    
    '''
    Concensus Algorithm, it resolves conflicts by replacing our chain with the longest
    one in the network
    '''
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        # Only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        # Replace our chain if we found a new valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():

    # Run Proof of Work to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # The sender is 0 to signify that this node has mined a new coin
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1, 
    )

    # Add the new block to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required data is in the POST request
    required = ['sender', 'recipient', 'amount']
    if not all (k in values for k in required):
        return 'Missing values', 400

    # Create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)