import threading

from sqlalchemy import Column, String
from PrimeMega.modules.sql import BASE, SESSION

class PrimeMega(BASE):
    __tablename__ = "prime_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id

PrimeMega.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_prime(chat_id):
    try:
        chat = SESSION.query(PrimeMega).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()

def set_prime(chat_id):
    with INSERTION_LOCK:
        primemega = SESSION.query(PrimeMega).get(str(chat_id))
        if not primemega:
            primemega = PrimeMega(str(chat_id))
        SESSION.add(primemega)
        SESSION.commit()

def rem_prime(chat_id):
    with INSERTION_LOCK:
        primemega = SESSION.query(PrimeMega).get(str(chat_id))
        if primemega:
            SESSION.delete(primemega)
        SESSION.commit()


def get_all_prime_chats():
    try:
        return SESSION.query(PrimeMega.chat_id).all()
    finally:
        SESSION.close()
