import rpyc

listaJogadores = {}
idJogador = 0

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