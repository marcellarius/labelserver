import collections
import marshmallow.fields
import marshmallow.exceptions


def extend(destination, *sources):
    """
    Python equivalent of Underscore.js _.extend method.

    This updates a dictionary with the keys other dictionaries. This is similar
    to (and uses) dict's `update()` method, however it supports multiple
    source dictionaries, which are processed in order.

    Like _.extend, this modifies the first parameter. If that's undesirable,
    then ``extend({}, a, b)`` will merge a and b into a new dict.

    Arguments:
        destination: the dict to modify
        *sources: a number of dicts to copy the items from

    Returns:
        The `destination` dict.
    """
    for s in sources:
        if s is not None:
            destination.update(s)
    return destination


def defaults(d, default_values):
    return extend({}, default_values, d)



# This field was a proposed alteration to the marshmallow.Dict field, which
# has not yet been included in Marshmallow.
#
# See: https://github.com/marshmallow-code/marshmallow/issues/483
#
class NestedDict(marshmallow.fields.Field):
    """A dict field. Supports dicts and dict-like objects. Optionally composed
    with another `Field` class or instance.
    Example: ::
        numbers = fields.Dict(fields.Float())
    :param Field cls_or_instance: A field class or instance.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    .. note::
        When the structure of nested data is not known, you may omit the
        schema argument to prevent content validation.
    .. versionadded:: 2.1.0
    """

    default_error_messages = {
        'invalid': 'Not a valid mapping type.'
    }

    def __init__(self, cls_or_instance=None, **kwargs):
        super(NestedDict, self).__init__(**kwargs)
        if cls_or_instance is None:
            self.container = None
        elif isinstance(cls_or_instance, type):
            if not issubclass(cls_or_instance, marshmallow.fields.Field):
                raise ValueError('The type of the dict elements '
                                 'must be a subclass of '
                                 'marshmallow.base.FieldABC')
            self.container = cls_or_instance()
        else:
            if not isinstance(cls_or_instance, marshmallow.fields.Field):
                raise ValueError('The instances of the dict '
                                 'elements must be of type '
                                 'marshmallow.base.FieldABC')
            self.container = cls_or_instance

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        if not self.container:
            return value
        if isinstance(value, collections.Mapping):
            return dict([
                (idx, self.container._serialize(each, attr, obj))
                for idx, each in value.items()
            ])
        self.fail('invalid')

    def _deserialize(self, value, attr, data):
        if not isinstance(value, collections.Mapping):
            self.fail('invalid')
        if not self.container:
            return value

        result = {}
        errors = {}
        for idx, each in value.items():
            try:
                result.update({idx: self.container.deserialize(each)})
            except marshmallow.exceptions.ValidationError as e:
                result.update({idx: e.messages})
                errors.update({idx: e.messages})

        if errors:
            raise marshmallow.exceptions.ValidationError(errors, data=result)

        return result
