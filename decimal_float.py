# c 2025-01-03
# m 2025-01-03

import os


class dec:
    '''
    decimal floating point number
    '''

    def __init__(self, bits: list[bool] = [], exponent_length: int = 0, mantissa_length: int = 0):
        self.bits: list[bool] = bits
        self.exp_len: int = exponent_length
        self.man_len: int = mantissa_length

        self.sign: str = '-' if self.bits[0] else ''

        self.exp: int = 0
        for i in range(self.exp_len):
            self.exp += 2**(self.exp_len - 1 - i) if self.bits[i + 1] else 0

        self.man: int = 0
        for i in range(self.man_len):
            self.man += 2**(self.man_len - 1 - i) if self.bits[i + 1 + self.exp_len] else 0

    def __repr__(self) -> str:
        return f'{type(self)} {self.binary()}'

    def __str__(self) -> str:
        ret: str = f'0{self.man}0'
        ret = f'{ret[:self.exp]}.{ret[self.exp:]}'
        ret = ret.lstrip('0').rstrip('0')
        if ret.startswith('.'):
            ret = f'0{ret}'
        if ret.endswith('.'):
            ret = f'{ret}0'

        return f'{self.sign}{ret}'

    def binary(self) -> str:
        return ''.join('1' if bit else '0' for bit in self.bits)


class dec1(dec):
    '''
    1-byte decimal floating point number
    2 significant figures
    {
        [-31.0,-0.01],
        -0.0,
        0.0,
        [0.01,31.0]
    }
    '''

    def __init__(self, bits: list[bool] = []):
        super().__init__(bits, 2, 5)


def main() -> None:
    while True:
        print('give me 8 bits')

        s = input('> ')
        if len(s) != 8:
            print('bad input')
            continue

        f: dec1 = dec1([int(i) for i in s])
        print(f)


if __name__ == '__main__':
    main()
