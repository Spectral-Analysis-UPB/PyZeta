"""
Module containing numba compiled filtering functions for usage in symbolic
dynamics implementations.

Authors:\n
- Philipp Schuette\n
"""

from typing import Tuple, no_type_check

import numba as nb  # type: ignore
import numpy as np
from numpy.typing import NDArray

from pyzeta.core.pyzeta_types.general import tBoolMat, tMat, tWordVec
from pyzeta.core.pyzeta_types.special import tLetter, tMask, tWord

##############################################
# Numba Versions of Symbolic Dynamic Methods #
##############################################


@nb.jit(
    nb.uint32[:, :](nb.uint32[:, :], nb.bool_[:, :]),
    nopython=True,
    fastmath=True,
    cache=True,
)
@no_type_check
def matMul(left: tMat, right: tBoolMat) -> tMat:
    """
    Multiply two matrices `left` and `right` fast. Performs no checks.

    :param left: First matrix to multiply
    :param right: Second matrix to multiply
    :return: Matrix product
    """
    dim: np.uint8 = left.shape[0]
    result: NDArray[np.uint32] = np.zeros((dim, dim), dtype=np.uint32)
    for i in range(dim):
        for j in range(dim):
            for k in range(dim):
                result[i][j] += left[i][k] * right[k][j]
    return result


@nb.jit(
    nb.uint8[:, :](nb.uint8, nb.bool_[:, :]),
    nopython=True,
    fastmath=True,
    cache=True,
)
@no_type_check
def getWordsFast(n: int, adj: tBoolMat) -> tMat:
    """
    Generate all words of length `n` for alphabet with adjacency matrix `adj`.

    :param n: Length of words to be generated
    :param adj: Adjacency matrix over some alphabet
    :return: Array containing all words of length `n`
    """
    alphabetSize: np.uint8 = adj.shape[0]
    adjPower: NDArray[np.uint32] = np.eye(alphabetSize, dtype=np.uint32)
    for i in range(1, n):
        adjPower = matMul(adjPower, adj)
    wordNum: nb.uint8 = np.sum(adjPower)
    adjNonNull = np.nonzero(adj)
    # array for storing generated words; initialise with all entries set to -1
    result: tWordVec = np.full((wordNum, n), -1, dtype=tLetter)
    tmp: tWordVec

    # initialize words of length 1:
    for i in range(alphabetSize):
        result[i][0] = i
    adjPower = np.eye(alphabetSize, dtype=np.uint32)

    for length in range(1, n):
        wordNum = np.sum(adjPower)
        adjPower = matMul(adjPower, adj)
        tmp = np.copy(result)
        pos: np.uint8 = 0
        for i in range(wordNum):
            word: tWord = tmp[i]
            adjRow: tWord = adjNonNull[1][adjNonNull[0] == word[length - 1]]
            for letter in adjRow:
                for k in range(length):
                    result[pos][k] = word[k]
                result[pos][k + 1] = letter
                pos += 1

    return result


@nb.jit(
    nb.uint8[:, :](nb.uint8, nb.bool_[:, :], nb.uint8[:, :]),
    nopython=True,
    fastmath=True,
    cache=True,
)
@no_type_check
def appendWordsFast(n: int, adj: tBoolMat, words: tWordVec) -> tWordVec:
    """
    Append to given words according to a given adjacency matrix to obtain words
    of a given length

    :param n: Length of words to be generated
    :param adj: Adjacency matrix determining valid words
    :param words: Array containing (all) words of some length <`n`
    :return: Array containing all words of length `n`
    """
    alphabetSize: np.uint8 = adj.shape[0]
    givenWordNum: np.uint8 = words.shape[0]
    givenWordLen: np.uint8 = words.shape[1]
    adjPower: NDArray[np.uint32] = np.eye(alphabetSize, dtype=np.uint32)
    for i in range(1, n):
        adjPower = matMul(adjPower, adj)
    wordNum: nb.uint8 = np.sum(adjPower)
    adjNonNull = np.nonzero(adj)

    # array for storing generated words; initialise with all entries set to -1
    result: tWordVec = np.full((wordNum, n), -1, dtype=tLetter)
    tmp: tWordVec

    result[:givenWordNum, :givenWordLen] = words
    adjPower = np.eye(alphabetSize, dtype=np.uint32)
    for length in range(1, givenWordLen):
        adjPower = matMul(adjPower, adj)

    for length in range(givenWordLen, n):
        wordNum = np.sum(adjPower)
        adjPower = matMul(adjPower, adj)
        tmp = np.copy(result)
        pos: nb.uint8 = 0
        for i in range(wordNum):
            word: tWord = tmp[i]
            adjRow: tWord = adjNonNull[1][adjNonNull[0] == word[length - 1]]
            for letter in adjRow:
                for k in range(length):
                    result[pos][k] = word[k]
                result[pos][k + 1] = letter
                pos += 1

    return result


