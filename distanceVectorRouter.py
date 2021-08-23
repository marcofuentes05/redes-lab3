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
#   type: 'ECHO'|'MESSAGE'|'RESPONSE'|'ECHO-RESPONSE'
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
        'type': 'MESSAGE',
        'payload': ''
    },
    'response': {
        'from': '',
        'type': 'RESPONSE',
        'payload': ''
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

def create_message(sender, type, payload):
    message = copy.deepcopy(REQUESTS[type])
    message['from'] = sender
    message['payload'] = payload
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

    def load_neighbors(self, neighbors):
        self.neighbors = neighbors

    def init_table_vector(self):
        for neighbor in neighbors:
            pass
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
                                response_message = create_message(self.port, 'echo-response', dataJson['payload'])
                                conn.send(str.encode(json.dumps(response_message)))
                                logging.debug(bcolors.OKBLUE+'[{} ECHO RESPONSE SENT TO {}]'.format(self.id,addr)+bcolors.ENDC)
                            elif dataJson['type'] == 'ECHO-RESPONSE':
                                self.distance_vector_table[dataJson['from']] = time.perf_counter() - dataJson['payload']
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

if __name__ == '__main__':

    # Cargando nodos y topologia de red
    names_file = open('names-demo.txt')
    names = json.load(names_file)
    names_file.close()

    topo_file = open('topo-demo.txt')
    topo = json.load(topo_file)
    topo_file.close()

    # print(names)
    # print(topo)
    nodes = []
    thread_pool = []
    for id, node in enumerate(names['config']):
        nodes.append(Node(id, int(names['config'][node])))
        nodes[-1].load_neighbors(topo['config'][node])
        thread_pool.append(threading.Thread(target=nodes[-1].listen)) # Agarro el nodo que acabo de agregar (tiene el indice -1) y agrego el hilo
        thread_pool[-1].start()
    
    
    # time.sleep(5)
    nodes[0].echo("C")
    # node_0 = Node(0, 3001)
    # node_1 = Node(1, 3002)


    # thread_1 = threading.Thread(target=node_1.listen)
    # thread_1.start()

    # thread_2 = threading.Thread(target=node_1.echo, args=(3001, b'Message Test'))
    # time.sleep(5)
    # thread_2.start()
    # for i in range(50):
    #     # print(i)
    #     time.sleep(2)

    # print(names['config'])
    # for thread in thread_pool:
    #     thread.join()
    # thread_0.join()
    # thread_1.join()
