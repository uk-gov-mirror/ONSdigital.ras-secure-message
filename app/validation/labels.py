from enum import Enum


class Labels(Enum):
    INBOX = "INBOX"
    UNREAD = "UNREAD"
    SENT = "SENT"
    ARCHIVE = "ARCHIVE"
    DRAFT = "DRAFT"
    DRAFT_INBOX = "DRAFT_INBOX"
