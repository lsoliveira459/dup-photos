import numba as nb

@nb.njit
def hamming_distance(a: int, b: int) -> int:
    '''The function calculates the Hamming distance between two integers using bitwise
    operations.

    Sources:
    - Hamming distance: [Fast way of counting non zero bits in positive integer](https://stackoverflow.com/a/64848298)

    Parameters
    ----------
    a : int
        The first integer input for calculating the Hamming distance between two
    numbers.
    b : int
        The parameter "b" in the function "hamming_distance" is an integer representing
    one of the two numbers for which we want to calculate the Hamming distance.

    Returns
    -------
        The function `hamming_distance` takes two integers `a` and `b` as input and
    returns the Hamming distance between them. The Hamming distance is the number of
    positions at which the corresponding bits are different in the binary
    representation of `a` and `b`.

    '''
    return (~(a^(~b))).bit_count()