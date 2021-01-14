import fcntl
import struct
import termios
from typing import Optional


def print_hline(character: Optional[str] = '-',
                newline: Optional[bool] = False,
                width: Optional[int] = 0) -> None:
    """
    Print horizontal line
    """

    print(get_hline(character, newline, width))


def get_hline(character: Optional[str] = '-',
              newline: Optional[bool] = True,
              width: Optional[int] = 0) -> None:
    """
    Return the same number of characters as the terminal width
    """

    if width == 0:
        width, height = terminal_size()

    line = character * width

    if newline:
        line += '\n'

    return line


def terminal_size() -> tuple:
    """
    Get terminal width and height
    """

    packed_struct = struct.pack('HHHH', 0, 0, 0, 0)
    h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ,
                                                     packed_struct))
    return w, h


def lrstrip(line: str) -> str:
    """
    Do lstrip and rstrip on a string
    """

    return line.lstrip().rstrip()
