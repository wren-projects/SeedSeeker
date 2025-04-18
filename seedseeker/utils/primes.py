from collections.abc import Iterator


def primes_up_to(n: int) -> Iterator[int]:
    """Generate primes up to n."""
    # Seive of Eratosthenes
    primes = [True] * (n + 1)
    primes[0] = False
    primes[1] = False

    for i in range(2, n + 1):
        if primes[i]:
            yield i
            for j in range(i * 2, n + 1, i):
                primes[j] = False


PRIMES = list(primes_up_to(2**16))


def divisors(n: int) -> Iterator[int]:
    """
    Generate divisors of n.

    Includes the number itself, but not 1.
    """
    yield n
    for prime in PRIMES:
        res, rem = divmod(n, prime)
        if rem == 0:
            yield res
