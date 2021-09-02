# -------------------------------------------------------  
#Link state routing
# -------------------------------------------------------  
from getpass import getpass
from lsr import *


if __name__ == '__main__':
    print( " ------------------------------")
    print("--- Welcome to the Chat! ---")
    print( " ------------------------------")
    jid = input('Type your jid: ')
    password = getpass('Type your password --> ')
    name_file = input('Type your names file --> ')
    topo_file = input('Type your topo file --> ')

    xmpp = LSRClient(jid, password,topo_file,name_file)
    xmpp.connect()
    xmpp.process(forever=False)
