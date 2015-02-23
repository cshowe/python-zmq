import curses
import sys
import zmq

import commands


class Console(object):
    LEFT_WIDTH = 20
    STATUS_HEIGHT = 2

    def __init__(self, parent_window):
        self._parent_window = parent_window
        y, x = parent_window.getmaxyx()
        self._main = parent_window.subwin(
            y - Console.STATUS_HEIGHT - 1,
            x - Console.LEFT_WIDTH - 1,
            0,
            Console.LEFT_WIDTH + 1)
        self._status = parent_window.subwin(
            Console.STATUS_HEIGHT, x - Console.LEFT_WIDTH - 1,
            y - Console.STATUS_HEIGHT, Console.LEFT_WIDTH + 1)
        parent_window.vline(0, Console.LEFT_WIDTH, '|', y)
        parent_window.hline(
            y - Console.STATUS_HEIGHT - 1,
            Console.LEFT_WIDTH + 1, '-', x - Console.LEFT_WIDTH - 1)

    def main_size(self):
        return self._main.getmaxyx()

    def getch(self):
        return self._parent_window.getch()

    def update(self, update_dict):
        self._status.erase()
        self._status.addstr(update_dict.get('status', ''))
        self._status.noutrefresh()

        self._main.erase()
        for y, line in enumerate(update_dict.get('map', [])):
            self._main.addstr(y, 0, ''.join(line))
        for entity in update_dict.get('entities', []):
            self._main.addstr(entity['y'], entity['x'], '@')
        self._main.noutrefresh()

    def refresh(self):
        curses.doupdate()


def main_loop(window, socket):
    console = Console(window)
    y, x = console.main_size()
    socket.send_json({'size_x': x  - 1, 'size_y': y})
    while True:
        result = socket.recv_json()
        if result['type'] == 'QUIT':
            break
        console.update(result)
        console.refresh()
        keypress = console.getch()
        socket.send_json(commands.input_to_command(keypress))

if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://127.0.0.1:5555')
    window = curses.initscr()
    curses.curs_set(0)
    curses.wrapper(main_loop, socket)
