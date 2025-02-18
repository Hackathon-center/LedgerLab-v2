from app import db
from datetime import datetime

class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    trend_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meme_id = db.Column(db.Integer, db.ForeignKey("meme.id"), nullable=False)
    token_name = db.Column(db.String, nullable=False)
    supply = db.Column(db.Integer)
    minted_at = db.Column(db.DateTime, default=datetime.timestamp)
    status = db.Column(db.String, nullable=False)

    meme = db.relationship("Meme", backref="tokens")
