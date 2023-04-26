from email.message import Message

from typing import Dict

from ds4biz_format_parsers.business.converters import Email2TextEmail



class Email2TextEmail2(Email2TextEmail):

    def get_attachments(self, part: Message, fn: str) -> Dict[str, str]:

        attachments = {}
        attachments[fn] = part.get_payload(decode=True)

        return attachments
