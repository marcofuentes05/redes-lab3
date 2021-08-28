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


def getDistance():
    pass

def send_message(to, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, int(to)))
        s.sendall(json.dumps(message).encode())
        # s.close()
    return 1

def receive_message(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, int(port)))
        s.listen()
        conn, addr = s.accept()
        data=conn.recv(1024)
        if not data:
            conn.close()
            return None
        else:
            s.close()
            return data.decode()

def create_message(sender, type, payload, to=None):
    message = copy.deepcopy(REQUESTS[type])
    message['from'] = sender
    message['payload'] = payload
    message['to'] = to
    return message

class Node:
    def __init__(self, id, port):
        self.neighbors = []
        # self.neighbors = ['A', 'B', 'C', 'D']
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

        threading.Thread(target=self.share_table).start()

    def load_neighbors(self, neighbors):
        self.neighbors = neighbors

    def init_table_vector(self):
        for neighbor in self.neighbors:
            self.echo(neighbor)

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, self.port))
            # with conn:
            while True:
                s.listen()
                conn, addr = s.accept()
                logging.debug(bcolors.HEADER + 'LISTENING' + bcolors.ENDC)
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        logging.debug(bcolors.WARNING+'[{}] - No data received: {}'.format(self.id, self.port)+bcolors.ENDC)
                        # conn.close()
                        # break
                        # pass
                    else:
                        try: 
                            receivedData = data.decode()
                            dataJson = json.loads(receivedData)
                            logging.debug(bcolors.OKBLUE+'[{} RECEIVED MESSAGE FROM {}] - {}'.format(self.id,addr, dataJson)+bcolors.ENDC)
                            if dataJson['type'] == 'ECHO':
                                response_message = create_message(self.id, 'echo-response', dataJson['payload'])
                                # time.sleep(2)
                                send_message(names['config'][dataJson['from']], response_message)
                                logging.debug(bcolors.OKBLUE+'[{} ECHO RESPONSE SENT TO {}]'.format(self.id,dataJson['from'])+bcolors.ENDC)
                            elif dataJson['type'] == 'ECHO-RESPONSE':
                                temp_distance = time.perf_counter() - dataJson['payload']
                                self.distance_vector_table[dataJson['from']] = temp_distance
                                self.paths[dataJson['from']] = dataJson['from']
                                logging.debug(bcolors.OKBLUE+'[{}] {} IS AT DISTANCE {}'.format(self.id, dataJson['from'], temp_distance)+bcolors.ENDC)
                            elif dataJson['type'] == 'MESSAGE':
                                if dataJson['to'] == self.id:
                                    logging.debug(bcolors.OKGREEN+'[{}] - MESSAGE RECEIVED FROM {}: {}'.format(self.id, dataJson['from'], dataJson['payload'])+bcolors.ENDC)
                                else:
                                    if dataJson['to'] in self.neighbors:
                                        self.send(dataJson['to'], dataJson)
                                        logging.debug(bcolors.OKCYAN+'[{}] - MESSAGE FORWARDED FROM {} TO {}'.format(self.id, dataJson['from'], dataJson['to'])+bcolors.ENDC)
                                    else:
                                        logging.debug(bcolors.FAIL+'[{}] - MESSAGE NOT SENT TO: {} - Not in neighbors'.format(self.id, dataJson['to'])+bcolors.ENDC)
                            elif dataJson['type'] == 'SHARE-TABLE':
                                logging.debug(bcolors.OKGREEN+'[{}] - TABLE RECEIVED FROM {}'.format(self.id, dataJson['from'])+bcolors.ENDC)
                                new_table = json.loads(dataJson['payload'])
                                sender = dataJson['from']
                                for key in new_table:
                                    if key in self.distance_vector_table:
                                        actual_distance_to_sender = self.distance_vector_table[sender] if  self.distance_vector_table[sender] else 0
                                        if (actual_distance_to_sender + new_table[key]) < self.distance_vector_table[key]:
                                            self.distance_vector_table[key] = actual_distance_to_sender + new_table[key]
                                            self.paths[key] = sender
                                    else:
                                        self.distance_vector_table[key] = new_table[key]
                        except Exception as e:
                            logging.debug(bcolors.FAIL+'[{}] - ERROR: {}'.format(self.id, e)+bcolors.ENDC)
                            logging.debug(bcolors.FAIL+'[{}] - ERROR: Message received from {} could not be decoded'.format(self.id, addr)+bcolors.ENDC)

    def echo(self, to):
        # Esta fn sera llamada por un hilo independiente que medira el tiempo transcurrido
        message = create_message(self.id, 'echo', time.perf_counter())
        tic = time.perf_counter()
        send_message(names['config'][to],message)
        logging.debug(bcolors.OKGREEN+'[{}] - Echo sent to: {}'.format(self.id, to)+bcolors.ENDC)
        # response = receive_message(names['config'][to])b
        # toc = time.perf_counter()
        # if response:
        #     self.distance_vector_table[to] = (toc - tic) * 1000 # Almaceno la cantidad de segundos que se tarda
        # else:
        #     self.distance_vector_table[to] = float('inf')

    def send(self, to, message):
        my_message = create_message(self.id, 'message', message, to)
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

    def share_table(self):
        time.sleep(20)
        while True:
            message = create_message(self.id, 'share-table', json.dumps(self.distance_vector_table))
            for neighbor in self.neighbors:
                send_message(names['config'][neighbor], message)
                logging.debug(bcolors.OKGREEN+'[{}] - Table sent to: {}'.format(self.id, neighbor)+bcolors.ENDC)
            time.sleep(20)

if __name__ == '__main__':

    # Cargando nodos y topologia de red
    names_file = open('names-demo.txt')
    names = json.load(names_file)
    names_file.close()

    topo_file = open('topo-demo.txt')
    topo = json.load(topo_file)
    topo_file.close()

    nodes = []
    thread_pool = []
    for id, node in enumerate(names['config']):
        nodes.append(Node(node, int(names['config'][node])))
        nodes[-1].load_neighbors(topo['config'][node])
        thread_pool.append(threading.Thread(target=nodes[-1].listen)) # Agarro el nodo que acabo de agregar (tiene el indice -1) y agrego el hilo
        thread_pool[-1].start()
    
    time.sleep(5)
    for node in nodes:
        node.init_table_vector()
    
    time.sleep(25)
    nodes[0].send('B', 'Hello, this is a test from A to C')
