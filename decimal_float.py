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
        ret: str = str(self.man)
        z_count: int = 2 << (self.exp_len - 2)

        ret1: str = f'{'0' * (z_count - len(ret))}{ret}{'0' * z_count}'
        ret2: str = f'{ret1[:self.exp]}.{ret1[self.exp:]}'
        ret3: str = ret2.lstrip('0').rstrip('0')

        ret4: str = str(ret3)
        if ret4.startswith('.'):
            ret4 = f'0{ret4}'
        if ret4.endswith('.'):
            ret4 = f'{ret4}0'

        return f'{self.sign}{ret4}'

    def binary(self) -> str:
        return ''.join('1' if bit else '0' for bit in self.bits)


class dec1(dec):
    '''
    - 1-byte signed decimal floating point number
    - 1 significant figure (or 2 if < 16)
    - range {
        [-15'000.0,-0.00001],
        -0.0,
        0.0,
        [0.00001,15'000.0]
    }
    '''

    def __init__(self, bits: list[bool] = []):
        super().__init__(bits, 3, 4)


class dec2(dec):
    '''
    - 2-byte signed decimal floating point number
    - 3 significant figures (or 4 if < 1'024)
    - range {
        [-102.3e16,-1.0e-16,
        -0.0,
        0.0,
        [1.0e-16,102.3e16]
    }
    '''

    def __init__(self, bits: list[bool] = []):
        super().__init__(bits, 5, 10)


class dec3(dec):
    '''
    - 3-byte signed decimal floating point number
    - 5 significant figures (or 6 if < 131'072)
    - range {
        [-13'107.2e32,-1.0e-32,
        -0.0,
        0.0,
        [1.0e-32,13'107.2e32]
    }
    '''

    def __init__(self, bits: list[bool] = []):
        super().__init__(bits, 6, 17)


def main() -> None:
    # while True:
    #     print('give me 8 bits')

    #     s = input('> ')
    #     if len(s) != 8:
    #         print('bad input')
    #         continue

    #     f: dec1 = dec1([int(i) for i in s])
    #     print(f)

    # while True:
    #     print('give me 16 bits')

    #     s = input('> ')
    #     if len(s) != 16:
    #         print('bad input')
    #         continue

    #     f: dec2 = dec2([int(i) for i in s])
    #     print(f)

    # while True:
    #     print('give me 24 bits')

    #     s = input('> ')
    #     if len(s) != 24:
    #         print('bad input')
    #         continue

    #     f: dec3 = dec3([int(i) for i in s])
    #     print(f)

    lines: list[str] = []

    # for i in range(256):
    #     b: str  = bin(i).replace('0b', '').rjust(8, '0')
    #     d: dec1 = dec1([int(c) for c in b])
    #     e: str = f'{str(i).zfill(3)} {b[0]} {b[1:d.exp_len + 1]} {b[d.exp_len + 1:]}'
    #     # print(f'{e} {d}')
    #     lines.append(f'{e} {d}\n')

    # with open('dec1.txt', 'w', newline='\n') as f:
    #     f.writelines(lines)

    # for i in range(65536):
    #     b: str  = bin(i).replace('0b', '').rjust(16, '0')
    #     d: dec2 = dec2([int(c) for c in b])
    #     e: str = f'{str(i).zfill(5)} {b[0]} {b[1:d.exp_len + 1]} {b[d.exp_len + 1:]}'
    #     # print(f'{e} {d}')
    #     lines.append(f'{e} {d}\n')

    # with open('dec2.txt', 'w', newline='\n') as f:
    #     f.writelines(lines)

    # for i in range(16777216):
    #     if not i % 1000000:
    #         print(i)
    #         # if i:
    #         #     break

    #     b: str  = bin(i).replace('0b', '').rjust(24, '0')
    #     d: dec3 = dec3([int(c) for c in b])
    #     e: str = f'{str(i).zfill(8)} {b[0]} {b[1:d.exp_len + 1]} {b[d.exp_len + 1:]}'
    #     # print(f'{e} {d}')
    #     line: str = f'{e} {d}\n'
    #     lines.append(line)

    # with open('dec3.txt', 'w', newline='\n') as f:
    #     for line in lines:
    #         f.write(line)


if __name__ == '__main__':
    main()
