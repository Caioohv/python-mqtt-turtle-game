# python-mqtt-turtle-game
Exercício proposto na disciplina de Sistemas Distribuídos

Enunciado:
Agora iremos incrementar o jogo de bolas da última atividade prática. Para isso, utilizaremos o estilo arquitetônico baseado em eventos: https://github.com/Garrocho/sistemas_distribuidos/tree/main/eventos. 

Basicamente, iremos desenvolver a mecânica de criação de partida. Você pode utilizar o jogo Dota 2 de exemplo.

Nesse caso, teremos então o servidor MQTT, e trẽs clientes jogadores. Você deverá determinar somente para essa parte de criação de partida, como cada jogador irá Publicar ou Assinar tópicos no servidor MQTT visando o gerenciamento da criação de partida.

O jogo (partida iniciada) continua com a comunicação baseada em objetos. O jogo quando iniciar, cada jogador deverá ter uma posição específica, não podendo ser uma posição igual à versão anterior do jogo, para isso, veja o exemplo de posicionamento de jogadores na Tela 4.
