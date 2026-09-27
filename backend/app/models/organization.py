from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Organization(BaseModel):
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    industry = Column(String(255))
    website = Column(String(255))
    
    members = relationship("User", back_populates="organization")
