from app import db
from datetime import datetime


class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    picture = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    up_vote = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    metadata_cid = db.Column(db.String, nullable=False)
    image_cid = db.Column(db.String, nullable=False)

    tokens = db.relationship('Tokens', backref='memes', lazy=True)

class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meme_id = db.Column(db.Integer, db.ForeignKey("meme.id"), nullable=False)
    wallet_id = db.Column(db.String, nullable=False)
    token_name = db.Column(db.String, nullable=False)
    supply = db.Column(db.Integer)
    minted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String, nullable=False)
