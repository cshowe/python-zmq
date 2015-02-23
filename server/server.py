import sched
import zmq


class Scheduler(object):
    def __init__(self, gamestate):
        self._t = 0
        self._scheduler = sched.scheduler(self._now, self._delay)
        self._gamestate = gamestate

    def _now(self):
        return self._t

    def _delay(self, delay):
        self._t += delay

    def handle_event(self, agent, action):
        self._gamestate.apply_action(action)
        new_action = agent.get_action(self._gamestate)
        if new_action is not None:
            self._scheduler.enter(1, 0, self.handle_event, (agent, new_action))

    def start(self, player):
        self._scheduler.enter(0, 0, self.handle_event, (player, {}))
        self._scheduler.run()


class Player(object):
    def __init__(self, socket):
        self._socket = socket

    def get_action(self, gamestate):
        self._socket.send_json(gamestate.to_json())
        if gamestate._quit:
            return None
        return self._socket.recv_json()


class GameState(object):
    def __init__(self, size_x, size_y):
        self._player_x = 5
        self._player_y = 5
        self._map = []
        self._quit = False
        for i in range(size_y):
            if i == 0 or i == size_y - 1:
                self._map.append(['#'] * size_x)
            else:
                self._map.append(['#'] + ['.'] * (size_x - 2) + ['#'])

    def apply_action(self, action):
        if action.get('type', 'NOP') == 'QUIT':
            self._quit = True
        elif action.get('type', 'NOP') == 'MOVE':
            nx = self._player_x + action.get('dx', 0)
            ny = self._player_y + action.get('dy', 0)
            if self._map[ny][nx] == '.':
                self._player_x = nx
                self._player_y = ny

    def to_json(self):
        if self._quit:
            return {'type': 'QUIT'}
        else:
            return {
                'type': 'STATE',
                'map': self._map,
                'entities': [{
                    'type': 'player',
                    'x': self._player_x,
                    'y': self._player_y}]}


if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://127.0.0.1:5555')
    config = socket.recv_json()
    gamestate = GameState(config['size_x'], config['size_y'])
    scheduler = Scheduler(gamestate)
    player = Player(socket)
    scheduler.start(player)

