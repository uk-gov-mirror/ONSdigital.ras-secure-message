from enum import Enum


class Labels(Enum):
    """Includes all labels for the api"""

    INBOX = "INBOX"
    UNREAD = "UNREAD"
    CLOSED = "CLOSED"
    SENT = "SENT"

    label_list = [INBOX, UNREAD, CLOSED, SENT]
