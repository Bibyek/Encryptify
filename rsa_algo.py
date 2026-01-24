import random

# --------------------------------------------------
# RSA MATHEMATICAL CORE
# --------------------------------------------------

# 1. Helper: Check if a number is prime
def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# 2. Helper: Find the Greatest Common Divisor (GCD)
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# 3. Helper: Find Modular Inverse (d * e) % phi == 1
def mod_inverse(e, phi):
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        else:
            g, y, x = extended_gcd(b % a, a)
            return g, x - (b // a) * y, y

    g, x, y = extended_gcd(e, phi)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    else:
        return x % phi

# 4. KEY GENERATION (The Math Magic)
def generate_keypair():
    # In real life, these primes are HUGE. For this demo, we use small ones for speed.
    primes = [i for i in range(100, 300) if is_prime(i)]
    p = random.choice(primes)
    q = random.choice(primes)
    while p == q:
        q = random.choice(primes)

    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose public exponent e
    e = random.randrange(1, phi)
    g = gcd(e, phi)
    while g != 1:
        e = random.randrange(1, phi)
        g = gcd(e, phi)

    # Calculate private exponent d
    d = mod_inverse(e, phi)

    # Return ((Public Key), (Private Key))
    return ((e, n), (d, n))

# 5. ENCRYPTION: C = (M ^ e) % n
def encrypt(pk, plaintext):
    key, n = pk
    # Convert each letter to a number -> do the math -> list of numbers
    cipher = [(ord(char) ** key) % n for char in plaintext]
    return cipher

# 6. DECRYPTION: M = (C ^ d) % n
def decrypt(pk, ciphertext_list):
    key, n = pk
    # Do the math -> convert number back to letter -> join string
    plain = [chr((char ** key) % n) for char in ciphertext_list]
    return ''.join(plain)