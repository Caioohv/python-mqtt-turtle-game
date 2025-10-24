import rpyc
import paho.mqtt.client as mqtt
import json
import threading
import os

listaJogadores = {}
idJogador = 0
_lock = threading.Lock()
mqtt_client = None 


class MeuServico(rpyc.Service):
    def exposed_obter_estado(self):
        with _lock:
            jogadores_list = []
            for jid, jogador in listaJogadores.items():
                jogadores_list.append({
                    'id': jogador['id'],
                    'color': jogador['color'],
                    'x': jogador['x'],
                    'y': jogador['y']
                })
            print(f'[RPC] obter_estado chamado - {len(jogadores_list)} jogadores: {[j["id"] for j in jogadores_list]}')
            return jogadores_list

    def exposed_obter_id(self):
        global idJogador
        with _lock:
            idJogador += 1
            return idJogador

    def exposed_criar_jogador(self, player_id, color, x, y):
        with _lock:
            if player_id not in listaJogadores:
                jogador = {
                    'id': player_id,
                    'color': color,
                    'x': x,
                    'y': y
                }
                print('criando jogador ', player_id)
                listaJogadores[player_id] = jogador
                return True
            else:
                print('jogador já existe:', player_id)
                return False

    def exposed_remover_jogador(self, player_id):
        with _lock:
            if player_id in listaJogadores:
                del listaJogadores[player_id]
                print('removendo jogador ', player_id)
                return True
        return False

    def exposed_atualizar_posicao(self, player_id, x, y):
        with _lock:
            if player_id in listaJogadores:
                listaJogadores[player_id]['x'] = x
                listaJogadores[player_id]['y'] = y
                print('atualizando posição jogador ', player_id, x, y)
                return True
        return False


def _start_rpc_server_in_thread(host="0.0.0.0", port=18861):
    def _run():
        from rpyc.utils.server import ThreadedServer
        t = ThreadedServer(MeuServico, hostname=host, port=port)
        print(f"RPC server iniciado em {host}:{port}")
        t.start()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread


def _handle_init(payload):
    global idJogador
    try:
        data = json.loads(payload)
        if isinstance(data, dict) and 'id' in data:
            with _lock:
                idJogador = int(data['id'])
            print(f"inicializado idJogador = {idJogador}")
            return
    except Exception:
        pass

    try:
        with _lock:
            idJogador = int(payload)
        print(f"inicializado idJogador = {idJogador}")
    except Exception as e:
        print("payload init inválido:", payload, "erro:", e)


def _handle_join(payload):
    try:
        data = json.loads(payload)
        pid = int(data.get('id'))
        color = data.get('color', 'blue')
        x = float(data.get('x', 0))
        y = float(data.get('y', 0))
        with _lock:
            listaJogadores[pid] = {'id': pid, 'color': color, 'x': x, 'y': y}
        print('join -> adicionou jogador', pid)
        
        if len(listaJogadores) == 3:
            global mqtt_client
            if mqtt_client:
                _emit_start_game(mqtt_client)
                
    except Exception as e:
        print('erro ao processar join payload:', payload, 'erro:', e)


def _handle_left(payload):
    try:
        data = json.loads(payload)
        pid = int(data.get('id'))
    except Exception:
        try:
            pid = int(payload)
        except Exception as e:
            print('payload left inválido:', payload, 'erro:', e)
            return
    with _lock:
        if pid in listaJogadores:
            del listaJogadores[pid]
            print('left -> removeu jogador', pid)
        else:
            print('left -> jogador não encontrado', pid)


def _emit_start_game(client):
    with _lock:
        jogadores_count = len(listaJogadores)
        jogadores_ids = list(listaJogadores.keys())
    
    print(f'=== INICIANDO JOGO ===')
    print(f'Jogadores na lista: {jogadores_count}')
    print(f'IDs: {jogadores_ids}')
    
    start_data = {
        'host': '127.0.0.1',
        'port': 18861,
        'players': jogadores_count
    }
    message = json.dumps(start_data)
    client.publish('game/start', message)
    print(f'Emitindo game/start -> {jogadores_count} jogadores prontos')
    _start_rpc_server_in_thread(host=start_data['host'], port=start_data['port'])
    print(f'=== SERVIDOR RPC INICIADO ===')


def on_connect(client, userdata, flags, rc):
    global mqtt_client
    mqtt_client = client
    print("MQTT conectado com código", rc)
    client.subscribe("game/init")
    client.subscribe("game/join")
    client.subscribe("game/left")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    print('MQTT mensagem recebida', topic, payload)
    if topic == 'game/init':
        _handle_init(payload)
    elif topic == 'game/join':
        _handle_join(payload)
    elif topic == 'game/left':
        _handle_left(payload)
    else:
        print('Tópico não tratado:', topic)


def start_mqtt_loop(broker_host=None, broker_port=None):
    broker_host = broker_host or os.environ.get('MQTT_BROKER', 'localhost')
    broker_port = broker_port or int(os.environ.get('MQTT_PORT', '1883'))
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_host, broker_port, 60)
    print(f'Conectado ao broker MQTT {broker_host}:{broker_port}, aguardando eventos...')
    client.loop_forever()


try:
    start_mqtt_loop()
except KeyboardInterrupt:
    print('Encerrando servidor MQTT')



