import pytest
from SIEP.utils import get_block_candidates


@pytest.mark.parametrize(
    "width, height, x_off, y_off, x_chunk, y_chunk, expected_blocks",
    [
        (
            10,
            20,
            5,
            6,
            5,
            4,
            [
                (5, 6, 5, 4),
                (5, 10, 5, 4),
                (5, 14, 5, 4),
                (5, 18, 5, 4),
                (5, 22, 5, 4),
                (10, 6, 5, 4),
                (10, 10, 5, 4),
                (10, 14, 5, 4),
                (10, 18, 5, 4),
                (10, 22, 5, 4),
            ],
        ),
    ],
)
def test_get_block_candidates(
    width, height, x_off, y_off, x_chunk, y_chunk, expected_blocks
):
    blocks = list(
        get_block_candidates(width, height, x_off, y_off, x_chunk, y_chunk)
    )
    assert blocks == expected_blocks
