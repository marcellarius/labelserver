from labelserver.printer import Printer, LabelType, Job
import yaml


class CognitiveLbt42Printer(Printer):
    def __init__(self, id, hostname, port, device):
        super(CognitiveLbt42Printer, self).__init__()
        self.id = id
        self.label_types = {}
        self.hostname = hostname
        self.port = port
        self.device = device

    def _add_label_type(self, label_type):
        self.label_types[label_type.id] = label_type

    @classmethod
    def load_config(cls, id, printer_def):
        hostname = printer_def.get("hostname")
        port = printer_def.get("port", 9100)
        device = printer_def.get("device")

        if not (hostname and port) and not device:
            raise Exception("Hostname/port or a serial device must be specified")

        printer = cls(id, hostname, port, device)

        label_types = {}
        for labeltype_id, labeltype_filename in printer_def.get("label-types", {}).items():
            with open(labeltype_filename) as f:
                labeltype_def = yaml.load(f)
            printer._add_label_type(CognitiveLbt42LabelType.load_config(labeltype_id, printer, labeltype_def))
        return printer


class CognitiveLbt42LabelType(LabelType):
    def __init__(self, id, printer, label_template):
        self.id = id
        self.printer = printer
        self.label_template = label_template

    def prepare(self, label_data):
        pass

    @classmethod
    def load_config(cls, id, printer, labeltype_def):
        template = labeltype_def.get("template")
        return cls(id, printer, template)


class CognitiveLbt42Job(Job):
    def __init__(self, printer, label_type, compiled_label):
        super(self, CognitiveLbt42Job).__init__(printer, label_type)

