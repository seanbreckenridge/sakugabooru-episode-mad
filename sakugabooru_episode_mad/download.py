import time
import json
from urllib.parse import urlparse
from typing import Any, Optional, Dict
from pathlib import Path

import click
import requests
import backoff


# https://www.sakugabooru.com/help/api
# backoff handler if 421
@backoff.on_exception(
    lambda: backoff.expo(base=15), requests.exceptions.HTTPError, max_time=60
)
def request_json(url: str) -> Any:
    click.echo(f"Requesting {url}", err=True)
    time.sleep(2)
    res = requests.get(url)
    if res.status_code == 421:
        time.sleep(30)
        res.raise_for_status()
    res.raise_for_status()
    return res.json()


def download_post(
    post: Dict[str, Any],
    skip_downloading_media: bool,
    output_folder: str,
    score_over: Optional[int],
) -> None:
    file_url = post["file_url"]
    file_extension = urlparse(file_url).path.split(".")[-1]
    target_file = Path(output_folder) / f"{post['id']}.{file_extension}"
    target_data = Path(output_folder) / f"{post['id']}.json"

    if target_file.exists() and target_data.exists():
        click.echo(f"Skipping {post['id']}, already downloaded", err=True)
        return

    # write to JSON file
    click.echo(f"Writing {post['id']}.json", err=True)
    with open(target_data, "w") as f:
        f.write(json.dumps(post))

    if skip_downloading_media:
        click.echo(json.dumps(post))
        return

    if score_over is not None and post["score"] < score_over:
        click.echo(
            f"Skipping {post['id']}, score {post['score']} < {score_over}", err=True
        )
        return

    click.echo(f"Downloading {post['id']} to {target_file}", err=True)
    with open(target_file, "wb") as f:
        for chunk in requests.get(file_url, stream=True).iter_content(chunk_size=1024):
            f.write(chunk)
    time.sleep(1)


def download_bulk(
    tags: str,
    skip_downloading_media: bool,
    output_folder: str,
    only_animated: bool,
    score_over: Optional[int],
) -> None:
    if only_animated:
        tags += "+animated"
    tags_base = f"https://www.sakugabooru.com/post.json?tags={tags}"
    page = 1

    if not Path(output_folder).exists():
        Path(output_folder).mkdir()

    while True:
        url = f"{tags_base}&limit=100&page={page}"
        res = request_json(url)
        assert isinstance(res, list)

        for post in res:
            download_post(post, skip_downloading_media, output_folder, score_over)

        if len(res) == 0:
            click.echo("No more posts to download.", err=True)
            break

        page += 1
