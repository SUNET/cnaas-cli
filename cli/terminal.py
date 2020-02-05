import fcntl
import termios
import struct

from typing import Optional


def print_hline(character: Optional[str] = '-',
                newline: Optional[bool] = False,
                width: Optional[int] = 0) -> None:
    """
    Print horizontal line
    """
    if newline:
        print('')
    if width == 0:
        width, height = terminal_size()
    print(character * width)


def terminal_size() -> tuple:
    """
    Get terminal width and height
    """

    packed_struct = struct.pack('HHHH', 0, 0, 0, 0)
    h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ,
                                                     packed_struct))
    return w, h
