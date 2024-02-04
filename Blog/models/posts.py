from sqlalchemy.orm import relationship

from Blog import db


class BlogPost(db.Model):
    __tablename__ = "BlogPost"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post')
    