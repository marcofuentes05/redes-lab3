
import json

hello = 'HELLO'
echo_send = "ECHO SEND"
echo_response = "ECHO RESPONSE"
message_type= "MESSAGE"
lsp = 'LSP'


def json_to_object(jason_string):
    object = json.loads(jason_string)
    return object


def object_to_json(object):
    json_string = json.dumps(object)
    return json_string


def get_JID(names_file,ID):
	file = open(names_file, "r")
	file = file.read()
	info = eval(file)
	if(info["type"]=="names"):
		names = info["config"]
		JID = names[ID]
		return(JID)
	else:
		raise Exception('The file does not have a valid format for names')


def get_ID(names_file, JID):
	file = open(names_file, "r")
	file = file.read()
	info = eval(file)
	if(info["type"]=="names"):
		names = info["config"]
		JIDS = {v: k for k, v in names.items()}
		name = JIDS[JID]
		return(name)
	else:
		raise Exception('The file has not a valid format for names')



def get_neighbors(topology_file, ID):
	file = open(topology_file, "r")
	file = file.read()
	info = eval(file)
	if(info["type"]=="topo"):
		names = info["config"]
		neighbors_IDs = names[ID]
		return(neighbors_IDs)
	else:
		raise Exception('The file has not a valid format for topology')
	return  