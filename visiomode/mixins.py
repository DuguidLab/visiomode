"""Useful Mixins for class code reuse"""
#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import os
import re
import yaml
import logging


class BaseClassMixin:
    """Provides convenience methods for identifying and tracking the progeny of Base classes."""

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
        """Generate lowercase identifier for the class."""
        return cls.__name__.lower()

    @classmethod
    def get_common_name(cls):
        """"Return the human-readable, space-separated name for the class."""
        return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", cls.__name__)


class WebFormMixin:
    """Webform UI for class parameters."""

    form_path: str

    @classmethod
    def get_form(cls):
        return cls.form_path


class YamlAttributesMixin:
    """Load and save class attributes as YAML files."""

    def load_yaml(self, path):
        """Loads YAML file parameters as class attributes.

        Args:
            path: Path to config YAML.
        """
        if not path or not os.path.exists(path):
            return
        with open(path) as f:
            attrs = yaml.safe_load(f)
            for key, value in attrs.items():
                if key not in self.__dict__.keys():
                    logging.info(
                        "{} is not a valid config parameter, skipping...".format(key)
                    )
                    continue
                setattr(self, key, value)

    def save_yaml(self, path, exclude=None):
        """Save class attributes as a YAML file."""
        pass
