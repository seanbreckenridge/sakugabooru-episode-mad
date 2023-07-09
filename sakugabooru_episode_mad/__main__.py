import json
import tempfile
import subprocess
from typing import Optional, List, Dict
from pathlib import Path

import click

from .download import download_bulk
from .process import Item


@click.group()
def main() -> None:
    pass


@main.command(short_help="download posts from sakugabooru")
@click.option(
    "--download/--skip-download",
    is_flag=True,
    default=True,
    help="download media, or just grab medata from each post",
)
@click.option(
    "-S",
    "--skip-score-under",
    type=int,
    default=None,
    help="skip posts with score under this value",
)
@click.option(
    "-o",
    "--output-folder",
    help="output folder",
    type=str,
)
@click.option(
    "--only-animated/--all",
    is_flag=True,
    default=True,
    help="only download animated posts, or all posts",
)
@click.argument("TAG", required=True, type=str)
def download(
    output_folder: Optional[str],
    tag: str,
    download: bool,
    only_animated: bool,
    skip_score_under: Optional[int],
) -> None:
    """
    Download posts from Sakugabooru
    """
    if not output_folder:
        output_folder = "".join(e for e in tag if e.isalnum() or e in "-_")
    download_bulk(tag, not download, output_folder, only_animated, skip_score_under)


@main.command(name="process", short_help="process downloaded posts")
@click.option(
    "-s",
    "--sort-by",
    type=str,
)
@click.option(
    "-o",
    "--output-type",
    type=click.Choice(["json", "media_path", "id", "url", "file_url", "merge_videos"]),
    default="json",
)
@click.option(
    "-g",
    "--group-by",
    type=click.Choice(["source"]),
    default=None,
    help="group by source, or not when merging into combined video",
)
@click.option(
    "--reverse/--no-reverse",
    is_flag=True,
    default=False,
    help="reverse sort order",
)
@click.argument(
    "FOLDER",
    required=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
)
def _list(
    folder: Path,
    output_type: str,
    reverse: bool,
    sort_by: Optional[str],
    group_by: Optional[str],
) -> None:
    """
    Process/List downloaded posts
    """
    items = Item.parse_folder(folder)
    if sort_by:
        items = Item.sort_by(items, sort_by, reverse)

    if output_type == "merge_videos":
        items = list(filter(lambda item: item.is_video, items))

    for item in items:
        if output_type == "json":
            click.echo(json.dumps(item.data))
        elif output_type == "media_path":
            click.echo(item.media_path)
        elif output_type == "id":
            click.echo(item.data["id"])
        elif output_type == "url":
            click.echo(f"https://www.sakugabooru.com/post/show/{item.data['id']}")
        elif output_type == "file_url":
            click.echo(item.data["file_url"])
        else:
            assert output_type == "merge_videos"

    if output_type != "merge_videos":
        return

    # merge videos
    grouped_items: Dict[str, List[Item]]
    if group_by is None:
        grouped_items = {"all": items}
    else:
        grouped_items = {
            str(group): group_items
            for group, group_items in Item.group_by(items, group_by).items()
        }

    # output dir
    output_dir = folder / "merged"
    output_dir.mkdir(exist_ok=True)

    # merge videos
    for output_name, items in grouped_items.items():
        # ffmpeg them all together
        output_stem = output_name
        if output_name.isdigit():
            output_stem = output_name.zfill(4)  # prepend zeros
        output_path = output_dir / f"{output_stem}.mkv"

        # create a manifest .txt file that lets user know what these all were
        with open(output_path.with_suffix(".txt"), "w") as manifest:
            for item in items:
                manifest.write(
                    f"https://www.sakugabooru.com/post/show/{item.data['id']}\n"
                )

        if output_path.exists():
            click.echo(f"Skipping {output_path}", err=True)
            continue

        with tempfile.NamedTemporaryFile() as f:
            # create input file for ffmpeg
            for item in items:
                f.write(f"file '{item.media_path.absolute()}'\n".encode("utf-8"))
            f.flush()

            click.echo(f"Merging {output_path}", err=True)
            cmd = ["ffmpeg", "-y"]
            # input file
            cmd.extend(["-f", "concat", "-safe", "0", "-i", f.name])
            # output file
            cmd.append(str(output_path.absolute()))
            click.echo(" ".join(cmd), err=True)
            subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
