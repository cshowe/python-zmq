import random
import zmq


class GameState(object):
    def __init__(self, size_x, size_y):
        self._player_x = 5
        self._player_y = 5
        self._map = []
        for i in range(size_y):
            if i == 0 or i == size_y - 1:
                self._map.append(['#'] * size_x)
            else:
                self._map.append(['#'] + ['.'] * size_x + ['#'])
        for i in range(200):
            y, x = random.randint(0, size_y - 1), random.randint(0, size_x - 1)
            self._map[y][x] = '#'

    def update(self, **kwargs):
        nx = self._player_x + kwargs.get('player_dx', 0)
        ny = self._player_y + kwargs.get('player_dy', 0)
        if self._map[ny][nx] == '.':
            self._player_x = nx
            self._player_y = ny

    def to_json(self):
        return {
            'type': 'STATE',
            'map': self._map,
            'entities': [{
                'type': 'player',
                'x': self._player_x,
                'y': self._player_y}]}


def server_loop(socket, gamestate):
    while True:
        request = socket.recv_json()
        if request['type'] == 'QUIT':
            socket.send_json({'type': 'QUIT'})
            continue
        elif request['type'] == 'MOVE':
            gamestate.update(player_dx = request['dx'], player_dy = request['dy'])
        socket.send_json(gamestate.to_json())


if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://127.0.0.1:5555')
    gamestate = GameState(164, 44)
    server_loop(socket, gamestate)

