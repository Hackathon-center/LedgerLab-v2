from flask import Blueprint, request, jsonify
from app import db
from app.models import Meme, Token

main_bp = Blueprint("main", __name__)

@main_bp.route("/getTrending", methods=["GET"])
def get_top_trending_memes():
    pass

@main_bp.route("/mintHistory", methods=["GET"])
def mint_history():
    pass


@main_bp.route("/mintToken", methods=["POST"])
def mint_token():
    pass

