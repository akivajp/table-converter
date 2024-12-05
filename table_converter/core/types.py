'''
This module contains the dataclasses that are used to define the configuration
for the table_converter package.
'''

import dataclasses

from collections import (
    OrderedDict,
    defaultdict,
)
from dataclasses import dataclass
from typing import (
    Any,
    Literal,
    Mapping,
)

@dataclasses.dataclass
class Row:
    flat: OrderedDict
    nested: OrderedDict

@dataclasses.dataclass
class AssignConstantConfig:
    target: str
    value: Any

@dataclasses.dataclass
class AssignFormatConfig:
    target: str
    format: str

@dataclasses.dataclass
class AssignIdConfig:
    target: str
    primary: list[str]
    context: list[str] | None = None

@dataclasses.dataclass
class FilterConfig:
    field: str
    operator: Literal['==', '!=', '>', '>=', '<', '<=', 'not-in']
    value: str | list[str]

@dataclasses.dataclass
class PickConfig:
    target: str
    source: str

@dataclasses.dataclass
class SplitConfig:
    target: str
    source: str
    delimiter: str | None = None

ActionConfig = \
    AssignIdConfig | \
    AssignConstantConfig | \
    AssignFormatConfig | \
    FilterConfig | \
    SplitConfig


type ContextColumnTuple = tuple[str]
type ContextValueTuple = tuple 
type PrimaryColumnTuple = tuple[str]
type PrimaryValueTuple = tuple

@dataclasses.dataclass
class IdMap:
    max_id: int = 0
    dict_value_to_id: Mapping[PrimaryValueTuple, int] = \
        dataclasses.field(default_factory=defaultdict)
    dict_id_to_value: Mapping[int, PrimaryValueTuple] = \
        dataclasses.field(default_factory=defaultdict)

type IdContextMap = Mapping[
    (
        ContextColumnTuple,
        ContextValueTuple,
        PrimaryColumnTuple,
    ),
    IdMap
]

@dataclasses.dataclass
class GlobalStatus:
    id_context_map: IdContextMap = \
        dataclasses.field(default_factory=lambda: defaultdict(IdMap))
