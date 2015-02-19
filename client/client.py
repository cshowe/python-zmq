import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect('tcp://127.0.0.1:5555')
while True:
    print 'PING'
    socket.send_string('PING')
    response = socket.recv_string()
    print response
    time.sleep(2)
