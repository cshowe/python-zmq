COMMANDS = [
    'PING',
    'MOVE',
    'QUIT',
    'NOP'
]


def _key_to_move(key):
    rv = {'type': 'MOVE', 'dx': 0, 'dy': 0}
    if key == 'h':
        rv['dx'] = -1
    elif key == 'j':
        rv['dy'] = 1
    elif key == 'k':
        rv['dy'] = -1
    elif key == 'l':
        rv['dx'] = 1
    return rv


def input_to_command(keypress):
    key = chr(keypress)
    if key in 'q':
        return {'type': 'QUIT'}
    elif key in 'hjkl':
        return _key_to_move(key)
    return {'type': 'NOP'}
