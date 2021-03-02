
#Snap 7
import snap7
from snap7.util import *
import struct
from db_layouts import step7toALGO

#ALgorand
import json
import time
import base64
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction

#Selfmade constants
import constants

# function from algorand inc.
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print('waiting for confirmation')
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print('transaction confirmed in round', txinfo.get('confirmed-round'))
    return txinfo

def ALGOtransaction(send_to_address, amount, TransactionNote):
    # setup http client w/guest key provided by purestake
    ip_address = "https://testnet-algorand.api.purestake.io/ps2"
    token = "YOUR TOKEN"
    headers = {
       "X-API-Key": token,
    }

    mnemonic1 = "your mnemonic"
    account_private_key = mnemonic.to_private_key(mnemonic1)
    account_public_key = 'YOUR PUPLIC KEY'

    algodclient = algod.AlgodClient(token, ip_address, headers)

    # get suggested parameters from algod
    params = algodclient.suggested_params()

    gh = params.gh
    first_valid_round = params.first
    last_valid_round = params.last
    fee = params.min_fee
    send_amount = amount

    existing_account = account_public_key

    # create and sign transaction
    tx = transaction.PaymentTxn(existing_account, fee, first_valid_round, last_valid_round, gh, send_to_address, send_amount, flat_fee=True,note=TransactionNote.encode())
    signed_tx = tx.sign(account_private_key)

    try:
        tx_confirm = algodclient.send_transaction(signed_tx)
        print('transaction sent with id', signed_tx.transaction.get_txid())
        wait_for_confirmation(algodclient, txid=signed_tx.transaction.get_txid())
        return constants.TRANSACTION_GOOD
    except Exception as e:
        print(e)
        return constants.TRANSACTION_BAD

def checkSendReq(plc, db_ALGO, dblength):
    sendIT = False

    while sendIT == False:
        try:
            print("####### Read DB Data #######")

            all_data = plc.db_read(db_ALGO,0,dblength)
            
            print("Bytearray of DB" + str(db_ALGO) + ":\n" + str(all_data) + ":\n")

            # Format the bytearray to the defined struct, which represents the DB structure
            db1 = snap7.util.DB(
                db_ALGO, # the db we use
                all_data, # bytearray from the plc
                step7toALGO, # layout specification DB variable data
                dblength,  #row size
                1, #size
                id_field=None, # field we can use to identify a row.
                db_offset=0,
                layout_offset=0,
                row_offset=0
            )

            print("Read data of DB" + str(db_ALGO) + str(db1[0]) + ":\n")

            if db1[0]['SendRequest'] == True:
                sendIT = True

            PartID = db1[0]['PartID']
            PartName = db1[0]['PartName']

        except Exception as e:
            try:
                plc.disconnect()
                plc.connect("192.168.0.1",0,2)
            except Exception as e:
                pass

        time.sleep(2.0)

    return PartID, PartName

def Result2PLC(plc, db_ALGO, transaction_res):
    print("Write Result to PLC")

    #An INT of the S7-PLC consists of two bytes
    bytearrayResult = bytearray(2)
    snap7.util.set_int(bytearrayResult, 0, transaction_res)

    #Run loop until plc.db_write() was succesful. Otherwise try to
    #establish a new connection
    confirmed = False

    while (confirmed == False):
        try:
            #Writte a
            plc.db_write(db_ALGO, 2, bytearrayResult) 
            confirmed = True
            print("Result handover was successful \n")
        except Exception as e:
            try:
                plc.disconnect()
                plc.connect("192.168.0.1",0,2)
            except Exception as e:
                pass

def payMaterial(PartID, PartName):
    print("####### Start Sending #######")
    print("Send Request from PLC for Part" + str(PartID))
        
    if PartID == 1:
        send_to_address = 'Your recipient address Nr.1'
        amount = 777
        TransactionNote = PartName + " has arrived"
    elif PartID == 2:
        send_to_address = 'Your recipient address Nr.2'    
        amount = 555
        TransactionNote = PartName + " has arrived"
    else:
        send_to_address = ' '  
        amount = 0

    if send_to_address != ' ':
        transaction_res = ALGOtransaction(send_to_address, amount, TransactionNote)
    else:
        print("Error: Unknown PartID")
        transaction_res = constants.UNKNOWN_PART

    return transaction_res

def main():

    plc = snap7.client.Client()

    # Connect to PLC:
    try:
        plc.connect("192.168.0.1",0,2)
    except Exception as e:
        print('No connection possible - program is terminated')
        return None

    #Specify DB number and length
    db_ALGO = 444
    dblength = 38

    try:
        while True:
            # check if there is a payment request from the machine
            PartID, PartName = checkSendReq(plc, db_ALGO, dblength)

            #Perform the payment via Algorand
            transaction_res = payMaterial(PartID, PartName)

            #Tell the machine if payment was an success or not
            Result2PLC(plc, db_ALGO, transaction_res)
    except KeyboardInterrupt:
        pass

    print("###### Ending Communication ######")
    plc.disconnect();

if __name__ == "__main__":
    main()



