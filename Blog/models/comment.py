from sqlalchemy.orm import relationship

from Blog import db


class Comment(db.Model):
    __tablename__ = 'Comment'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('BlogPost.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    text = db.Column(db.Text, nullable=False)
    post = relationship('BlogPost', back_populates='comments')
    author = relationship('User', back_populates='comments')
    