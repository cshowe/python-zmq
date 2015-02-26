import sched
import zmq


class Scheduler(object):
    def __init__(self, gamestate):
        self._gamestate = gamestate
        self._scheduler = sched.scheduler(self._gamestate.now, self._gamestate.delay)


    def handle_event(self, agent, action):
        self._gamestate.apply_action(agent, action)
        new_action = agent.get_action(self._gamestate)
        if new_action is not None:
            self._scheduler.enter(1, 0, self.handle_event, (agent, new_action))

    def spawn(self, entity):
        self._scheduler.enter(0, 0, self.handle_event, (entity, {}))

    def start(self):
        self._scheduler.run()


class Player(object):
    def __init__(self, x, y, socket):
        self._socket = socket
        self.x = x
        self.y = y

    def get_action(self, gamestate):
        self._socket.send_json(gamestate.to_json())
        if gamestate._quit:
            return None
        return self._socket.recv_json()


class Bob(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_action(self, gamestate):
        if gamestate._quit:
            return None
        return {
            'type': 'MOVE',
            'dx': 1,
        }


class GameState(object):
    def __init__(self, size_x, size_y):
        self._time = 0
        self._map = []
        self._entities = []
        self._quit = False
        for i in range(size_y):
            if i == 0 or i == size_y - 1:
                self._map.append(['#'] * size_x)
            else:
                self._map.append(['#'] + ['.'] * (size_x - 2) + ['#'])

    def now(self):
        return self._time

    def delay(self, delay):
        self._time += delay

    def add_entity(self, entity):
        self._entities.append(entity)

    def apply_action(self, entity, action):
        if action.get('type', 'NOP') == 'QUIT':
            self._quit = True
        elif action.get('type', 'NOP') == 'MOVE':
            nx = entity.x + action.get('dx', 0)
            ny = entity.y + action.get('dy', 0)
            if self._map[ny][nx] == '.':
                entity.x = nx
                entity.y = ny

    def to_json(self):
        if self._quit:
            return {'type': 'QUIT'}
        else:
            return {
                'type': 'STATE',
                'map': self._map,
                'status': 'Time %d' % self._time,
                'entities': [{
                    'type': 'player',
                    'x': e.x, 'y': e.y} for e in self._entities]}


if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://127.0.0.1:5555')
    config = socket.recv_json()
    gamestate = GameState(config['size_x'], config['size_y'])
    scheduler = Scheduler(gamestate)
    player = Player(5, 5, socket)
    bob = Bob(3, 20)
    gamestate.add_entity(player)
    gamestate.add_entity(bob)
    scheduler.spawn(player)
    scheduler.spawn(bob)
    scheduler.start()

