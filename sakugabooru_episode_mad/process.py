from __future__ import annotations

import json
import itertools
from pathlib import Path
from functools import cached_property
from typing import List, Dict, Any
from dataclasses import dataclass

import click


def _process_episode_source(data: str) -> int:
    if data.startswith("#"):
        data = data.strip("#")
        if data.isdigit():
            return int(data)
        try:
            return int(data.split(" ")[0])
        except ValueError:
            click.echo(f"Error: could not parse episode number from {data}", err=True)
            return 0
    return 0


@dataclass
class Item:
    data_path: Path
    media_path: Path

    @cached_property
    def data(self) -> Dict[str, Any]:
        with self.data_path.open("r") as f:
            return json.load(f)  # type: ignore[no-any-return]

    @staticmethod
    def parse_folder(folder: Path) -> List[Item]:
        """Process a folder."""
        items: List[Item] = []
        all_files = list(folder.iterdir())
        for file in (f for f in all_files if f.is_file() and f.suffix == ".json"):
            # find filename attached to this with same stem
            media = [
                f for f in all_files if f.stem == file.stem and f.name != file.name
            ]
            if not media:
                click.echo(
                    f"Error: could not find file assosiated with {file}", err=True
                )
                continue
            items.append(Item(file, media[0]))

        return items

    @staticmethod
    def sort_by(data: List[Item], key: str, reverse: bool) -> List[Item]:
        return sorted(data, key=lambda item: item.data[key], reverse=reverse)  # type: ignore[no-any-return]

    @staticmethod
    def group_by(data: List[Item], key: str) -> Dict[int, List[Item]]:
        assert key in {"source"}
        groups = {}

        grouped = itertools.groupby(
            sorted(data, key=lambda item: _process_episode_source(item.data[key])),
            key=lambda item: _process_episode_source(item.data[key]),
        )
        # internally, sort by score (descending, best stuff first)
        for group, items in grouped:
            groups[group] = sorted(
                items, key=lambda item: int(item.data.get("score", 0)), reverse=True
            )

        return groups

    @property
    def is_video(self) -> bool:
        return self.media_path.suffix in [".mp4", ".webm", ".mkv"]
