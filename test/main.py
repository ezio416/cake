import os
import sys

try:
    from ..baker import Baker
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from baker import Baker


def main() -> None:
    baker = Baker(os.path.dirname(__file__))
    baker.bake(True)

    pass


if __name__ == '__main__':
    main()
