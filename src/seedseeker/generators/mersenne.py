from itertools import islice

from collections.abc import Iterator

IntegerRNG = Iterator[int]
RealRNG = Iterator[float]

N = 624
M = 397
W = 32
R = 31
UMASK = 0xFFFFFFFF << R
LMASK = 0xFFFFFFFF >> (W - R)
A = 0x9908B0DF
U = 11
S = 7
T = 15
L = 18
B = 0x9D2C5680
C = 0xEFC60000 
F = 1812433253 # Can be changed


def mersenne_twister(seed: int) -> IntegerRNG:
    """Create a Mersenne Twister 19937 PRNG."""
    # TODO: Allow for parameters to be specified as arguments
    state_array = [0] * N
    state_index = 0

    assert 0 <= seed < 2**32, "Seed must be between 0 and 2^32"

    state_array[0] = seed
    for i in range(1, N):
        seed = F * (seed ^ (seed >> (W - 2))) % 2**32 + i
        state_array[i] = seed

    while True:
        k = state_index
        j = k - (N - 1)
        if j < 0:
            j += N

        x = (state_array[k] & UMASK) | (state_array[j] & LMASK)
        x_a = x >> 1
        if x & 1:  # modulo 2 == 1
            x_a ^= A

        j = k - (N - M)
        if j < 0:
            j += N

        x = state_array[j] ^ x_a
        state_array[k] = x
        k += 1
        if k >= N:
            k = 0
        state_index = k

        y = x ^ (x >> U)
        y ^= (y << S) & B
        y ^= (y << T) & C
        y ^= y >> L
        
        yield y


def mersenne_twister_real(seed: int) -> RealRNG:
    """Create a Mersenne Twister 19937 PRNG with real values."""
    yield from (x_n / 2**32 for x_n in mersenne_twister(seed))


"""
Class:
    RandCrack

Function:     
    One of the most known predictors for MT19937.
    The generator find internal state and then he can predict the numbers.
    The cracker needs 624 numbers to find internal state.

Return:
    # TODO IntegerRNG / class Mersenne_twister
    # Now it can return predicted numbers

"""

"""
Dependencies: pip install randcrack
"""
from randcrack import RandCrack


"""
Function for predicted numbers.
TODO instead of [list(islice(mersenne_twister(mersenne_seed), 1000)] there will be numbers from input

"""
def predict(mersenne_seed):
    unknown = list(islice(mersenne_twister(mersenne_seed), 1000))
    #print("Trying to predict MT19937 generator...")

    cracker = RandCrack()

    if (len(unknown) < 624):
        assert("File have less than 624 numbers!")

    # Submit the first 624 numbers from your Mersenne Twister
    for i in range(624):
        cracker.submit(unknown[i])

    # Future values
    future_predictions_match = 0
    mt_future = islice(mersenne_twister(mersenne_seed), 624, 1624) # Dalších 1000 čísel
    for i, predicted in zip(mt_future, (cracker.predict_getrandbits(32) for _ in range(1000))):
        if i == predicted:
            future_predictions_match += 1
    percentage_future = (future_predictions_match / 1000) * 100

    return percentage_future

if __name__ == "__main__":
    twister = 19650218
    print(predict(twister))

