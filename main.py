import hashlib
import os
import sys
import time
from PandaCoin import PandaCoin as pc
from Blockchain import BlockChain as bc

#create a blockchain
blockchain = bc()
#create some transactions
t1='Javi manda 478 pc a Carlos'
t2='Carlos manda a Javi 578 pc'
t3='Pedro manda a Juan 43 pc'
t4='Juan manda a Pedro 5 pc'
#create a block from transactions
blockchain.createBlock([t1,t2])
blockchain.createBlock([t3,t4])
#display the chain
blockchain.displayChain()
