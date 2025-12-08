from sqlalchemy.orm import Session
from infr.posgres.models import user_events

class UserEventRep():
    def __init__(self, db : Session):
        self.db = db

    def log_event(self, user_id : int, article_id : int, event_type : str, event_value : int | None = None):
        event = UserEventRep(
            user_id = user_id,
            article_id = article_id,
            event_type = event_type,
            event_value = event_value
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def get_user_by_id(self, user_id : int):
        return self.db.query(UserEventRep).filter(UserEventRep.user_id == user_id).all()
    
    def get_by_article(self, article_id : int):
        return self.db.query(UserEventRep).filter(UserEventRep.article_id == article_id).all()
    
    def get_all(self):
        return self.db.query(UserEventRep).all()
    
    def delete_by_user(self,user_id : int):
        events = self.get_user_by_id(user_id)
        for e in events:
            self.db.delete(e)
        self.db.commit()
        return len(events)