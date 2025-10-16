# python-mqtt-turtle-game
Exercício proposto na disciplina de Sistemas Distribuídos

Enunciado:
Agora iremos incrementar o jogo de bolas da última atividade prática. Para isso, utilizaremos o estilo arquitetônico baseado em eventos: https://github.com/Garrocho/sistemas_distribuidos/tree/main/eventos. 

Basicamente, iremos desenvolver a mecânica de criação de partida. Você pode utilizar o jogo Dota 2 de exemplo.

Nesse caso, teremos então o servidor MQTT, e trẽs clientes jogadores. Você deverá determinar somente para essa parte de criação de partida, como cada jogador irá Publicar ou Assinar tópicos no servidor MQTT visando o gerenciamento da criação de partida.

O jogo (partida iniciada) continua com a comunicação baseada em objetos. O jogo quando iniciar, cada jogador deverá ter uma posição específica, não podendo ser uma posição igual à versão anterior do jogo, para isso, veja o exemplo de posicionamento de jogadores na Tela 4.

## Para rodar:

```sh
sudo apt update

sudo apt install python3-rpyc python3-paho-mqtt

for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo systemctl enable --now docker
docker --version
docker compose version


# iniciar
sudo docker compose up -d

# ver status
sudo docker ps

# testar
mosquitto_sub -h localhost -t test/topic &
mosquitto_pub -h localhost -t test/topic -m "Olá MQTT!"

```

