"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

import numba as nb  # type: ignore
import numpy as np

from pyzeta.core.pyzeta_types.general import tMat, tVec


@nb.njit(
    nb.complex128[:, :](nb.complex128[:], nb.complex128[:, :], nb.int16),
    fastmath=True,
    cache=True,
)  # type: ignore
def bellIteration(s: tVec, aArr: tMat, nMax: int) -> tMat:
    "Numba compiled step in the Bell polynomial construction iteration."
    sSize = s.shape[0]
    dArr = np.zeros((sSize, nMax + 1), dtype=np.complex128)

    dArr[:, 0] = 1
    for n in range(1, nMax + 1):
        for k in range(1, n + 1):
            dArr[:, n] += k * dArr[:, n - k] * aArr[:, k - 1]
        dArr[:, n] *= 1.0 / n
    return dArr
