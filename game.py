import turtle
import time
import random
import paho.mqtt.client as mqtt
import json
import os

searching = False
mqtt_client = None
player_id = None
BUTTON_LEFT = -100
BUTTON_RIGHT = 100
BUTTON_BOTTOM = -25
BUTTON_TOP = 25

BUTTON_TEXT_PROCURAR = "Procurar partida"
BUTTON_TEXT_CANCELAR = "Cancelar busca"


def generate_player_data():
	"""Gera dados do jogador (ID, cor e posição inicial)"""
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
		# Aqui você pode adicionar lógica para conectar ao servidor RPC
		# e iniciar o jogo propriamente dito


def setup_mqtt():
	"""Configura e conecta ao broker MQTT"""
	global mqtt_client
	broker_host = os.environ.get('MQTT_BROKER', 'localhost')
	broker_port = int(os.environ.get('MQTT_PORT', '1883'))
	
	mqtt_client = mqtt.Client()
	mqtt_client.on_connect = on_mqtt_connect
	mqtt_client.on_message = on_mqtt_message
	
	try:
		mqtt_client.connect(broker_host, broker_port, 60)
		mqtt_client.loop_start()  # Inicia loop em thread separada
		print(f'Conectado ao broker MQTT {broker_host}:{broker_port}')
		return True
	except Exception as e:
		print(f'Erro ao conectar ao MQTT: {e}')
		return False


def emit_join():
	"""Emite evento de join para entrar na partida"""
	if mqtt_client:
		player_data = generate_player_data()
		message = json.dumps(player_data)
		mqtt_client.publish('game/join', message)
		print(f'Enviando game/join: {message}')


def emit_left():
	"""Emite evento de left para sair da partida"""
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
	if BUTTON_LEFT <= x <= BUTTON_RIGHT and BUTTON_BOTTOM <= y <= BUTTON_TOP:
		searching = not searching
		
		if searching:
			# Clicou em "Procurar partida" - emite join
			emit_join()
		else:
			# Clicou em "Cancelar busca" - emite left
			emit_left()
			
		draw_button(_button_pen)
		print("searching =", searching)


def setup_screen():
	screen = turtle.Screen()
	screen.title("Jogo - Busca de Partida")
	screen.setup(width=600, height=400)
	pen = turtle.Turtle()
	pen.hideturtle()
	pen.speed(0)
	return screen, pen



screen, _button_pen = setup_screen()

# Configurar MQTT antes de desenhar o botão
if setup_mqtt():
	print("MQTT configurado com sucesso")
else:
	print("Falha ao configurar MQTT")

draw_button(_button_pen)
screen.onclick(on_screen_click)
screen.mainloop()
