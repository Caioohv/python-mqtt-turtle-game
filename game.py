import turtle
import time
import random
import paho.mqtt.client as mqtt
import json
import os
import rpyc
import threading

searching = False
game_started = False
mqtt_client = None
player_id = None
proxy = None
delay = 0.1

player_turtle = None
direction = "stop"
posX = 0
posY = 0
velocidade = 5
screen = None
other_players_turtles = {}
debug_frame_count = 0
BUTTON_LEFT = -100
BUTTON_RIGHT = 100
BUTTON_BOTTOM = -25
BUTTON_TOP = 25

BUTTON_TEXT_PROCURAR = "Procurar partida"
BUTTON_TEXT_CANCELAR = "Cancelar busca"


def generate_player_data():
	global player_id
	if player_id is None:
		player_id = random.randint(1, 10000)
	
	colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
	color = random.choice(colors)
	x = random.randint(-200, 200)
	y = random.randint(-150, 150)
	
	return {
		'id': player_id,
		'color': color,
		'x': x,
		'y': y
	}


def on_mqtt_connect(client, userdata, flags, rc):
	print(f"MQTT conectado com código {rc}")
	if rc == 0:
		client.subscribe("game/start")
		print("Inscrito no tópico game/start")


def on_mqtt_message(client, userdata, msg):
	topic = msg.topic
	payload = msg.payload.decode('utf-8')
	print(f'MQTT mensagem recebida: {topic} -> {payload}')
	
	if topic == 'game/start':
		print("Jogo iniciando! Conectando ao servidor RPC...")
		try:
			start_data = json.loads(payload)
			host = start_data.get('host', '127.0.0.1')
			port = start_data.get('port', 18861)
			start_game(host, port)
		except Exception as e:
			print(f"Erro ao processar game/start: {e}")
			start_game('127.0.0.1', 18861)


def setup_mqtt():
	global mqtt_client
	broker_host = os.environ.get('MQTT_BROKER', 'localhost')
	broker_port = int(os.environ.get('MQTT_PORT', '1883'))
	
	mqtt_client = mqtt.Client()
	mqtt_client.on_connect = on_mqtt_connect
	mqtt_client.on_message = on_mqtt_message
	
	try:
		mqtt_client.connect(broker_host, broker_port, 60)
		mqtt_client.loop_start()
		print(f'Conectado ao broker MQTT {broker_host}:{broker_port}')
		return True
	except Exception as e:
		print(f'Erro ao conectar ao MQTT: {e}')
		return False


def emit_join():
	if mqtt_client:
		player_data = generate_player_data()
		message = json.dumps(player_data)
		mqtt_client.publish('game/join', message)
		print(f'Enviando game/join: {message}')


def emit_left():
	if mqtt_client and player_id:
		message = json.dumps({'id': player_id})
		mqtt_client.publish('game/left', message)
		print(f'Enviando game/left: {message}')


def draw_button(pen):
	pen.clear()
	pen.penup()
	pen.goto(BUTTON_LEFT, BUTTON_BOTTOM)
	pen.pendown()
	fill_color = "#4CAF50" if not searching else "#f44336"
	pen.fillcolor(fill_color)
	pen.pencolor("black")
	pen.begin_fill()
	for _ in range(2):
		pen.forward(BUTTON_RIGHT - BUTTON_LEFT)
		pen.left(90)
		pen.forward(BUTTON_TOP - BUTTON_BOTTOM)
		pen.left(90)
	pen.end_fill()
	pen.penup()
	pen.goto((BUTTON_LEFT + BUTTON_RIGHT) / 2, (BUTTON_BOTTOM + BUTTON_TOP) / 2 - 8)
	pen.color("white")
	text = BUTTON_TEXT_CANCELAR if searching else BUTTON_TEXT_PROCURAR
	pen.write(text, align="center", font=("Arial", 14, "bold"))


def on_screen_click(x, y):
	global searching
	if game_started:
		return
		
	if BUTTON_LEFT <= x <= BUTTON_RIGHT and BUTTON_BOTTOM <= y <= BUTTON_TOP:
		searching = not searching
		
		if searching:
			emit_join()
		else:
			emit_left()
			
		draw_button(_button_pen)
		print("searching =", searching)


def setup_screen():
	global screen
	screen = turtle.Screen()
	screen.title("Jogo - Busca de Partida")
	screen.setup(width=600, height=400)
	pen = turtle.Turtle()
	pen.hideturtle()
	pen.speed(0)
	return screen, pen


def start_game(host, port):
	global game_started, proxy, player_turtle, screen, posX, posY
	
	try:
		proxy = rpyc.connect(host, port, config={'allow_public_attrs': True})
		print(f"Conectado ao servidor RPC em {host}:{port}")
		
		time.sleep(0.5)
		
		jogadores_list = proxy.root.exposed_obter_estado()
		
		print(f"Estado do servidor ao conectar: {len(jogadores_list)} jogadores")
		for jogador in jogadores_list:
			print(f"  Jogador {jogador['id']}: cor={jogador['color']}, pos=({jogador['x']}, {jogador['y']})")
		
		game_started = True
		
		setup_game_screen()
		
		game_player_id = player_id
		print(f"Usando ID do jogador: {game_player_id}")
		
		game_thread = threading.Thread(target=game_loop, args=(game_player_id,), daemon=True)
		game_thread.start()
		
	except Exception as e:
		print(f"Erro ao conectar ao servidor RPC: {e}")
		import traceback
		traceback.print_exc()
		game_started = False


