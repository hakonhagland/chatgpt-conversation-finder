import colorama
import re
import enum


class GrepColor(enum.Enum):
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    BLUE = colorama.Fore.BLUE
    MAGENTA = colorama.Fore.MAGENTA
    CYAN = colorama.Fore.CYAN
    WHITE = colorama.Fore.WHITE

    @classmethod
    def from_str(cls, color: str) -> "GrepColor":
        color_mapping = {
            "RED": cls.RED,
            "GREEN": cls.GREEN,
            "YELLOW": cls.YELLOW,
            "BLUE": cls.BLUE,
            "MAGENTA": cls.MAGENTA,
            "CYAN": cls.CYAN,
            "WHITE": cls.WHITE,
        }
        return color_mapping[color.upper()]

    def to_colorama(self) -> str:
        return self.value


class RegexFlags(enum.Flag):
    IGNORECASE = re.IGNORECASE
    MULTILINE = re.MULTILINE
    DOTALL = re.DOTALL
    NOFLAG = re.NOFLAG

    @classmethod
    def from_str(cls, flags: str) -> "RegexFlags":
        flag_mapping = {
            "IGNORECASE": cls.IGNORECASE,
            "I": cls.IGNORECASE,
            "MULTILINE": cls.MULTILINE,
            "M": cls.MULTILINE,
            "DOTALL": cls.DOTALL,
            "S": cls.DOTALL,
        }
        if flags == "":
            return cls(cls.NOFLAG)
        flag_strs = flags.split("|")
        flag_values = [flag_mapping[flag.upper()] for flag in flag_strs]
        return cls(*flag_values)

    def to_re_flags(self) -> int:
        re_flags = 0
        for flag in RegexFlags:
            if self & flag:
                re_flags |= flag.value
        return re_flags
