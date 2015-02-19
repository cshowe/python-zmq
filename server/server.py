import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://127.0.0.1:5555')
while True:
    request = socket.recv_string()
    socket.send_string('PONG')
