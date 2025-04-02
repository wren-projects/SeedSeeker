import random

def rot(x, k, digits=64):
    return ((x << k) | (x >> (digits - k)))%2**digits

def xoshiro(s0, s1, s2, s3):
    """
    implementation of xoshiro256**
    """
    print(s1)
    print(s0^s2)
    print(s0^s3)
    i=0
    while True:
        i+=1
        if i==1: 
            print(s0,s1,s2,s3)
        r = (rot((s1*5)%2**64,7) * 9)%2**64
        t = (s1<<17)%2**64
        s2 ^= s0
        s3 ^= s1
        s1 ^= s2
        s0 ^= s3
        s2 ^= t
        s3 = rot(s3, 45)
        yield r

def helper(x):
    return (rot((x*inv9)%2**64, 64-7)*inv5)%2**64

inv9 = pow(9, -1, 2**64)
inv5 = pow(5, -1, 2**64)
def reverseXoshiro(gen):
    a = next(gen)
    b = next(gen)
    c = next(gen)
    d = next(gen)   
    
    # sX is the inital state
    s1 = helper(a)
    s0s2 = s1^helper(b)
    s0s3 = ((s1<<17)^helper(c))%2**64

    # tX us the state after one iteration
    t0 = s1^s0s3
    t1 = s1^s0s2
    t2 = s0s2^(s1<<17)%2**64
    t3 = t0 ^ helper(d) ^ (t1<<17)%2**64

    s3 = rot(t3, 64-45) ^ s1
    s0 = t0^s1^s3
    s2 = t1^s0^s1
    return s0,s1,s2,s3



x = lambda : random.randint(0, 2**64-1)
reverseXoshiro(xoshiro(x(), x(), x(), x()))

