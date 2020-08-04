"""Useful Mixins for class code reuse"""
#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import re


class NamingMixin:
    """Provides convenience methods for pretty-printing user-facing classes."""

    @classmethod
    def get_common_name(cls):
        """"Return the human-readable, space-separated name for the class."""
        return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", cls.__name__)

    @classmethod
    def get_identifier(cls):
        return cls.__name__.lower()


class BaseClassMixin:
    """Provides convenience methods for tracking the progeny of Base classes."""

    @classmethod
    def get_children(cls):
        """Return all inheriting children as a list."""
        for child in cls.__subclasses__():
            yield from child.get_children()
            yield child


class WebFormMixin:
    form_path: str

    @classmethod
    def get_form(cls):
        return cls.form_path
