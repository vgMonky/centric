from __future__ import annotations

from typing import Any

from tile_centric.ecs import Entity


def _parse_pos(pos: Any) -> tuple[int, int]:
    if not isinstance(pos, list) or len(pos) != 2:
        raise ValueError('pos must be [x, y]')

    x, y = pos
    if isinstance(x, bool) or isinstance(y, bool):
        raise ValueError('pos must contain two ints')
    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError('pos must contain two ints')

    return x, y


def _format_pos(x: int, y: int) -> list[int]:
    return [x, y]


def _normalize_dir(dir_val: Any) -> int:
    if isinstance(dir_val, str):
        try:
            dir_val = int(dir_val)
        except ValueError:
            dir_val = 0

    if not isinstance(dir_val, int) or isinstance(dir_val, bool):
        dir_val = 0

    return dir_val % 8


_DIR_DELTAS: dict[int, tuple[int, int]] = {
    0: (0, -1),
    1: (1, -1),
    2: (1, 0),
    3: (1, 1),
    4: (0, 1),
    5: (-1, 1),
    6: (-1, 0),
    7: (-1, -1),
}


def move_system(entities: list[Entity]) -> None:
    # For each entity that has walk component = true
    for ent in entities:
        comps = ent.components
        if comps.get('walk') is not True:
            continue

        # 1. Update entities with pos based on their dir
        x, y = _parse_pos(comps.get('pos'))
        dir_val = _normalize_dir(comps.get('dir'))
        dx, dy = _DIR_DELTAS[dir_val]
        ent.add_component('pos', _format_pos(x + dx, y + dy))

        # 2. Shift the matrix based on the `user` `dir` and `walk` state

        # 3. Generate and remove tiles based on `user` `reality_radius`