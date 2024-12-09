"""Useful Mixins for class code reuse."""

#  This file is part of visiomode.
#  Copyright (c) 2020 Constantinos Eleftheriou <Constantinos.Eleftheriou@ed.ac.uk>
#  Distributed under the terms of the MIT Licence.
import re


class BaseClassMixin:
    """Provides convenience methods for identifying and tracking the progeny of Base classes.

    This mixin provides a class method for generating a lowercase identifier for
    the class, and a class method for generating a human-readable name for the
    class. It also provides a class method for returning all inheriting children
    as a list, and a class method for returning a child class with a matching
    identifier.
    """

    @classmethod
    def get_children(cls):
        """Return all inheriting children as a list.

        Returns:
            List of child classes.
        """
        for child in cls.__subclasses__():
            yield from child.get_children()
            yield child

    @classmethod
    def get_child(cls, child_id):
        """Return child class with matching identifier.

        Args:
            child_id: String identifier for child class.

        Returns:
            Child class with matching identifier.
        """
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
        """Return the human-readable, space-separated name for the class."""
        return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", cls.__name__)


class WebFormMixin:
    """Webform UI for class parameters.

    This mixin provides a class method for generating a webform for the class
    parameters, and a class attribute for specifying the path to the form
    template.
    """

    form_path: str

    @classmethod
    def get_form(cls):
        """Generate webform for class parameters.

        Returns:
            String path to webform html file.
        """
        return cls.form_path


class TaskEventsMixin:
    """Interface declarations for methods handling task events.

    This mixin provides a set of interface declarations for methods that handle
    task events. These methods are called by the task runner at
    appropriate times during the experiment, and can be overridden by the
    task class to implement custom behaviour.
    """

    def on_task_start(self):
        """Called when the task is started."""
        pass

    def on_trial_start(self):
        """Called when a trial is started."""
        pass

    def on_stimulus_start(self):
        """Called when a stimulus is presented."""
        pass

    def on_trial_end(self):
        """Called when a trial is ended."""
        pass

    def on_task_end(self):
        """Called when the task is ended."""
        pass

    def on_correct(self):
        """Called during a correct response."""
        pass

    def on_incorrect(self):
        """Called during an incorrect response."""
        pass

    def on_no_response(self):
        """Called if a trial ends with no response."""
        pass

    def on_precued(self):
        """Called if there is a response prior to stimulus presentation."""
        pass