@nb.guvectorize(
    [(nb.uint8[:], nb.bool_[:])], "(n)->()", nopython=True, cache=True
)
@no_type_check
def isPrimeFast(word: tWord, res: bool):
    """
    Check if given `word` is prime. Accepts arrays of symbolic words.

    :param word: Word (or array of words) of letters from a given alphabet
    :return: `True` iff word is prime
    """
    n: np.uint8 = len(word)
    kPerm: bool = True
    res[0] = True

    for k in range(1, n // 2 + 1):
        if n % k == 0:
            for m in range(1, n // k):
                if np.any(word[:k] != word[m * k : (m + 1) * k]):
                    kPerm = False
                    break
            if kPerm:
                res[0] = False
                break
            kPerm = True


@nb.jit(
    nb.bool_(nb.uint8[:], nb.uint8[:, :]),
    fastmath=True,
    nopython=True,
    cache=True,
)
@no_type_check
def containsPermFast(word: tWord, wordsToCheck: tWordVec) -> bool:
    """
    Return `True` if `wordList` contains a permutation of `word`.

    :param word: Word over a given alphabet
    :param wordsToCheck: array of words over the same alphabet
    :return: `True` iff `wordsToCheck` contain permutations of `word`
    """
    n: np.uint8 = len(word)
    for _ in range(n):
        word = np.roll(word, 1)
        for checkWord in wordsToCheck:
            if np.all(word == checkWord):
                return True
    return False


@nb.jit(nb.bool_[:](nb.uint8[:, :]), fastmath=True, nopython=True, cache=True)
@no_type_check
def filterPermsFast(words: tWordVec) -> tMask:
    """
    Filter out all permutations from a list of `words` after the first
    occurrence.

    :param words: array of words over a given alphabet
    :return: Mask that implements this filter on the list
    """
    size: np.int8 = len(words)
    mask: tMask = np.zeros(size, dtype=np.bool_)
    mask[0] = True
    for i in range(1, size):
        mask[i] = not containsPermFast(words[i], words[:i])
    return mask


@nb.guvectorize(
    [(nb.uint8[:], nb.bool_[:, :], nb.bool_[:])],
    "(n),(m,m)->()",
    nopython=True,
    cache=True,
)
@no_type_check
def isCyclRedFast(word: tWord, adj: tBoolMat, res: Tuple[bool]) -> None:
    """
    Return `True` if last to first letter of `word` defines a valid transtion
    (i.e. word is cyclically reduced). Accepts arrays of symbolic words.

    :param word: Word (or array of words) over a given alphabet
    :return: `True` if word is cyclically reduced, `False` otherwise
    """
    n: np.uint8 = len(word)
    if adj[word[n - 1]][word[0]] == 0:
        res[0] = False
    else:
        res[0] = True


@nb.guvectorize(
    [(nb.uint8[:], nb.bool_[:])], "(n)->()", nopython=True, cache=True
)
@no_type_check
def isPeriodicFast(word: tWord, res: Tuple[bool]) -> None:
    """
    Check if given `word` is periodic. Accepts arrays of symbolic words.

    :param word: Word (or array of words) over a given alphabet
    :return: `True` if word is periodic, `False` otherwise
    """
    n: np.uint8 = len(word)
    if word[0] == word[n - 1]:
        res[0] = True
    else:
        res[0] = False
