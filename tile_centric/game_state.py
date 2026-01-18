from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random
import time
from typing import Any, Mapping

from tile_centric.ecs import Entity
from tile_centric.systems import _format_pos, move_system


def _now_ts() -> int:
    return time.time_ns()


def _make_state_id(index: int) -> str:
    return f'{index}_{_now_ts()}'


def _parse_state_index(state_id: Any) -> int:
    if not isinstance(state_id, str) or not state_id:
        raise ValueError('info.id must be a non-empty string')

    head = state_id.split('_', 1)[0]
    try:
        idx = int(head)
    except ValueError as e:
        raise ValueError('info.id must start with an int index') from e

    if idx < 0:
        raise ValueError('info.id index must be >= 0')

    return idx


@dataclass(slots=True)
class GameStateInfo:
    id: str
    parent_id: str | None


@dataclass(slots=True)
class GameState:
    info: GameStateInfo
    entities: list[Entity]

    def to_dict(self) -> dict[str, Any]:
        return {
            'info': {
                'id': self.info.id,
                'parent_id': self.info.parent_id,
            },
            'entities': [e.to_dict() for e in self.entities],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> 'GameState':
        raw_info = data.get('info')
        if not isinstance(raw_info, dict):
            raise ValueError('game_state.info must be a JSON object')

        id_val = raw_info.get('id')
        if not isinstance(id_val, str) or not id_val.strip():
            raise ValueError('info.id must be a non-empty string')

        parent_id = raw_info.get('parent_id')
        if parent_id is not None and not isinstance(parent_id, str):
            raise ValueError('info.parent_id must be a string or null')

        raw_entities = data.get('entities')
        if not isinstance(raw_entities, list):
            raise ValueError('game_state.entities must be a list')

        entities: list[Entity] = []
        for ent in raw_entities:
            if not isinstance(ent, dict):
                raise ValueError('entities must contain JSON objects')
            entities.append(Entity.from_dict(ent))

        info = GameStateInfo(id=id_val, parent_id=parent_id)
        return cls(info=info, entities=entities)

    @classmethod
    def read_json(cls, path: Path) -> 'GameState':
        raw = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(raw, dict):
            raise ValueError('game_state must be a JSON object')
        return cls.from_dict(raw)

    def write_json(self, path: Path) -> None:
        path.write_text(
            json.dumps(self.to_dict(), indent=4) + '\n',
            encoding='utf-8',
        )

    @classmethod
    def initial(cls, size: int = 3) -> 'GameState':
        if size <= 0 or size % 2 == 0:
            raise ValueError('size must be a positive odd integer')

        half = size // 2
        entities: list[Entity] = []

        for y in range(-half, half + 1):
            for x in range(-half, half + 1):
                e = Entity.create_entity()
                e.add_component('type', 'tile')
                e.add_component('pos', _format_pos(x, y))
                e.add_component('material', random.getrandbits(1))
                entities.append(e)

        userChar = Entity.create_entity()
        userChar.add_component('user', True)
        userChar.add_component('type', 'char')
        userChar.add_component('pos', _format_pos(0, 0))
        userChar.add_component('dir', 2)
        userChar.add_component('walk', True)
        entities.append(userChar)

        char = Entity.create_entity()
        char.add_component('type', 'char')
        char.add_component('pos', _format_pos(1, 1))
        char.add_component('dir', 7)
        char.add_component('walk', True)
        entities.append(char)

        return cls(
            info=GameStateInfo(id=_make_state_id(0), parent_id=None),
            entities=entities,
        )

    def step(self) -> 'GameState':
        entities = [e.clone() for e in self.entities]

        move_system(entities)

        next_index = _parse_state_index(self.info.id) + 1
        info = GameStateInfo(id=_make_state_id(next_index), parent_id=self.info.id)
        return GameState(info=info, entities=entities)
