import zmq


class GameState(object):
    def __init__(self):
        self._player_x = 1
        self._player_y = 1

    def update(self, **kwargs):
        self._player_x += kwargs.get('player_dx', 0)
        self._player_y += kwargs.get('player_dy', 0)

    def to_json(self):
        return {
            'type': 'STATE',
            'entities': [{
                'type': 'player',
                'x': self._player_x,
                'y': self._player_y}]}


def server_loop(socket, gamestate):
    while True:
        request = socket.recv_json()
        if request['type'] == 'QUIT':
            socket.send_json({'type': 'QUIT'})
        elif request['type'] == 'MOVE':
            gamestate.update(player_dx = request['dx'], player_dy = request['dy'])
            socket.send_json(gamestate.to_json())
        else:
            socket.send_json({'type': 'NOP'})


if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://127.0.0.1:5555')
    gamestate = GameState()
    server_loop(socket, gamestate)

