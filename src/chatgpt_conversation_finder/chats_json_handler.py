from typing import Any

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.helpers import Helpers


class ChatsJsonHandler:
    def __init__(self, config: Config) -> None:
        self.json_path = config.get_conversations_json_path()
        self.conversations = Helpers.load_json(str(self.json_path))

    def get_conversations(self) -> list[dict[str, Any]]:
        return self.conversations

    def search_conversations(self, search_term: str) -> list[dict[str, Any]]:
        results = []
        for conversation in self.conversations:
            title = conversation.get("title", "") or ""  # Ensure title is not None
            create_time = conversation.get("create_time", 0)  # Get creation time

            if search_term.lower() in title.lower():
                results.append(
                    {
                        "title": title,
                        "id": conversation["id"],
                        "create_time": create_time,
                    }
                )
            else:
                for message_id, message_details in conversation.get(
                    "mapping", {}
                ).items():
                    message = message_details.get("message")
                    if message:  # Check if message is not None
                        message_content = message.get("content", {}).get("parts", [])
                        if any(
                            search_term.lower() in part.lower()
                            for part in message_content
                            if isinstance(part, str)
                        ):
                            results.append(
                                {
                                    "title": title,
                                    "id": conversation["id"],
                                    "create_time": create_time,
                                }
                            )
                            break  # Break after the first match within this conversation
        return results
