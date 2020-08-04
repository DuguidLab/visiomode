"""Useful Mixins for class code reuse"""
#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import re


class BaseClassMixin:
    """Provides convenience methods for identifying and  tracking the progeny of Base classes."""

    @classmethod
    def get_children(cls):
        """Return all inheriting children as a list."""
        for child in cls.__subclasses__():
            yield from child.get_children()
            yield child

    @classmethod
    def get_child(cls, child_id):
        children = cls.get_children()
        for child in children:
            if child.get_identifier() == child_id:
                return child

    @classmethod
    def get_identifier(cls):
        return cls.__name__.lower()


class WebFormMixin:
    form_path: str

    @classmethod
    def get_form(cls):
        return cls.form_path

    @classmethod
    def get_common_name(cls):
        """"Return the human-readable, space-separated name for the class."""
        return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", cls.__name__)
