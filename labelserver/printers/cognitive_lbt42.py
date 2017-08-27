from labelserver.printer import Printer, LabelType, Job
from labelserver.transports import TCPTransport
import labelserver.utils
import time
import yaml

class CognitiveLbt42Printer(Printer):
    default_config = {
        "job_delay": 1,
        "port": 9100
    }

    def __init__(self, id, config):
        super(CognitiveLbt42Printer, self).__init__()
        self.id = id
        self.config = config

    def create_transport(self):
        return TCPTransport(self.config["hostname"], self.config["port"])

    def print(self, job):
        with self.create_transport() as transport:
            data = _convert_line_endings(job.data).encode("ascii")
            transport.send(data)
            transport.close()
            time.sleep(self.config["job_delay"])

    @classmethod
    def create(cls, id, config):
        config = labelserver.utils.defaults(config, cls.default_config)
        hostname = config.get("hostname")
        port = config.get("port")
        device = config.get("device")

        if not (hostname and port) and not device:
            raise Exception("Hostname/port or a serial device must be specified")

        return cls(id, config)

def _convert_line_endings(data):
    return data.replace("\n", "\r\n")
