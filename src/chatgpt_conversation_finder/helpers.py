import datetime
import io
import json
import logging
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

# import nltk
# import nltk.corpus
from chatgpt_conversation_finder.config import Config


class Helpers:
    @staticmethod
    def extract_conversations_json_file(datadir: Path, filename: str) -> None:
        # Extract the conversations.json file from the .zip file
        # First copy the .zip file to the user's data directory
        new_zip_filename = datadir / Config.chats_zip_fn
        shutil.copy(filename, new_zip_filename)
        # Then extract the .zip file to a temporary directory
        tempdir = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(new_zip_filename, "r") as zip_ref:
            zip_ref.extractall(tempdir.name)
        # Then copy the conversations.json file to the user's data directory
        extracted_file = Path(tempdir.name) / Config.conversation_json_fn
        shutil.copy(extracted_file, datadir / Config.conversation_json_fn)
        tempdir.cleanup()
        logging.info(f"Extracted {Config.conversation_json_fn} to {datadir}")

    @staticmethod
    def flatten_conversations(conversations: list[dict[str, Any]]) -> dict[str, str]:
        flattend_conversations = {}
        for conversation in conversations:
            buffer = io.StringIO()
            id = conversation["id"]
            for message_id, message_details in conversation.get("mapping", {}).items():
                message = message_details.get("message")
                if message:
                    message_content = message.get("content", {}).get("parts", [])
                    for part in message_content:
                        if isinstance(part, str):
                            buffer.write(part)
                            buffer.write("\n")
            content = buffer.getvalue()
            if len(content) > 0:
                flattend_conversations[id] = content
        return flattend_conversations

    @staticmethod
    def format_create_time(create_time: int) -> str:
        # Convert UNIX timestamp to datetime object
        create_time_dt = datetime.datetime.fromtimestamp(create_time)
        # Format datetime object to exclude minutes and seconds, include hour
        formatted_create_time = create_time_dt.strftime("%B %d, %Y %H:00")
        return formatted_create_time

    @staticmethod
    def get_conversations_info(
        conversations: list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        return {
            conversation["id"]: {
                "id": conversation["id"],
                "title": conversation.get("title", ""),
                "create_time": conversation.get("create_time", 0),
            }
            for conversation in conversations
        }

    @staticmethod
    def get_conversations_create_time(
        conversations: list[dict[str, Any]],
    ) -> dict[str, int]:
        return {
            conversation["id"]: conversation.get("create_time", 0)
            for conversation in conversations
        }

    @staticmethod
    def get_conversation_titles(conversations: list[dict[str, Any]]) -> dict[str, str]:
        return {
            conversation["id"]: conversation.get("title", "")
            for conversation in conversations
        }

    @staticmethod
    def load_json(json_path: str) -> list[dict[str, Any]]:
        with open(json_path, "r") as f:
            return json.load(f)  # type: ignore


#    @staticmethod
#    def lowercase_conversations(conversations: dict[str, str]) -> dict[str, str]:
#        return {id: content.lower() for id, content in conversations.items()}
