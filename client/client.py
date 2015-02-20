import curses
import zmq.green as zmq
import gevent
import sys

context = zmq.Context()

window = curses.initscr()
curses.noecho()
curses.cbreak()
window.keypad(1)

def hb():
    hb_socket = context.socket(zmq.REQ)
    hb_socket.connect('tcp://127.0.0.1:5555')
    try:
        while True:
            hb_socket.send_string('PING')
            response = hb_socket.recv_string()
            gevent.sleep(2)
    except gevent.GreenletExit:
        return

def gevent_getch(window):
    gevent.select.select([sys.stdin], [], [])
    return window.getch()

def input_loop(window):
    while True:
         keypress = gevent_getch(window)
         if keypress == ord('q'):
             return
         window.addch(keypress)
         window.refresh()


if __name__ == '__main__':
    hb_greenlet = gevent.spawn(hb)
    curses.wrapper(input_loop)
    hb_greenlet.kill()
