# -------------------------------------------------------  
#Link state routing
# -------------------------------------------------------  
from getpass import getpass
from lsr import *


if __name__ == '__main__':
    print( " ------------------------------")
    print("--- Welcome to the Chat! ---")
    print( " ------------------------------")
    jid = input('Enter your jid: ')
    password = getpass('Enter your password --> ')
    name_file = input('Enter your names file --> ')
    topo_file = input('Enter your topo file --> ')

    xmpp = LSRClient(jid, password,topo_file,name_file)
    xmpp.connect()
    xmpp.process(forever=False)
