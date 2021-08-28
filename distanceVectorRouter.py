# -----------------------------------------------------------------------------
# distanceVectorRouter.py
# Implementation of the Distance Vector Router (AKA, Bellman-Ford Algorithm)
# 
# -----------------------------------------------------------------------------
import threading 
import time
import logging
import json
import socket
import random
import copy
import sys

HOST = '127.0.0.1'
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Todos los requests deben tener  este formato:
# {
#   from: <nombre del nodo origen>,
#   type: 'ECHO'|'MESSAGE'|'RESPONSE'|'ECHO-RESPONSE'|'SHARE-TABLE'
#   payload: str -> solo si es de tipo MESSAGE
# }
REQUESTS = {
    'echo': {
        'from': '',
        'type': 'ECHO',
        'payload': '',
    },
    'echo-response': {
        'from': '',
        'type': 'ECHO-RESPONSE',
        'payload': '',
    },
    'message': {
        'from': '',
        'to': '',
        'type': 'MESSAGE',
        'hops': 0,
        'nodes': [],
        'distance': 0,
        'payload': ''
    },
    'share-table': {
        'from': '',
        'to': '',
        'type': 'SHARE-TABLE',
        'payload': '' #Es un json dumpeado con su tabla de rutas
    }
}


logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] - %(threadName)-10s : %(message)s')

#------------------------------------------------------------------
#------------------------------------------------------------------
#------------------------------------------------------------------
#------------------------------------------------------------------
def send_message(to, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, int(to)))
            s.sendall(json.dumps(message).encode())
            # s.close()
        return 1
    except:
        return 0


def create_message(sender, type, payload, to=None):
    message = copy.deepcopy(REQUESTS[type])
    message['from'] = sender
    message['payload'] = payload
    message['to'] = to
    return message

class Node:
    def __init__(self, id, port):
        self.neighbors = [] # ['A', 'B', 'C', 'D']
        self.distance_vector_table = {}
        # {
        #   destination_node_id: distance,
        # }
        self.paths = {}
        #{
        #   destination_node_id: first_node_id,
        # }

        #Tanto paths como distance_vector_table deben tener los mismos keys
        self.id = id
        self.port = port
        self.threads = True

        self.thread_pool = [threading.Thread(target=self.share_table),threading.Thread(target=self.periodic_echo) ]
        self.thread_pool[0].start()
        self.thread_pool[1].start()

    def load_neighbors(self, neighbors):
        self.neighbors = neighbors
        self.init_table_vector()

    def init_table_vector(self):
        for neighbor in self.neighbors:
            self.echo(neighbor)

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, self.port))
            while True:
                s.listen()
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        logging.debug(bcolors.WARNING+'[{}] - No data received: {}'.format(self.id, self.port)+bcolors.ENDC)

                    else:
                        try: 
                            receivedData = data.decode()
                            dataJson = json.loads(receivedData)
                            logging.debug(bcolors.OKBLUE+'[{} RECEIVED MESSAGE FROM {}] - {}'.format(self.id,addr, dataJson)+bcolors.ENDC)
                            if dataJson['type'] == 'ECHO':
                                response_message = create_message(self.id, 'echo-response', dataJson['payload'])
                                time.sleep(random.randint(0,5))
                                send_message(names['config'][dataJson['from']], response_message)
                                # logging.debug(bcolors.OKBLUE+'[{} ECHO RESPONSE SENT TO {}]'.format(self.id,dataJson['from'])+bcolors.ENDC)
                            elif dataJson['type'] == 'ECHO-RESPONSE':
                                temp_distance = time.perf_counter() - dataJson['payload']
                                self.distance_vector_table[dataJson['from']] = temp_distance
                                self.paths[dataJson['from']] = dataJson['from']
                                # logging.debug(bcolors.OKBLUE+'[{}] {} IS AT DISTANCE {}'.format(self.id, dataJson['from'], temp_distance)+bcolors.ENDC)
                            elif dataJson['type'] == 'MESSAGE':
                                if dataJson['to'] == self.id:
                                    logging.debug(bcolors.OKCYAN+'[{}] - MESSAGE RECEIVED FROM {}: {}'.format(self.id, dataJson['from'], dataJson['payload'])+bcolors.ENDC)
                                else:
                                    if dataJson['to'] in self.neighbors:
                                        self.resend(dataJson['to'], dataJson)
                                        logging.debug(bcolors.OKCYAN+'[{}] - MESSAGE FORWARDED FROM {} TO {}'.format(self.id, dataJson['from'], dataJson['to'])+bcolors.ENDC)
                                    else:
                                        if dataJson['to'] in self.paths:
                                            self.resend(self.paths[dataJson['to']], dataJson)
                                            logging.debug(bcolors.OKCYAN+'[{}] - MESSAGE FORWARDED FROM {} TO {}'.format(self.id, dataJson['from'], self.paths[dataJson['to']])+bcolors.ENDC)
                                        else:
                                            logging.debug(bcolors.FAIL+'[{}] - MESSAGE NOT SENT TO: {} - Route not loaded'.format(self.id, dataJson['to'])+bcolors.ENDC)
                            elif dataJson['type'] == 'SHARE-TABLE':
                                # logging.debug(bcolors.OKGREEN+'[{}] - TABLE RECEIVED FROM {}'.format(self.id, dataJson['from'])+bcolors.ENDC)
                                new_table = json.loads(dataJson['payload'])
                                sender = dataJson['from']
                                for key in new_table:
                                    if key in self.distance_vector_table:
                                        actual_distance_to_sender = self.distance_vector_table[sender] if  self.distance_vector_table[sender] else 0
                                        if (actual_distance_to_sender + new_table[key]) < self.distance_vector_table[key]:
                                            self.distance_vector_table[key] = actual_distance_to_sender + new_table[key]
                                            self.paths[key] = sender
                                    else:
                                        actual_distance_to_sender = self.distance_vector_table[sender] if  self.distance_vector_table[sender] else 0
                                        self.distance_vector_table[key] = new_table[key]+actual_distance_to_sender
                                        self.paths[key] = sender
                        except Exception as e:
                            logging.debug(bcolors.FAIL+'[{}] - ERROR: {}'.format(self.id, e)+bcolors.ENDC)
                            # logging.debug(bcolors.FAIL+'[{}] - ERROR: Message received from {} could not be decoded'.format(self.id, addr)+bcolors.ENDC)

    def echo(self, to):
        try:
            message = create_message(self.id, 'echo', time.perf_counter())
            tic = time.perf_counter()
            # logging.debug(bcolors.OKGREEN+'[{}] - Echo sending to: {}'.format(self.id, to)+bcolors.ENDC)
            send_message(names['config'][to],message)
        except Exception as e:
            self.distance_vector_table[to] = float('inf')

    def send(self, to, message):
        my_message = {}
        try:
            my_message = json.loads(message)
        except:
            my_message = create_message(self.id, 'message', message, to)
        my_message['hops'] += 1
        my_message['nodes'].append(self.id)
        my_message['distance'] += self.distance_vector_table[to] if to in self.distance_vector_table else 0
        logging.debug(bcolors.HEADER +'[{}] - Sending to: {}: {}'.format(self.id, to, my_message)+bcolors.ENDC)
        if to in self.neighbors:
            send_message(names['config'][to], my_message)
            logging.debug(bcolors.OKCYAN+'[{}] - MESSAGE SENT TO {} VIA DIRECT NEIGHBOR'.format(self.id, to)+bcolors.ENDC)
        else:
            if to in self.paths:
                neighbor = self.paths[to]
                send_message(names['config'][neighbor], my_message)
                logging.debug(bcolors.OKCYAN+'[{}] - MESSAGE FORWARDED TO {}'.format(self.id, neighbor)+bcolors.ENDC)
            else:
                logging.debug(bcolors.WARNING+'[{}] - COULD NOT FIND A ROUTE TO {} - FLOODING'.format(self.id, to)+bcolors.ENDC)
                for neighbor in self.neighbors:
                    send_message(names['config'][neighbor], my_message)

    def resend(self, to, message):
        my_message = copy.deepcopy(message)
        my_message['hops'] +=  1
        my_message['nodes'].append(self.id)
        my_message['distance'] += self.distance_vector_table[to]
        logging.debug(bcolors.HEADER +'[{}] - Re-sending to: {}: {}'.format(self.id, to, my_message)+bcolors.ENDC)
        send_message(names['config'][to], my_message)

    def share_table(self):
        time.sleep(10)
        while True:
            message = create_message(self.id, 'share-table', json.dumps(self.distance_vector_table))
            for neighbor in self.neighbors:
                send_message(names['config'][neighbor], message)
                logging.debug(bcolors.OKGREEN+'[{}] - TABLE SENT TO: {}'.format(self.id, neighbor)+bcolors.ENDC)
            if not self.threads:
                return 0
            time.sleep(10)

    def periodic_echo(self):
        time.sleep(10)
        while True:
            for neighbor in self.neighbors:
                self.echo(neighbor)
            if not self.threads:
                return 0
            time.sleep(10)

