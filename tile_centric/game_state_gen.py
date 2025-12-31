from __future__ import annotations

import random
import json
from pathlib import Path

from tile_centric.config import load_config
from tile_centric.ecs import Entity


ZERO_UUID = '00000000-0000-0000-0000-000000000000'


def generate_game_state(size: int = 3) -> dict:
    if size <= 0 or size % 2 == 0:
        raise ValueError('size must be a positive odd integer')

    half = size // 2
    entities: list[Entity] = []

    for y in range(-half, half + 1):
        for x in range(-half, half + 1):
            e = Entity.create_entity()
            e.add_component('type', 'tile')
            e.add_component('pos', f'{x},{y}')
            e.add_component('material', random.getrandbits(1))
            entities.append(e)

    char = Entity.create_entity()
    char.add_component('type', 'char')
    char.add_component('pos', '0,0')
    char.add_component('dir', 2)
    entities.append(char)

    return {
        'info': {
            'uuid': ZERO_UUID,
            'parent_uuid': None,
        },
        'entities': [e.to_dict() for e in entities],
    }


def main() -> None:
    cfg = load_config()
    out_dir = Path(cfg.store_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f'{ZERO_UUID}.json'
    state = generate_game_state(size=3)

    out_path.write_text(
        json.dumps(state, indent=4) + '\n',
        encoding='utf-8',
    )

    print(out_path)


if __name__ == '__main__':
    main()
