

class Transport(object):
    def send(self, data):
        raise NotImplementedError()

    def connect(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class TransportError(Exception):
    pass

class UnexpectedlyClosed(TransportError):
    pass


from .tcp import TCPTransport
