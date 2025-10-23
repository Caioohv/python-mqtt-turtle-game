import turtle
import time
import random
import paho.mqtt.client as mqtt
searching = False
BUTTON_LEFT = -100
BUTTON_RIGHT = 100
BUTTON_BOTTOM = -25
BUTTON_TOP = 25

BUTTON_TEXT_PROCURAR = "Procurar partida"
BUTTON_TEXT_CANCELAR = "Cancelar busca"


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
draw_button(_button_pen)
screen.onclick(on_screen_click)
screen.mainloop()
