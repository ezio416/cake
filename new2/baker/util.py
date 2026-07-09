from datetime import datetime as dt, timezone as tz


VERSION = '0.3.0'


class LanguageError(RuntimeError):
    pass


def debug_header(middle: str) -> str:
    return f'baker v{VERSION}, generated at {dt.now(tz.utc).strftime(f'%Y-%m-%d %H:%M:%S UTC')}\n{middle}\n{'-' * 50}\n'
