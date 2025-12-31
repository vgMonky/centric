from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from tile_centric.config import load_config


def _parse_pos(pos: Any) -> tuple[int, int]:
    if not isinstance(pos, str):
        raise ValueError('pos must be a string like "x,y"')

    parts = pos.split(',')
    if len(parts) != 2:
        raise ValueError('pos must be "x,y"')

    try:
        x = int(parts[0].strip())
        y = int(parts[1].strip())
    except ValueError as e:
        raise ValueError('pos must contain two ints') from e

    return x, y


def _normalize_dir(dir_val: Any) -> int:
    if isinstance(dir_val, str):
        try:
            dir_val = int(dir_val)
        except ValueError:
            dir_val = 0

    if not isinstance(dir_val, int):
        dir_val = 0

    return dir_val % 8


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


def _load_game_state(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(raw, dict):
        raise ValueError('game_state must be a JSON object')
    return raw


def render_game_state(state: dict[str, Any]) -> str:
    entities = state.get('entities', [])
    if not isinstance(entities, list):
        raise ValueError('entities must be a list')

    tiles: dict[tuple[int, int], int] = {}
    chars: dict[tuple[int, int], int] = {}

    color_enabled = sys.stdout.isatty()

    for ent in entities:
        if not isinstance(ent, dict):
            continue
        comps = ent.get('components')
        if not isinstance(comps, dict):
            continue

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
                cell = f'[ {glyph} ]'
            elif (x, y) in tiles:
                if tiles[(x, y)] == 0:
                    cell = _gray('[   ]', color_enabled)
                else:
                    cell = '[   ]'
            else:
                cell = '     '
            row.append(cell)
        lines.append(''.join(row))

    return '\n'.join(lines)


def main(argv: list[str]) -> int:
    cfg = load_config()

    if len(argv) > 1:
        path = Path(argv[1])
    else:
        uuid = '00000000-0000-0000-0000-000000000000'
        path = Path(cfg.store_path) / f'{uuid}.json'

    state = _load_game_state(path)
    out = render_game_state(state)
    if out:
        print(out)

    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
