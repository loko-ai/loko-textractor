import codecs
import logging
import os
import re
from email.header import decode_header
from email.message import Message
from tempfile import NamedTemporaryFile
from typing import List, Tuple, Dict

import html2text


from ds4biz_format_parsers.business.text_extractors import RESTDS4BizTextract
from ds4biz_format_parsers.model.emails import TextEmail


class AsyncEmail2TextEmail:

    def __init__(self, extractor: RESTDS4BizTextract, part_types: List[str] = ["text/plain", "text/html"],
                 attachment_flag: bool = True):
        self.extractor = extractor
        self.attachment_flag = attachment_flag
        self.part_types = part_types

    async def __call__(self, email: Message) -> TextEmail:
        te = TextEmail("")
        te.sender = self.get_sender(email)
        te.recipients, te.cc, te.bcc = self.get_recipients(email)
        te.subject = self.get_subject(email)
        te.body_parts, te.attachments = await self.get_parts(email)

        return te

    def get_sender(self, email: Message) -> str:
        try:
            sender = email.get("from")
            sender_address_temp = re.search("<(.*?)>", sender)
            sender_address = str(sender_address_temp.group(1)).strip() if sender_address_temp else sender
            if sender_address:
                return sender_address
            else:
                return ""
        except Exception as inst:
            logging.debug(inst)
            return ""

    def get_recipients(self, email: Message) -> List[str]:
        addresses = {"to": [], "cc": [], "bcc": []}
        for k in addresses.keys():  # :-)
            rfiled = email.get(k)
            if rfiled:
                address_temp = re.search("<(.*?)>", rfiled)
                address = str(address_temp.group(1)).strip() if address_temp else rfiled
                if address not in addresses:
                    addresses[k].append(address)
        return addresses["to"], addresses["cc"], addresses["bcc"]

    def get_subject(self, email: Message) -> str:
        subject = email.get("subject", "")
        subject = self.text_part_decode(subject)
        return subject

    async def get_parts(self, email: Message) -> Tuple[List[str], Dict[str, str]]:
        body_parts = []
        attachments = {}
        duplicated_names = {}
        for part in email.walk():
            ct = part.get_content_type().lower()
            cd = part.get_content_disposition()
            fn = part.get_filename()
            fn = self.text_part_decode(fn)
            if cd != 'attachment' and ct in self.part_types:
                body_parts.append(dict(content_type=ct,content=self.get_body(part)))
            else:
                if self.attachment_flag and fn:
                    if fn not in duplicated_names:
                        duplicated_names[fn] = 1
                    else:
                        duplicated_names[fn] += 1
                        fn_s = fn.split('.')
                        ext = fn_s[-1]
                        fn = '.'.join(fn_s[:-1])+'('+str(duplicated_names[fn])+').'+ext
                    if cd == "attachment" or ct == "application/octet-stream" or ct.startswith("image/"):
                        ris = await self.get_attachments(part, fn)
                        if ris:
                            attachments.update(ris)
        return body_parts, attachments

    def text_part_decode(self, text_part: str) -> str:
        try:
            text_part = "".join([codecs.decode(sub, enc) for sub, enc in decode_header(text_part)])
        except:
            pass
        return text_part

    def get_body(self, part: Message) -> str:
        h = html2text.HTML2Text()
        h.ignore_links = True
        body_part = ""
        payload = part.get_payload(decode=True)
        if payload:
            if part.get_content_charset():
                # body_part = h.handle(payload.decode(part.get_content_charset(), 'replace'))  # Questo appiattisce molto il testo: da discutere
                body_part = payload.decode(part.get_content_charset(),
                                           'replace')  # Questo non lo appiattisce invece: valutare
            else:
                body_part = payload.decode("utf8", 'replace').strip()
        return body_part

    async def get_attachments(self, part: Message, fn: str) -> Dict[str, str]:
        attachments = {}
        if self.extractor is None:
            return attachments

        ext = os.path.splitext(fn)[-1]
        ct = part.get_content_type().lower()
        if ct == 'image/jpeg':
            ext = '.jpg'

        with NamedTemporaryFile(suffix=ext) as tt:
            try:
                temp = part.get_payload(decode=True)
                if temp:
                    tt.write(temp)
                    attachments[fn] = await self.extractor.extract(tt.name)
            except Exception as inst:
                logging.debug(inst)
                attachments[fn] = ""
                return attachments
        return attachments