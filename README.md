# sakugabooru-episode-mad

Downloads all sakugabooru posts for a particular tag, and optionally lets you combine them into Source(episode)-based videos using ffmpeg

## Installation

Requires `python3.7+`

To install with pip, run:

```
pip install git+https://github.com/seanbreckenridge/sakugabooru_episode_mad
```

## Usage

```
Usage: python -m sakugabooru_episode_mad download [OPTIONS] TAG

  Download posts from Sakugabooru

Options:
  --download / --skip-download    download media, or just grab medata from
                                  each post
  -S, --skip-score-under INTEGER  skip posts with score under this value
  -o, --output-folder TEXT        output folder
  --only-animated / --all         only download animated posts, or all posts
  --help                          Show this message and exit.
```

`sakugabooru_episode_mad download <tag name>` to download all posts with that tag

Once thats done, you can `merge` them into a video using the `Source` metadata from each post. Typically, that is an episode, but if its from a movie/OP/ED, it'll just be marked as `Episode 0`

```
Usage: python -m sakugabooru_episode_mad process [OPTIONS] FOLDER

  Process/List downloaded posts

Options:
  -s, --sort-by TEXT
  -o, --output-type [json|media_path|id|url|file_url|merge_videos]
  -g, --group-by [source]         group by source, or not when merging into
                                  combined video
  --reverse / --no-reverse        reverse sort order
  --help                          Show this message and exit.
```

There are some `--output-type`s to just view the data from the JSON files, otherwise if you want to merge the downloaded videos, use something like:

```
sakugabooru_episode_mad process --output-type merge_videos --group-by source <folder>
```
