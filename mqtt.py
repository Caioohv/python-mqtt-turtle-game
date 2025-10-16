import paho.mqtt.client as paho
broker="localhost"
port=1883

def on_publish(client, userdata, result):
    print(result)
    print(userdata)
    print(client)
    print("Dispositivo 1: Dados Publicados.")

client = paho.Client("admin")
client.on_publish = on_publish
client.connect(broker, port)