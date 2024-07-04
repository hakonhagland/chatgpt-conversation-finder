import logging

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.helpers import Helpers


class ValidateConversations:
    def __init__(self, config: Config) -> None:
        self.config = config
        json_path = self.config.get_conversations_json_path()
        logging.info(f"Loading conversations from: {json_path}")
        raw_conversations = Helpers.load_json(str(json_path))
        self.conversation_info = Helpers.get_conversations_info(raw_conversations)

    def validate(self) -> bool:
        result = True
        for conversation_id in self.conversation_info:
            if not self.validate_conversation_id(conversation_id):
                result = False
        return result

    def validate_conversation_id(self, conversation_id: str) -> bool:
        # Validate a conversation by its ID
        conversation = self.conversation_info[conversation_id]
        if not conversation["title"]:
            print(f"Conversation {conversation_id} has no title.")
            return False
        return True