if __name__ == '__main__':

    # Cargando nodos y topologia de red
    names_file = open('names-demo.txt')
    names = json.load(names_file)
    names_file.close()

    topo_file = open('topo-demo.txt')
    topo = json.load(topo_file)
    topo_file.close()


    name = input('Cual es tu nombre?\n')
    if name not in names['config']:
        print('No hay ningun nodo con ese nombre')
        exit()

    node = Node(name, int(names['config'][name]))
    node.load_neighbors(topo['config'][name])
    # Para que escuche
    listening = threading.Thread(target=node.listen).start()


    while True:
        response = input("""
        MENU
        1. Send message
        2. Disconnect
        3. Get distance vector
        4. Get neighbors
        """)

        if response == '1':
            to = input('To: ')
            message = input('Message: ')
            node.send(to, message)
        elif response == '2':
            node.threads = False
            node.thread_pool[0].join()
            node.thread_pool[1].join()
            listening.join()
            sys.exit()
        elif response == '3':
            print(node.distance_vector_table)
        elif response == '4':
            print(node.neighbors)
        else:
            print('Invalid response')


    # nodes = []
    # thread_pool = []
    # for id, node in enumerate(names['config']):
    #     nodes.append(Node(node, int(names['config'][node])))
    #     nodes[-1].load_neighbors(topo['config'][node])
    #     thread_pool.append(threading.Thread(target=nodes[-1].listen)) # Agarro el nodo que acabo de agregar (tiene el indice -1) y agrego el hilo
    #     thread_pool[-1].start()
    
    # time.sleep(5)
    # for node in nodes:
    #     node.init_table_vector()
    
    # time.sleep(30)
    # print(nodes[0].distance_vector_table)
    # print(nodes[0].paths)
    # nodes[0].send('J', 'Hello, this is a test from A to J')
    # nodes[-1].send('A', 'Hello, this is a test from J to A')
