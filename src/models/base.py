from dataclasses import asdict
from datetime import datetime
from inspect import Parameter, signature
from types import MappingProxyType
from typing import Any, Callable
from typing_extensions import Self
from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass
from google.cloud import firestore

# IgnoreExtraArgs allows us to accept a minimum number of arguments in a pydantic basemodel so we can grab raw data from webhooks
# and put it into a typed class in the areas we need, but support any other kind of data for those kwargs we don't.

class _ArgTrimmer:
    """Just some fancy boilerplate that allows us to have `IgnoreExtraArgs` metaclass"""
    def __init__(self):
        self.new_args, self.new_kw = [], {}
        self.dispatch: dict[Parameter, Callable] = {
            Parameter.POSITIONAL_ONLY: self.pos_only,
            Parameter.KEYWORD_ONLY: self.kw_only,
            Parameter.POSITIONAL_OR_KEYWORD: self.pos_or_kw,
            Parameter.VAR_POSITIONAL: self.starargs,
            Parameter.VAR_KEYWORD: self.starstarkwargs,
        }

    def pos_only(self, p: Parameter, i: int, args: tuple, kwargs: dict[str, Any]):
        if i < len(args):
            self.new_args.append(args[i])

    def kw_only(self, p: Parameter, i: int, args: tuple, kwargs: dict[str, Any]):
        if p.name in kwargs:
            self.new_kw[p.name] = kwargs.pop(p.name)

    def pos_or_kw(self, p: Parameter, i: int, args: tuple, kwargs: dict[str, Any]):
        if i < len(args):
            self.new_args.append(args[i])
            # drop if also in kwargs, otherwise parameters collide
            # if there's a VAR_KEYWORD parameter to capture it
            kwargs.pop(p.name, None)
        elif p.name in kwargs:
            self.new_kw[p.name] = kwargs[p.name]

    def starargs(self, p: Parameter, i: int, args: tuple, kwargs: dict[str, Any]):
        self.new_args.extend(args[i:])

    def starstarkwargs(self, p: Parameter, i: int, args: tuple, kwargs: dict[str, Any]):
        self.new_kw.update(kwargs)

    def trim(self, params: MappingProxyType[str, Parameter], args: tuple, kwargs: dict[str, Any]):
        for i, p in enumerate(params.values()):
            if i:  # skip first (self or cls) arg of unbound function
                self.dispatch[p.kind](p, i - 1, args, kwargs)
        return self.new_args, self.new_kw

class IgnoreExtraArgs(ModelMetaclass):
    """A metaclass on top of pydantic's metaclass that allows additional arguments to be
    passed in a dictionary. This pattern allows us to handle a webhook body that may change
    without our control or knowledge.

    For example, if we want to have a webhook for company A, and all we need are two arguments
    from the body, we can define a smaller class and use this baseclass.
    ```
    class WebhookBody(BaseModel, metaclass=IgnoreExtraArgs):
        important_attribute: str
        other_important_attr: datetime.datetime
    ```
    Even if the webhook body has 100 attributes, we will ignore those other 98 and still get
    typed attrs (i.e. will convert the `other_important_attr` to a `datetime.datetime` class)
    for the important two we want from the webhook body.
    """
    def __call__(cls, *args, **kwargs):
        if cls.__new__ is not object.__new__:
            func = cls.__new__
        else:
            func = getattr(cls, '__init__', None)
        if func is not None:
            sig = signature(func)
            args, kwargs = _ArgTrimmer().trim(sig.parameters, args, kwargs)
        return super().__call__(*args, **kwargs)

# This base model will be used to grab values to and from Firebase

class _Metadata(BaseModel, metaclass=IgnoreExtraArgs):
    updated_time: datetime = Field(default_factory=datetime.utcnow)
    created_time: datetime = Field(default_factory=datetime.utcnow)
    path: str | None = None


class Base(BaseModel):
    metadata: _Metadata = Field(default_factory=_Metadata, alias='_metadata')

    @property
    def uid(self) -> str:
        if not self.metadata.path:
            raise ValueError(f"No path in metadata for {self} --> cannot generate a uid")
        return self.metadata.path.split('/')[-1]

    @property
    def ref(self) -> firestore.DocumentReference:
        if not self.metadata.path:
            raise ValueError(f"No path in metadata for {self} --> cannot generate a doc reference")
        return firestore.DocumentReference(self.metadata.path) if self.metadata.path else None

    def to_dict(self, *args, **kwargs) -> dict:
        """Wrapper for `BaseModel.dict` method. To see options, look at `.dict` instead of `.to_dict`.
        Sets an updated_time in _metadata and modifies pydantic's `dict()` defaults.
        
        Overwritten defaults:
        ```
        by_alias=True
        exclude_none=True
        ```"""
        self.metadata.updated_time = datetime.utcnow()
        return self.dict(*args, by_alias=True, exclude_none=True, **kwargs)

    @classmethod
    def from_snapshot(cls, snap: firestore.DocumentSnapshot) -> Self:
        d = snap.to_dict()
        metadata = d.get("_metadata", _Metadata())
        try:
            metadata.path = snap.reference.path
        except AttributeError:
            metadata['path'] = snap.reference.path
        d["_metadata"] = metadata
        return cls(**d)

    def __repr__(self) -> str:
        return f'<{type(self)}>'