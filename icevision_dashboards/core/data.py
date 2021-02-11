# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/core.data.ipynb (unless otherwise specified).

__all__ = ['Observable', 'ObservableList', 'DatasetDescriptor', 'StringDescriptor', 'GenericDataset']

# Cell
from typing import Union, Optional, Any, Iterable, Callable
import os
import shutil
from abc import ABC, abstractmethod

# Cell
class Observable(ABC):
    """Simple implementation of the observer pattern."""
    def __init__(self):
        self._callbacks = []

    def register_callback(self, callback: Callable):
        self._callbacks.append(callback)

    def trigger_callbacks(self):
        for callback in self._callbacks:
            callback(self)

# Cell
class ObservableList(Observable):
    """List with observer pattern"""
    def __init__(self, observable_list: list):
        self._list = observable_list
        super().__init__()

    @property
    def list(self):
        return self._list

    @list.setter
    def list(self, value: Any):
        self._list = value
        self.trigger_callbacks()

    def __repr__(self):
        return self._list.__repr__()

    def __iter__(self):
        for item in self._list:
            yield item

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index: int):
        return self._list[index]

    def __setitem__(self, index: int, value: Any):
        self._list[index] = value
        self.trigger_callbacks()

    def append(self, item: Any):
        self._list.append(item)
        self.trigger_callbacks()

    def remove(self, item: Any):
        self._list.remove(item)
        self.trigger_callbacks()

    def insert(self, index: int, item: Any):
        self._list.insert(index, item)
        self.trigger_callbacks()

    def pop(self, index: int = -1):
        poped_item = self._list.pop(index)
        self.trigger_callbacks()
        return poped_item

    def extend(self, iterable: Iterable):
        self._list.extend(iterable)
        self.trigger_callbacks()

    def clear(self):
        self._list = []

    def count(self, item):
        return self._list.count(item)

    def index(self, item, start=0, stop=9223372036854775807):
        return self._list.index(item, start=start, stop=stop)

    def reverse(self):
        self._list.reverse()

    def sort(self, key, reverse=False):
        self._list.sort(key, reverse=reverse)

# Cell
class DatasetDescriptor(ABC):
    def __set_name__(self, owner, name):
        owner._descriptors.append(self)
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        if getattr(obj, self.private_name) is None:
            value = self.calculate_description(obj)
            setattr(obj, self.private_name, value)
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if value is None:
            setattr(obj, self.private_name, value)
        else:
            raise ValueError("Attribute can externaly only be set to None")

    @abstractmethod
    def calculate_description(self, obj):
        pass

# Cell
class StringDescriptor:
    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)

# Cell
class GenericDataset:
    _descriptors = []

    name = StringDescriptor()
    description = StringDescriptor()

    def __init__(self, base_data, name: Optional[str] = None, description: Optional[str] = None):
        self.base_data = base_data
        self.name = name
        self.description = description
        super().__init__()

    def reset_infered_data(self, new_data=None):
        """Takes on argument to be compatible with panel."""
        for descriptor in self._descriptors:
            descriptor.__set__(self, None)