from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Mapping


class Component:
    kind: ClassVar[str] = 'component'

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> 'Component':
        return cls(**dict(data))



@dataclass(slots=True)
class Entity:
    id: int
    components: dict[str, Any] = field(default_factory=dict)

    _next_id: ClassVar[int] = 0

    @classmethod
    def create_entity(cls) -> 'Entity':
        entity_id = cls._next_id
        cls._next_id += 1
        return cls(id=entity_id)

    @classmethod
    def _bump_next_id(cls, entity_id: int) -> None:
        if entity_id >= cls._next_id:
            cls._next_id = entity_id + 1

    def add_component(self, kind: str, value: Any) -> None:
        self.components[kind] = value

    def remove_component(self, kind: str) -> None:
        self.components.pop(kind, None)

    def get_component(self, kind: str) -> Any | None:
        return self.components.get(kind)

    def to_dict(self) -> dict[str, Any]:
        return {'id': self.id, 'components': dict(self.components)}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> 'Entity':
        entity_id = data.get('id')
        if not isinstance(entity_id, int):
            raise ValueError('Entity.id must be int')

        comps = data.get('components', {})
        if not isinstance(comps, dict):
            raise ValueError('Entity.components must be dict')

        ent = cls(id=entity_id, components=dict(comps))
        cls._bump_next_id(entity_id)
        return ent
