# -*- coding: utf-8 -*-

import platform
import sys

def get_columns():
    def __get_columns_windows():
        import ctypes
        import ctypes.wintypes

        class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
            _fields_ = [
                ('dwSize', ctypes.wintypes._COORD),
                ('dwCursorPosition', ctypes.wintypes._COORD),
                ('wAttributes', ctypes.c_ushort),
                ('srWindow', ctypes.wintypes._SMALL_RECT),
                ('dwMaximumWindowSize', ctypes.wintypes._COORD)
            ]

        ctypes.windll.kernel32.GetStdHandle.restype = ctypes.wintypes.HANDLE
        hstd = ctypes.windll.kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE = -11
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(
            ctypes.wintypes.HANDLE(hstd), 
            ctypes.byref(csbi)
        )
        return min(csbi.srWindow.Right - csbi.srWindow.Left + 1, csbi.dwSize.X - 1)
    def __get_columns_unix():
        import os
        try:
            import fcntl
            import termios
            import struct
            ioctl_width = lambda fd: struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))[1]
            width = ioctl_width(0) or ioctl_width(1) or ioctl_width(2) or ioctl_width(3)
            if not width:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                width = ioctl_width(fd)
                print fd
                os.close(fd)
            if width:
                return width
        except:
            print 'xxx'
            width = os.environ.get('COLUMNS')
            if width:
                return width
            try:
                return int(os.popen('stty size').read().split()[1])
            except:
                return 80
    
    os = platform.system()
    if os == 'Windows':
        return __get_columns_windows()
    else:
        try:
            return __get_columns_unix()
        except:
            return 80

def draw(done, all, text, file=sys.stdout):
    cols = get_columns()
    cols_pgbar = cols - len(text) - 1
    file.write('\r')
    if cols_pgbar >= 4:
        cols_pg = cols_pgbar - 6
        cols_done = cols_pg * done / all
        percent = '%2d%%' % (done * 100 / all)
        pg_done = ('=' * cols_done)
        if done != all:
            pg_remain = '>%s' % (' ' * (cols_pg - cols_done - 1))
            percent += ' '
        else:
            pg_remain = ''
        file.write('%s[%s%s] %s' % (percent, pg_done, pg_remain, text))
    elif cols_pgbar >= 0:
        file.write('%s %s' % (' ' * cols_pgbar, text))
    file.flush()