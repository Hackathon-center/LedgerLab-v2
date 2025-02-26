from app import db
from datetime import datetime


class User(db.Model):
    wallet_id = db.Column(db.String, primary_key=True)


class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    up_vote = db.Column(db.Integer)
    comments = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.timestamp)
    metadata_cid = db.Column(db.String, nullable=False)
    image_cid = db.Column(db.String, nullable=False)

class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meme_id = db.Column(db.Integer, db.ForeignKey("meme.id"), nullable=False)
    wallet_id = db.Column(db.String, db.ForeignKey("user.wallet_id"), nullable=False)
    token_name = db.Column(db.String, nullable=False)
    supply = db.Column(db.Integer)
    minted_at = db.Column(db.DateTime, default=datetime.timestamp)
    status = db.Column(db.String, nullable=False)

    meme = db.relationship("Meme", backref="tokens")
    user = db.relationship("User", backref="tokens")
