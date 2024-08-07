import colorama
import re

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.constants import GrepColor, RegexFlags
from chatgpt_conversation_finder.helpers import Helpers


class MatchAppender:
    def __init__(self, conversation: str, match_color: GrepColor) -> None:
        self.conversation = conversation
        self.match_color = match_color.to_colorama()
        self.prev_lineno = 0
        self.match_items: list[str] = []
        self.color_mark_start = self.match_color
        self.color_mark_end = colorama.Fore.RESET
        self.extra_len_step = len(self.color_mark_start) + len(self.color_mark_end)
        self.extra_len = 0
        self.prev_line_start: int | None = None

    def append(self, start: int, end: int) -> None:
        lineno = self.conversation.count("\n", 0, start) + 1
        new_item = False
        if lineno == self.prev_lineno:
            line = self.match_items[-1]
            if self.prev_line_start is None:  # pragma: no cover
                raise Exception("This should never happen: prev_line_start is None.")
            line_start = self.prev_line_start
            self.extra_len += self.extra_len_step
        else:
            line_start = max(0, self.conversation.rfind("\n", 0, start))
            line_end = self.conversation.find("\n", end)
            line = self.conversation[line_start:line_end]
            self.prev_lineno = lineno
            self.prev_line_start = line_start
            self.extra_len = 0
            new_item = True
        start2 = start - line_start + self.extra_len
        end2 = end - line_start + self.extra_len
        line = (
            f"{line[:start2]}"
            f"{self.color_mark_start}{line[start2:end2]}"
            f"{self.color_mark_end}"
            f"{line[end2:]}"
        )
        if new_item:
            self.match_items.append(line)
        else:
            self.match_items[-1] = line

    def get_matches(self) -> list[str]:
        return self.match_items


class GrepConversationsHandler:
    def __init__(self, config: Config) -> None:
        self.json_path = config.get_conversations_json_path()
        raw_conversations = Helpers.load_json(str(self.json_path))
        self.conversations = Helpers.flatten_conversations(raw_conversations)
        self.create_time = Helpers.get_conversations_create_time(raw_conversations)
        self.titles = Helpers.get_conversation_titles(raw_conversations)
        self.match_color = config.get_grep_match_color()
        self.match_header_color = config.get_grep_match_header_color()
        self.match_trailer_color = config.get_grep_match_trailer_color()

    def grep(self, regex: str, flags: RegexFlags) -> None:
        num_matches = 0
        num_conv_matches = 0
        for id in self.conversations:
            conversation = self.conversations[id]
            matches = re.finditer(regex, conversation, flags.to_re_flags())
            create_time = Helpers.format_create_time(self.create_time[id])
            header = f"{id}: {self.titles[id]}: {create_time}"
            appender = MatchAppender(conversation, self.match_color)
            found_match = False
            for match in matches:
                num_matches += 1
                found_match = True
                start, end = match.span()
                appender.append(start, end)
            if found_match:
                num_conv_matches += 1
            match_items = appender.get_matches()
            if len(match_items) > 0:
                header_color = self.match_header_color.to_colorama()
                print(f"{header_color}{header}{colorama.Fore.RESET}")
                print("\n  ".join(match_items))
                print()
        if num_matches == 0:
            msg = "No matches found."
        else:
            msg = f"Found {num_matches} matches in {num_conv_matches} conversations."
        print(f"{self.match_trailer_color.to_colorama()}{msg}{colorama.Fore.RESET}")
