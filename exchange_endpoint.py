from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import sys

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """

def check_sig(payload,signature,pubKey):
    eth_account.Account.enable_unaudited_hdwallet_features()
    acct, mnemonic = eth_account.Account.create_with_mnemonic()
    print("KEY",acct.key)
    eth_pk = pubKey
    eth_sk = signature

    eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
    eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg,eth_sk)
    if eth_account.Account.recover_message(eth_encoded_msg,signature=eth_sig_obj.signature.hex()) == eth_pk:
        print( "Eth sig verifies!" )
        return True
    else 
        return False

    print("ETH",eth_sig_obj)

def fill_order(order,txes=[]):
    pass
  
def log_message(d):
    payload = json.dumps(d['payload'])
    log_obj = Log(message=payload)
    g.session.add(log_obj)
    g.session.commit()

""" End of helper methods """



@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]

        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
        
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session
        signature = content['sig']
        payload = json.dumps(content['payload'])
        senderPubKey = content['payload']['sender_pk']
        receiver = content['payload']['receiver_pk']
        buyCurrency = content['payload']['buy_currency']
        sellCurrency = content['payload']['sell_currency']
        buyAmount = content['payload']['buy_amount']
        sellAmount = content['payload']['sell_amount']
        
        
        # TODO: Check the signature
        # TODO: Add the order to the database
        # TODO: Fill the order
        if(content['payload']['platform']=="Ethereum"):
            print("VERIFY")
            if(check_sig(payload,signature,senderPubKey)):
                order = Order(receiver_pk=receiver,sender_pk=senderPubKey,buy_currency=buyCurrency,sell_currency=sellCurrency,buy_amount=buyAMount,sell_amount=sellAmount)
                g.session.add(order)
                g.session.commit()
        
        
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        return jsonify(True)

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')