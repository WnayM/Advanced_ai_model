from sqlalchemy.orm import Session
from infr.posgres.models import articles

class ArticlesRep :
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, url : str, title : str, content : str, source : str, language : str):
        article = articles(
            url = url,
            title = title,
            content = content,
            source = source,
            language = language
        )

        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def get_by_id(self, article_id : int) -> articles | None :
        return self.db.query(articles).filter(articles.id == article_id).first()
    
    def get_all(self) -> list[articles]:
        return self.db.query(articles).all()
    
    def get_by_url(self, url : str) -> articles | None :
        return self.db.query(articles).filter(articles.url == url).first()
    
    def update(self, article_id : int, **kwargs):
        article = self.get_by_id(article_id)
        if not article:
            return None
        for key, value in kwargs.items():
            setattr(article,key,value)
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def update(self, article_id : int, **kwargs):
        article = self.get_by_id(article_id)
        if not article:
            return None
        for key, value in kwargs.item():
            setattr(article,key,value)
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def delete(self, article_id : int):
        article = self.get_by_id(article_id)
        if not article :
            return False
        self.db.delete(article)
        self.db.commit()
        return True