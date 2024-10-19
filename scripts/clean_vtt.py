# pip install webvtt-py
import argparse
import io
from pathlib import Path

import webvtt
from tqdm import tqdm


def vtt_clean(vtt_content, same_line=False):
    result_lines, last_line = [], None
    for caption in webvtt.read_buffer(io.StringIO(vtt_content)):
        new_lines = caption.text.strip().splitlines()
        for line in new_lines:
            line = line.strip()
            if not line or line == last_line:
                continue
            result_lines.append(f"{str(caption.start).split('.')[0]} {line}\n" if not same_line else f"{line} ")
            last_line = line
    return "".join(result_lines)


parser = argparse.ArgumentParser()
parser.add_argument("input_path", type=Path)
parser.add_argument("output_path", type=Path)
args = parser.parse_args()

for filename in tqdm(args.input_path.glob("*.vtt")):
    new_filename = args.output_path / filename.name
    if new_filename.exists():
        continue
    with filename.open() as fobj:
        data = fobj.read()
    result = vtt_clean(data)
    with new_filename.open(mode="w") as fobj:
        fobj.write(result)
