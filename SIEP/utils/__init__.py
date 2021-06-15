import numpy as np
from typing import Iterable, List, Tuple


def get_block_candidates(
    width: int,
    height: int,
    x_off: int = 0,
    y_off: int = 0,
    x_chunk: int = 128,
    y_chunk: int = 128,
) -> Iterable[Tuple[int, int, int, int]]:
    """Get blocks of given chunk sizes for cartesian space starting with x and y
    offset and having given width and height.
        
    Yields:
        tuple[int, int, int, int]: Blocks with (x offset, y offest, width, height)
    """
    if width > x_chunk:
        x_start = x_off
        x_end = width + x_off
        x_offsets = np.arange(x_start, x_end, x_chunk)
        widths = list(x_offsets[1:] - x_offsets[:-1])
        widths.append(x_end - x_offsets[-1])
    else:
        x_offsets = [x_off]
        widths = [width]

    if height > y_chunk:
        y_start = y_off
        y_end = y_off + height
        y_offsets = np.arange(y_start, y_end, y_chunk)
        heights = list(y_offsets[1:] - y_offsets[:-1])
        heights.append(y_end - y_offsets[-1])
    else:
        y_offsets = [y_off]
        heights = [height]

    for w, chunk_x_off in zip(widths, x_offsets):
        for h, chunk_y_off in zip(heights, y_offsets):
            yield (chunk_x_off, chunk_y_off, w, h)
