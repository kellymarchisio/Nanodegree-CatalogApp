from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }


class Item(Base):
    __tablename__ = 'item'
   
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, nullable=False)
    name = Column(String(250), nullable=False)
    description = Column(String(250))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
           'parent_id'      : self.parent_id,
           'description'  : self.description,
       }

class User(Base):
    __tablename__ = 'user'

    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'email'        : self.email,
           'picture'      : self.picture,
           'id'           : self.id,
       }


engine = create_engine('postgresql+psychopg2://catalog:catalog@52.88.17.188/catalog')

Base.metadata.create_all(engine)
