from __future__ import annotations

import sys
from pathlib import Path

from tile_centric.config import load_config
from tile_centric.game_state import GameState


def _usage(prog: str) -> int:
    print('usage:', file=sys.stderr)
    print(f'  {prog} gen [size]', file=sys.stderr)
    print(f'  {prog} step [path-to-game-state.json]', file=sys.stderr)
    return 2


def _parse_store_entry(path: Path) -> tuple[int, int] | None:
    stem = path.stem
    parts = stem.split('_', 1)
    if len(parts) != 2:
        return None

    try:
        idx = int(parts[0])
        ts = int(parts[1])
    except ValueError:
        return None

    if idx < 0:
        return None

    return idx, ts


def _find_latest_state_path(store_dir: Path) -> Path | None:
    best: tuple[int, int] | None = None
    best_path: Path | None = None

    for p in store_dir.glob('*.json'):
        parsed = _parse_store_entry(p)
        if parsed is None:
            continue

        if best is None or parsed > best:
            best = parsed
            best_path = p

    return best_path

# commands
def _cmd_gen(argv: list[str]) -> int:
    size = 3
    if len(argv) == 1:
        try:
            size = int(argv[0])
        except ValueError:
            print('error: size must be an int', file=sys.stderr)
            return 2
    elif len(argv) > 1:
        print('error: too many args for gen', file=sys.stderr)
        return 2

    state = GameState.initial(size=size)

    cfg = load_config()
    out_dir = Path(cfg.store_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f'{state.info.id}.json'
    state.write_json(out_path)
    print(out_path)
    return 0


def _cmd_step(argv: list[str]) -> int:
    if len(argv) > 1:
        print('error: step expects at most one input path', file=sys.stderr)
        return 2

    cfg = load_config()
    out_dir = Path(cfg.store_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    if len(argv) == 1:
        in_path = Path(argv[0])
    else:
        in_path = _find_latest_state_path(out_dir)
        if in_path is None:
            print(
                f'error: no game states found in: {out_dir}',
                file=sys.stderr,
            )
            return 2

    if not in_path.exists():
        print(f'error: file not found: {in_path}', file=sys.stderr)
        return 2

    state = GameState.read_json(in_path)

    walk = True
    next_state = state.step(walk=walk)

    out_path = out_dir / f'{next_state.info.id}.json'
    next_state.write_json(out_path)
    print(out_path)
    return 0


def main(argv: list[str]) -> int:
    prog = Path(argv[0]).name if argv else 'run.py'
    if len(argv) < 2:
        return _usage(prog)

    cmd = argv[1]
    args = argv[2:]

    if cmd == 'gen':
        return _cmd_gen(args)

    if cmd == 'step':
        return _cmd_step(args)

    print(f'error: unknown command: {cmd}', file=sys.stderr)
    return _usage(prog)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
