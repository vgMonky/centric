from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib


@dataclass(frozen=True)
class Config:
    store_path: Path


def _default_config_path() -> Path:
    """
    Resolve config.toml from the repo root by default:
    <repo>/config.toml when this file is <repo>/tile_centric/config.py
    """
    return Path(__file__).resolve().parents[1] / "config.toml"


def load_config(config_path: str | os.PathLike[str] | None = None) -> Config:
    path = Path(config_path) if config_path is not None else _default_config_path()

    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Config file not found: {path}") from e

    store_path_val = raw.get("store_path")
    if not isinstance(store_path_val, str) or not store_path_val.strip():
        raise ValueError('config.toml must define a non-empty string key: "store_path"')

    store_path = Path(store_path_val).expanduser()

    return Config(store_path=store_path)

