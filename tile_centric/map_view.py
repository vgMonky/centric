from __future__ import annotations

import sys
from typing import Any

from tile_centric.game_state import GameState
from tile_centric.systems import _normalize_dir, _parse_pos


def _parse_int(val: Any, default: int) -> int:
    if isinstance(val, bool):
        return default
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            return default
    return default


def _gray(text: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f'\x1b[90m{text}\x1b[0m'


def render_game_state(state: GameState) -> str:
    tiles: dict[tuple[int, int], int] = {}
    chars: dict[tuple[int, int], int] = {}

    color_enabled = sys.stdout.isatty()

    for ent in state.entities:
        comps = ent.components

        ent_type = comps.get('type')
        pos = comps.get('pos')
        if ent_type not in ('tile', 'char'):
            continue

        x, y = _parse_pos(pos)
        if ent_type == 'tile':
            material = _parse_int(comps.get('material', 1), 1)
            tiles[(x, y)] = 1 if material else 0
        else:
            dir_val = _normalize_dir(comps.get('dir', 0))
            chars[(x, y)] = dir_val

    if not tiles:
        return ''

    xs = [p[0] for p in tiles.keys()]
    ys = [p[1] for p in tiles.keys()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    lines: list[str] = []
    for y in range(min_y, max_y + 1):
        row: list[str] = []
        for x in range(min_x, max_x + 1):
            if (x, y) in chars:
                dir_val = chars[(x, y)]
                glyph = {
                    0: '↑',
                    1: '↗',
                    2: '→',
                    3: '↘',
                    4: '↓',
                    5: '↙',
                    6: '←',
                    7: '↖',
                }[dir_val]
                if tiles.get((x, y)) == 0:
                    left = _gray('[', color_enabled)
                    right = _gray(']', color_enabled)
                    cell = f'{left}{glyph}{right}'
                else:
                    cell = f'[{glyph}]'
            elif (x, y) in tiles:
                if tiles[(x, y)] == 0:
                    cell = _gray('[ ]', color_enabled)
                else:
                    cell = '[ ]'
            else:
                cell = '   '
            row.append(cell)
        lines.append(''.join(row))

    return '\n'.join(lines)
