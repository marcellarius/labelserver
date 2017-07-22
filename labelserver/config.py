import yaml
from labelserver.printers import PRINTER_CLASSES


def load(config_file):
    config_data = yaml.load(config_file)
    printers = {}
    for printer_id, printer_def in config_data.get("printers", {}).items():
        printer_type = printer_def.get("type")
        printer_cls = PRINTER_CLASSES.get(printer_def.get("type"))
        if not printer_cls:
            raise ValueError("Unknown printer type: %s" % printer_type)
        printers[printer_id] = printer_cls.load_config(printer_id, printer_def)
    return printers
