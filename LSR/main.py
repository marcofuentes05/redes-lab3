from getpass import getpass
from lsr import *

"""
    Main class
"""

if __name__ == '__main__':
    print("\n--- Welcome to the Chat! ---\n")
    jid = input('Type your jid: ')
    password = getpass('Type your password: ')
    name_file = input('Type your names file: ')
    topo_file = input('Type your topology file: ')

    xmpp = LSRClient(jid, password,topo_file,name_file)
    xmpp.connect()
    xmpp.process(forever=False)
