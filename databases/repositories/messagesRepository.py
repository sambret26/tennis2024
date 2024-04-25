from databases.domains.messages import Message
from sqlalchemy.orm import sessionmaker
from databases.base import Base
from sqlalchemy import func

class MessagesRepository:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    # GETTERS
    def getMessages(self, session, category):
        return session.query(Message.id, Message.message).filter(Message.category == category).all()

    # INSERT
    def insertMessage(self, session, category, message):
        newMessage = Message(category=category, message=message)
        session.add(newMessage)
        session.commit()

    # DELETE
    def deleteMessageById(self, session, id):
        messageToDelete = session.query(Message).filter(Message.id == id).first()
        if messageToDelete:
            session.delete(messageToDelete)
            session.commit()
            return True
        return False
