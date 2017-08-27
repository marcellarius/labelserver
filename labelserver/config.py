import collections
from labelserver.printer import LabelType
from labelserver.printers import PRINTER_CLASSES
import labelserver.utils
import marshmallow
import marshmallow.fields
import marshmallow.validate
import yaml


class ConfigSchema(marshmallow.Schema):
    printers = labelserver.utils.NestedDict(marshmallow.fields.Nested("PrinterConfig"), required=True)


class PrinterConfig(marshmallow.Schema):
    type = marshmallow.fields.String(required=True, validate=marshmallow.validate.OneOf(PRINTER_CLASSES))
    name = marshmallow.fields.String()
    label_types = marshmallow.fields.Dict(required=True, allow_none=False)




class LabelTypeConfig(marshmallow.Schema):
    name = marshmallow.fields.String()
    schema = labelserver.utils.NestedDict(marshmallow.fields.Nested("LabelTypeSchemaEntry"))
    template = marshmallow.fields.String()


SUPPORTED_LABELTYPE_FIELDS = {
    "string": marshmallow.fields.String,
    "integer": marshmallow.fields.Integer,
    "boolean": marshmallow.fields.Boolean
}


class LabelTypeSchemaEntry(marshmallow.Schema):
    type = marshmallow.fields.String(required=True, validate=marshmallow.validate.OneOf(SUPPORTED_LABELTYPE_FIELDS))
    required = marshmallow.fields.Boolean(required=False, missing=False)
    default = marshmallow.fields.Field(required=False)


def _get_items(d, key):
    return d.get(key, {}).items()


def load(config_file):
    raw_config = yaml.load(config_file)
    config = ConfigSchema(strict=True).load(raw_config).data

    printers = {}
    for id in config["printers"]:
        printer_config = config["printers"][id]
        raw_printer_config = raw_config["printers"][id]
        extra_options = {key: value for key, value in raw_printer_config.items() if key not in printer_config}
        printers[id] = _load_printer(id, printer_config, extra_options)
    return printers


def _load_printer(printer_id, printer_config, extra_options):
    printer_cls = PRINTER_CLASSES.get(printer_config["type"])
    printer = printer_cls.create(printer_id, extra_options)
    for lt_id, lt_config in printer_config["label_types"].items():
        printer.add_label_type(_load_labeltype(lt_id, lt_config))
    return printer


def _load_labeltype(lt_id, lt_config_or_filename):
    if isinstance(lt_config_or_filename, str):
        with open(lt_config_or_filename) as f:
            lt_config = yaml.load(f)
    else:
        lt_config = lt_config_or_filename

    config, errors = LabelTypeConfig(strict=True).load(lt_config)

    name = config.get("name", lt_id)
    template = config["template"]
    schema_config = config.get("schema")
    schema = _load_schema(schema_config) if schema_config else None

    return LabelType(lt_id, name, template, schema)


def _load_schema(schema_config):
    field_map = {}
    for key, conf in schema_config.items():
        field_cls = SUPPORTED_LABELTYPE_FIELDS[conf["type"]]
        field_map[key] = field_cls(required=conf["required"], missing=conf.get("default", marshmallow.missing))
    return _argmap_to_schema(field_map)


def _argmap_to_schema(argmap, **kwargs):
    class Meta(object):
        strict = True

    attrs = dict(argmap, Meta=Meta)
    cls = type(str(''), (marshmallow.Schema,), attrs)
    return cls(**kwargs)

