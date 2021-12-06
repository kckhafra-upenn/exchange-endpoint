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

def check_sig(payload,signature):
    if(payload['platform']=="Ethereum"):
        eth_account.Account.enable_unaudited_hdwallet_features()
        acct, mnemonic = eth_account.Account.create_with_mnemonic()
        senderPubKey = payload['sender_pk']
        p=json.dumps(payload)
        eth_pk = senderPubKey
        eth_sk = signature
        # eth_pk = acct.address
        # eth_sk = acct.key

        eth_encoded_msg = eth_account.messages.encode_defunct(text=p)
        eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg,eth_sk)
        if eth_account.Account.recover_message(eth_encoded_msg,signature=eth_sig_obj.signature.hex()) == eth_pk:
            return True
        else: 
            return False
    elif(payload['platform']=="Algorand"):
        p=json.dumps(payload)
        # algo_sk, algo_pk = algosdk.account.generate_account()
        algo_sk = payload['sender_pk']
        algo_pk= payload['sender_pk']
        algo_sig_str = algosdk.util.sign_bytes(p.encode('utf-8'),algo_sk)

        if algosdk.util.verify_bytes(p.encode('utf-8'),algo_sig_str,algo_pk):
            return True
        return False
    else:
        return False


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
                log_message(content)
                return jsonify(False)
        
        for column in columns:
            if not column in content['payload'].keys():
                log_message(content)
                return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session
        signature = content['sig']
        payload = content['payload']
        senderPubKey = content['payload']['sender_pk']
        receiver = content['payload']['receiver_pk']
        buyCurrency = content['payload']['buy_currency']
        sellCurrency = content['payload']['sell_currency']
        buyAmount = content['payload']['buy_amount']
        sellAmount = content['payload']['sell_amount']
        
        
        # TODO: Check the signature
        # TODO: Add the order to the database
        # TODO: Fill the order
        
        if(check_sig(payload,signature)):
            order = Order(receiver_pk=receiver,sender_pk=senderPubKey,buy_currency=buyCurrency,sell_currency=sellCurrency,buy_amount=buyAmount,sell_amount=sellAmount)
            g.session.add(order)
            g.session.commit()
            return jsonify(True)
        else:
            return jsonify(False)
        
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
    return jsonify(False)

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    resultDb = {"data": g.session.query(Order).all()}
    resultArray=[]
    
    for x in resultDb['data']:
        resultDictx={}
        resultDictx['sender_pk']=x.sender_pk
        resultDictx['receiver_pk']=x.receiver_pk
        resultDictx['buy_currency']=x.buy_currency
        resultDictx['sell_currency']=x.sell_currency
        resultDictx['buy_amount']=x.buy_amount
        resultDictx['sell_amount']=x.sell_amount
        resultDictx['signature']=x.signature
        resultArray.append(resultDictx)
    result = {"data":resultArray}
    # print("RESULT",result)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')