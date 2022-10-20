"""
    salt.utils.yamldumper
    ~~~~~~~~~~~~~~~~~~~~~

"""
# pylint: disable=W0232
#         class has no __init__ method


import collections

import yaml  # pylint: disable=blacklisted-import

import salt.utils.context
from salt.utils.odict import OrderedDict

try:
    from yaml import CDumper as Dumper
    from yaml import CSafeDumper as SafeDumper
except ImportError:
    from yaml import Dumper, SafeDumper


__all__ = [
    "OrderedDumper",
    "SafeOrderedDumper",
    "IndentedSafeOrderedDumper",
    "get_dumper",
    "dump",
    "safe_dump",
]


class OrderedDumper(Dumper):
    """
    A YAML dumper that represents python OrderedDict as simple YAML map.
    """


class SafeOrderedDumper(SafeDumper):
    """
    A YAML safe dumper that represents python OrderedDict as simple YAML map.
    """


class IndentedSafeOrderedDumper(SafeOrderedDumper):
    """Like ``SafeOrderedDumper``, except it indents lists for readability."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def represent_ordereddict(dumper, data):
    return dumper.represent_dict(list(data.items()))


def represent_undefined(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:null", "NULL")


# OrderedDumper does not inherit from SafeOrderedDumper, so any applicable
# representers added to SafeOrderedDumper must also be explicitly added to
# OrderedDumper.

# TODO: Why does this representer exist?  It doesn't seem to do anything
# different compared to PyYAML's yaml.SafeDumper.
# TODO: Why isn't this representer also registered with OrderedDumper?
SafeOrderedDumper.add_representer(None, represent_undefined)

for D in (SafeOrderedDumper, OrderedDumper):
    D.add_representer(OrderedDict, represent_ordereddict)
    D.add_representer(
        collections.defaultdict, yaml.representer.SafeRepresenter.represent_dict
    )
    D.add_representer(
        salt.utils.context.NamespacedDictWrapper,
        yaml.representer.SafeRepresenter.represent_dict,
    )
    # TODO: This seems wrong: the first argument should be a type, not a tag.
    D.add_representer("tag:yaml.org,2002:timestamp", Dumper.represent_scalar)
del D


def get_dumper(dumper_name):
    return {
        "OrderedDumper": OrderedDumper,
        "SafeOrderedDumper": SafeOrderedDumper,
        "IndentedSafeOrderedDumper": IndentedSafeOrderedDumper,
    }.get(dumper_name)


def dump(data, stream=None, **kwargs):
    """
    .. versionadded:: 2018.3.0

    .. versionchanged:: 3006.0

        The default ``Dumper`` class is now ``OrderedDumper`` instead of
        ``yaml.Dumper``.

    Helper that wraps yaml.dump and ensures that we encode unicode strings
    unless explicitly told not to.
    """
    kwargs = {
        "allow_unicode": True,
        "default_flow_style": None,
        "Dumper": OrderedDumper,
        **kwargs,
    }
    return yaml.dump(data, stream, **kwargs)


def safe_dump(data, stream=None, **kwargs):
    """
    Use a custom dumper to ensure that defaultdict and OrderedDict are
    represented properly. Ensure that unicode strings are encoded unless
    explicitly told not to.
    """
    return dump(data, stream, Dumper=SafeOrderedDumper, **kwargs)
