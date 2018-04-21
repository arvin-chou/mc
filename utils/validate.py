# -*- coding: utf-8 -*-

from flask.ext.restful.fields import Raw
from flask.ext.restful import inputs
import utils.inputs as check_import


class int_in_list(Raw):
    """given a numbers list that we check the value is contain in it.

    Examples::
        validate.int_in_list(default=25, argument=[0, 25, 50, 100])

    """
    argument = None
    default = None

    def __init__(self, default=0, **kwargs):
        self.argument = kwargs['argument']\
            if kwargs['argument'] is not None else []
        self.default = default

        super().__init__(default=default)

    def __call__(self, value=None, **kwargs):
        value = inputs._get_integer(
            value if value is not None else self.default)
        if value not in self.argument:
            message = u"{0} is not in {1} List".format(value, self.argument)
            raise ValueError(message)
        return value

class Float(Raw):
    """given a number that we check the value is float.

    Examples::
        validate.float()

    """
    default = None

    def Float(value, argument='argument'):
        # todo implement
        #if float(value) <0:
        ##if isinstance(value, int) or isinstance(value, float):
        ##    pass
        ##else:
        #    error = ('Invalid {arg}: {value}. {arg} must be a '
        #            'integer or float'.format(arg=argument, value=value))
        #    raise ValueError(error)
        return value

    def __init__(self, default=0, **kwargs):
        self.default = default
        super().__init__(default=default)

    def __call__(self, value=None, **kwargs):
        value = value if not None else self.default
        return self.Float(value)
        
class natural(Raw):
    """given a number that we check the value is natural.

    Examples::
        validate.natural(default=25, 10)

    """
    default = None

    def __init__(self, default=0, **kwargs):
        self.default = default
        super().__init__(default=default)

    def __call__(self, value=None, **kwargs):
        value = value if not None else self.default
        return inputs.natural(value)


class str_in_list(Raw):
    """given a String list that we check the value is contain in it.

    Examples::
        validate.int_in_list(default='name', argument=['name', 'id'])

    """
    argument = None
    default = None

    def __init__(self, default=0, **kwargs):
        self.argument = kwargs['argument']\
            if kwargs['argument'] is not None else []
        self.default = default

        super().__init__(default=default)

    def __call__(self, value=None, **kwargs):
        if value not in self.argument:
            message = u"{0} is not in {1} List".format(value, self.argument)
            raise ValueError(message)

        return value


class Boolean(Raw):
    """given a value that we check the value is boolean.

    Examples::
        validate.natural(default=True, False)

    """
    default = None

    def __init__(self, default=0, **kwargs):
        self.default = default
        super().__init__(default=default)

    def __call__(self, value=None, **kwargs):
        value = value if not None else self.default
        return inputs.boolean(value)


class str_range(Raw):
    """given a String length range that we check the value is over-length in it.

    Examples::
        validate.str_range(argument={'low':1, 'high': 10})

    """
    argument = None

    def __init__(self, **kwargs):
        self.argument = kwargs['argument']\
            if kwargs['argument'] is not None else {}
        super().__init__()

    def __call__(self, value=None, **kwargs):
        """ Restrict input to an str in a range (inclusive) """

        low = self.argument['low']
        high = self.argument['high']

        try:
            value = str(value)
        except (TypeError, ValueError):
            raise ValueError('{} is not a valid str'.format(value))

        strlen = value.__len__()
        low = inputs._get_integer(low)
        high = inputs._get_integer(high)
        if strlen < low or high < strlen:
            error = ('Invalid {arg}: {val}. '
                     '{arg} length must be within the range {lo} - {hi}'.format(
                         arg=self.argument, val=value, lo=low, hi=high))
            raise ValueError(error)

        return value

class email(Raw):
    argument = None
    default = None

    def __init__(self, default=0, **kwargs):
        self.default = default

        super().__init__(default=default)

    def __call__(self, value=None):
        try:
            check_import.email(value)

        except Exception as error:
            raise ValueError(error)

        return value

