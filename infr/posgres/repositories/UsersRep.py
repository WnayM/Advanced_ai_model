from sqlalchemy.orm import Session
from infr.posgres.models import User

class UsersRep:
    def __init__(self,db : Session):
        self.db = db
    
    def create(self, external_id : str):
        user = User(external_id = external_id)
        self.db.add(user)
        self.db.commit()
        self.db.refresh()
        return user
    
    def get_by_id(self, user_id : int):
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_external_id(self, external_id : str):
        return self.db.query(User).filter(User.external_id == external_id).first()
    
    def update(self, user_id : int, **kwargs):
        user = self.get_by_id(user_id)
        if not user:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id : int):
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
    