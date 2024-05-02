import logging

from chatgpt_conversation_finder.config import Config
from chatgpt_conversation_finder.helpers import Helpers

class ValidateConversations:
    def __init__(self, config: Config) -> None:
        self.config = config
        json_path = self.config.get_conversations_json_path()
        logging.info(f"Loading conversations from: {json_path}")
        raw_conversations = Helpers.load_json(json_path)
        self.conversation_info = Helpers.get_conversations_info(raw_conversations)

    def validate(self) -> None:
        for conversation_id in self.conversation_info:
            self.validate_conversation_id(conversation_id)

    def validate_conversation_id(self, conversation_id: str) -> None:
        # Validate a conversation by its ID
        conversation = self.conversation_info[conversation_id]
        if not conversation['title']:
            print(f"Conversation {conversation_id} has no title.")