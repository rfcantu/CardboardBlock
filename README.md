# CardboardBlock

A simple example of a block chain that is hosted on a local machine
This blockchain uses blocks to store transactions from different users, storing the hash
of the previous block to link them together. 

There is a proof of work algorithm that works like so:
Find a number p such that hash(pp') contains 4 leading zeroes, where p is the previous proof
and p' is the new proof

To Use:
python blockchain.py
- this will start the server on port 5000

To make requests, a program like curl or postman can be used to make get or post requests

To mine a block:
- make a GET request to http://localhost:5000/mine
- this will produce a recipient hash that can be used for new transactions

To create a new transaction:
- make a POST request to http://localhost:5000/transactions/new
- in the body of the request there needs to be three pieces of information in the form of JSON:
{
  "sender": "hash-from-get-request",
  "recipient": "someone-else-address",
  "amount": int
}

To inspect the whole chain:
- make a GET request to http://localhost:5000/chain

Notes:
- by altering where the flask app starts, the page can serve from a different port
- by altering the proof of work algorithm, it can be made more difficult or less difficult
- by altering the hash algorithm you can choose which you want to use
