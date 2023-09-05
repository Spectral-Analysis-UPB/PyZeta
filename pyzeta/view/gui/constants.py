"""
Module containing some named constants used in the `pyzeta.view.gui` package.

Authors:\n
- Philipp Schuette\n
- Sebastian Albrecht\n
"""

from typing import Dict, Final, List, Tuple

import numpy as np
from bokeh.palettes import (
    Cividis256,
    Greys256,
    Inferno256,
    Magma256,
    Plasma256,
    Turbo256,
    Viridis256,
)
from numpy.typing import NDArray

CMAPS: Final[Dict[str, Tuple[str, ...]]] = {
    "Greys": Greys256,
    "Inferno": Inferno256,
    "Magma": Magma256,
    "Plasma": Plasma256,
    "Viridis": Viridis256,
    "Cividis": Cividis256,
    "Turbo": Turbo256,
}
MARKERS: Final[List[str]] = ["circle", "diamond", "triangle", "square", "hex"]

DEFAULT_RES_R: Final[NDArray[np.int32]] = np.array(
    [
        -12,
        -12,
        -12,
        -12,
        -12,
        -12,
        -12,
        -12,
        -11,
        -10,
        -9,
        -8,
        -8,
        -9,
        -10,
        -11,
        -8,
        -8,
        -8,
        -8,
        -7,
        -7,
        -7,
        -6,
        -6,
        -6,
        -6,
        -4,
        -3,
        -2,
        -1,
        0,
        1,
        1,
        0,
        -1,
        -2,
        -3,
        -4,
        -4,
        -3,
        -2,
        -1,
        0,
        1,
        4,
        5,
        5,
        5,
        4,
        3,
        3,
        3,
        3,
        3,
        4,
        5,
        7,
        8,
        9,
        8,
        8,
        8,
        8,
        8,
        8,
        8,
        13,
        13,
        13,
        13,
        12,
        11,
        11,
        11,
        11,
        11,
        12,
        13,
        14,
    ],
    dtype=np.int32,
)
DEFAULT_RES_I: Final[NDArray[np.int32]] = np.array(
    [
        -1,
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        6,
        6,
        6,
        5,
        4,
        3,
        3,
        3,
        2,
        1,
        0,
        -1,
        -2,
        -3,
        -4,
        -1,
        0,
        1,
        2,
        6,
        6,
        6,
        6,
        6,
        6,
        5,
        4,
        3,
        2,
        1,
        0,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        1,
        1,
        2,
        3,
        3,
        3,
        2,
        1,
        0,
        -1,
        -1,
        -1,
        3,
        3,
        3,
        6,
        5,
        4,
        2,
        1,
        0,
        -1,
        0,
        1,
        2,
        3,
        3,
        3,
        2,
        1,
        0,
        -1,
        -1,
        -1,
        -1,
    ],
    dtype=np.int32,
)

STR_STYLE_GREEN: Final[str] = "style='color:#008b02;'"
STR_STYLE_RED: Final[str] = "style='color:#b80000;'"

STR_LOAD_EXPLAIN: Final[str] = (
    "<p>Use the <i>Load/Clear</i> widget above to load resonance data from "
    + "up to five different files.</p>"
)
STR_CLEAR_EXPLAIN: Final[str] = (
    "<p>To clear specific or all data from the figure, use the above "
    + "<i>Load/Clear</i> widget.</p>"
)
STR_SAVE_REMINDER: Final[str] = (
    "<p>Current selection is <b>unsaved</b>. Use the above <i>Save</i> "
    + "widget to save selected resonances to file.</p>"
)
STR_SELECT_EXPLAIN: Final[str] = (
    "<p>To select indices, use the <i>Box Select</i> tool from the toolbar "
    + "above the figure.</p>"
)
STR_DESELECT_EXPLAIN: Final[str] = (
    "<p>Deselect single resonances by clicking on them. Deselect everything "
    + "by pressing <i>ESC</i> on your keyboard or using the <i>Reset</i> tool "
    + "above the figure.</p>"
)
