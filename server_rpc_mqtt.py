import rpyc

import paho.mqtt.client as mqtt

listaJogadores = {}
idJogador = 0
jogo_iniciado = False
class MeuServico(rpyc.Service):
    def exposed_obter_estado(self):
        return listaJogadores

    def exposed_obter_id(self):
        global idJogador
        idJogador += 1
        return idJogador
    
    def exposed_criar_jogador(self, player_id, color, x, y):
        jogador = {
            'id': player_id,
            'color': color,
            'x': x,
            'y': y
        }
        print('criando jogador ', player_id)
        listaJogadores[player_id] = jogador
        return True

    def exposed_remover_jogador(self, player_id):
        if player_id in listaJogadores:
            del listaJogadores[player_id]
            print('removendo jogador ', player_id)
            return True
        return False
    
    def exposed_atualizar_posicao(self, player_id, x, y):
        if player_id in listaJogadores:
            listaJogadores[player_id]['x'] = x
            listaJogadores[player_id]['y'] = y
            print('atualizando posição jogador ', player_id, x, y)
            return True
        return False

from rpyc.utils.server import ThreadedServer
t = ThreadedServer(MeuServico, port=18861)
t.start()


broker="localhost"
port=1883
global joined
joined = 0

def on_message(client, userdata, msg):
    global jogo_iniciado
    global joined 
    print(msg.payload.decode())
    if msg.payload.decode() == "joined":
        joined += 1
        if(joined >= 3 and not jogo_iniciado):
            jogo_iniciado = True
            client.publish("/start", "start")
        print("Um jogador se juntou ao jogo.", joined, " jogadores no total.")
    if msg.payload.decode() == "left":
        joined -= 1
        print("Um jogador saiu do jogo.", joined, " jogadores no total.")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("/joined")
    client.subscribe("/left")

def on_publish(client, userdata, mid):
    print("Dados Publicados.")

global players
players = 0

client = mqtt.Client("admin")
client.on_publish = on_publish
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port)
client.loop_forever()