def setup_game_screen():
	global screen, player_turtle, posX, posY
	
	screen.clear()
	
	screen.title("Jogo Multiplayer - Em andamento")
	screen.bgcolor("green")
	screen.setup(width=800, height=600)
	screen.tracer(0)
	
	player_data = None
	if proxy:
		try:
			jogadores_list = proxy.root.exposed_obter_estado()
			
			print(f"Estado atual do servidor: {len(jogadores_list)} jogadores")
			
			player_data = None
			for jogador in jogadores_list:
				if jogador['id'] == player_id:
					player_data = jogador
					posX = player_data['x']
					posY = player_data['y']
					print(f"Jogador {player_id} encontrado: pos({posX}, {posY}) cor({player_data['color']})")
					break
			
			if not player_data:
				print(f"Jogador {player_id} NÃO encontrado no servidor")
				player_data = generate_player_data()
				posX = player_data['x']
				posY = player_data['y']
		except Exception as e:
			print(f"Erro ao acessar servidor: {e}")
			import traceback
			traceback.print_exc()
			player_data = generate_player_data()
			posX = player_data['x']
			posY = player_data['y']
	else:
		player_data = generate_player_data()
		posX = player_data['x']
		posY = player_data['y']
	
	player_turtle = turtle.Turtle()
	player_turtle.speed(0)
	player_turtle.shape("circle")
	player_turtle.color(player_data['color'])
	player_turtle.penup()
	player_turtle.goto(posX, posY)
	print(f"Turtle do jogador atual criada: ID {player_id}, cor {player_data['color']}")
	
	setup_controls()


def setup_controls():
	screen.listen()
	screen.onkeypress(go_up, "w")
	screen.onkeypress(go_down, "s")
	screen.onkeypress(go_left, "a")
	screen.onkeypress(go_right, "d")
	screen.onkeypress(close_game, "Escape")


def go_up():
	global direction
	direction = "up"

def go_down():
	global direction
	direction = "down"

def go_left():
	global direction
	direction = "left"

def go_right():
	global direction
	direction = "right"

def close_game():
	global game_started
	if proxy and player_id:
		try:
			proxy.root.exposed_remover_jogador(player_id)
		except:
			pass
	game_started = False
	screen.bye()


def move():
	global posX, posY, player_turtle
	
	if direction == "up":
		posY += velocidade
		player_turtle.sety(posY)
	elif direction == "down":
		posY -= velocidade
		player_turtle.sety(posY)
	elif direction == "left":
		posX -= velocidade
		player_turtle.setx(posX)
	elif direction == "right":
		posX += velocidade
		player_turtle.setx(posX)


def criar_jogador_jogo():
	if proxy and player_id:
		try:
			jogadores_list = proxy.root.exposed_obter_estado()
			
			jogador_existe = False
			for jogador in jogadores_list:
				if jogador['id'] == player_id:
					jogador_existe = True
					break
			
			if jogador_existe:
				print(f"Jogador {player_id} já existe no servidor RPC")
				return player_id
			else:
				player_data = generate_player_data()
				proxy.root.exposed_criar_jogador(player_id, player_data['color'], posX, posY)
				print(f"Jogador criado no RPC com ID: {player_id}")
				return player_id
		except Exception as e:
			print(f"Erro ao criar jogador no RPC: {e}")
			import traceback
			traceback.print_exc()
	return None


def atualizar_posicao_jogo(game_id):
	if proxy and game_id:
		proxy.root.exposed_atualizar_posicao(game_id, posX, posY)


def atualizar_outros_jogadores(game_id):
	global other_players_turtles, debug_frame_count
	
	if not proxy:
		return
		
	try:
		jogadores_list = proxy.root.exposed_obter_estado()
		
		show_debug = debug_frame_count < 10
		
		if show_debug:
			jogadores_ids = [j['id'] for j in jogadores_list]
			print(f"[DEBUG] Total jogadores no servidor: {len(jogadores_list)}, IDs: {jogadores_ids}")
			print(f"[DEBUG] Meu ID: {game_id}")
			print(f"[DEBUG] Turtles criadas: {list(other_players_turtles.keys())}")
		
		for jogador in jogadores_list:
			jogador_id = jogador['id']
			
			if show_debug:
				print(f"[DEBUG] Processando jogador {jogador_id}, é outro jogador: {jogador_id != game_id}")
			
			if jogador_id != game_id:
				if jogador_id not in other_players_turtles:
					t = turtle.Turtle()
					t.speed(0)
					t.shape("circle")
					t.color(jogador['color'])
					t.penup()
					t.goto(jogador['x'], jogador['y'])
					other_players_turtles[jogador_id] = t
					print(f"✅ Criada turtle para jogador {jogador_id} cor {jogador['color']} pos({jogador['x']}, {jogador['y']})")
				else:
					other_players_turtles[jogador_id].goto(jogador['x'], jogador['y'])
		
		debug_frame_count += 1
				
	except Exception as e:
		print(f"Erro ao atualizar outros jogadores: {e}")
		import traceback
		traceback.print_exc()


def game_loop(game_id):
	global game_started
	
	print(f"Iniciando game loop para jogador {game_id}")
	frame_count = 0
	
	while game_started:
		try:
			atualizar_outros_jogadores(game_id)
			
			screen.update()
			
			move()
			
			atualizar_posicao_jogo(game_id)
			
			frame_count += 1
			if frame_count % 50 == 0:
				print(f"[LOOP] Frame {frame_count}, Turtles visíveis: {len(other_players_turtles) + 1}")
			
			time.sleep(delay)
		except Exception as e:
			print(f"Erro no loop do jogo: {e}")
			import traceback
			traceback.print_exc()
			break
	
	print("Loop do jogo encerrado")



screen, _button_pen = setup_screen()

if setup_mqtt():
	print("MQTT configurado com sucesso")
else:
	print("Falha ao configurar MQTT")

draw_button(_button_pen)
screen.onclick(on_screen_click)
screen.mainloop()
