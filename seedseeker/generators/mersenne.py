from itertools import islice

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
F = 1812433253


def mersenne_twister(seed):
    state_array = [0] * N
    state_index = 0

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
        xA = x >> 1
        if x & 1:  # modulo 2 == 1
            xA ^= A

        j = k - (N - M)
        if j < 0:
            j += N

        x = state_array[j] ^ xA
        state_array[k] = x
        k += 1
        if k >= N:
            k = 0
        state_index = k

        y = x ^ (x >> U)
        y = y ^ ((y << S) & B)
        y = y ^ ((y << T) & C)
        z = y ^ (y >> L)

        yield z


def mersenne_twister_real(seed):
    yield from (x_n / 2**32 for x_n in mersenne_twister(seed))


if __name__ == "__main__":
    print(*islice(mersenne_twister(19650218), 100), sep=", ")
    print(*islice(mersenne_twister_real(19650218), 100), sep=", ")
