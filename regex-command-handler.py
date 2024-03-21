import re
from typing import Optional
from telegram import MessageEntity, Update
from telegram.ext import BaseHandler, filters as filters_module


class RegexCommandHandler(BaseHandler):
    __slots__ = ("pattern", "filters")

    def __init__( self, pattern: re.Pattern | str, callback, filters: Optional[filters_module.BaseFilter] = None, block: bool = True):
        super().__init__(callback, block=block)
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.pattern = pattern
        self.filters: filters_module.BaseFilter = filters_module.UpdateType.MESSAGES if filters is None else filters


    def check_update(self, update):
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            if message.entities and message.entities[0].type == MessageEntity.BOT_COMMAND and message.entities[0].offset == 0 and message.text and message.get_bot():
                command = message.text[1 : message.entities[0].length]
                args = message.text.split()[1:]
                command_parts = command.split("@")
                command_parts.append(message.get_bot().username)

                match = self.pattern.match(command_parts[0])
                if not match and command_parts[1].lower() == message.get_bot().username.lower():
                    return None

                filter_result = self.filters.check_update(update)
                if filter_result:
                    return args, filter_result, match.groupdict()
                return False

        return None


    def collect_additional_context(self, context, update: Update, application, check_result) -> None:
        if isinstance(check_result, tuple):
            context.args = check_result[0]

            if isinstance(check_result[1], dict):
                context.update(check_result[1])
            
            if isinstance(check_result[2], dict):
                context.update(check_result[2])
