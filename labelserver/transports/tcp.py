import socket

from . import Transport, UnexpectedlyClosed

class TCPTransport(Transport):
    """
    A blocking TCP Transport object.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._socket = None

    def send(self, data):
        total_sent = 0
        while total_sent < len(data):
            bytes_sent = self._socket.send(data[total_sent:])
            if bytes_sent == 0:
                raise UnexpectedlyClosed("The remote host unexpectedly closed the connection")
            total_sent += bytes_sent

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.host, self.port))

    def close(self):
        if self._socket:
            self._socket.close()
