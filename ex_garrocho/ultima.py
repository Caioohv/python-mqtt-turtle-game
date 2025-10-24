import turtle
import time
import random
import rpyc

delay = 0.1

# Set up the screen
wn = turtle.Screen()
wn.title("Move Game by @Garrocho")
wn.bgcolor("green")
wn.setup(width=1.0, height=1.0, startx=None, starty=None)
wn.tracer(0) # Turns off the screen updates

# gamer 1
cor = random.choice(["red", "blue", "yellow", "purple", "orange", "pink", "cyan", "white"])
speed = 0
direction = "stop"
posX = 0 
posY = 0
velocidade = 5


head = turtle.Turtle()
head.speed(speed)
head.shape("circle")
head.color(cor)
head.penup()
head.goto(posX,posY)
head.direction = direction

# Functions
def go_up():
    global direction
    direction = "up"
    head.direction = direction

def go_down():
    global direction
    direction = "down"
    head.direction = direction

def go_left():
    global direction
    direction = "left"
    head.direction = direction

def go_right():
    global direction
    direction = "right"
    head.direction = direction

def close():
    proxy.root.exposed_remover_jogador(id)
    wn.bye()

def move():
    global posX, posY
    if direction == "up":
        y = head.ycor()
        posY = y + velocidade
        head.sety(posY)

    if direction == "down":
        y = head.ycor()
        posY = y - velocidade
        head.sety(posY)

    if direction == "left":
        x = head.xcor()
        posX = x - velocidade
        head.setx(posX)

    if direction == "right":
        x = head.xcor()
        posX = x + velocidade
        head.setx(posX)

# Keyboard bindings
wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
wn.onkeypress(close, "Escape")

def criar_jogador(): 
    id = proxy.root.exposed_obter_id()
    proxy.root.exposed_criar_jogador(id, cor, posX, posY)
    return id

def atualizar_posicao(id):
    proxy.root.exposed_atualizar_posicao(id, posX, posY)

def atualiza_jogo(id):
    todos = proxy.root.exposed_obter_estado()
    for j in todos:
        if todos[j]['id'] != id:
            if 'turtle' not in todos[j]:
                t = turtle.Turtle()
                t.speed(0)
                t.shape("circle")
                t.color(todos[j]['color'])
                t.penup()
                todos[j]['turtle'] = t
            todos[j]['turtle'].goto(todos[j]['x'], todos[j]['y'])

# Main game loop
proxy = rpyc.connect('localhost', 18861, config={'allow_public_attrs': True})

id = criar_jogador()

while True:
    atualiza_jogo(id)  
    wn.update()
    move()
    atualizar_posicao(id)
    time.sleep(delay)


wn.mainloop()