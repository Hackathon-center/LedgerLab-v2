from datetime import datetime
import os
from dotenv import load_dotenv
from flask import Blueprint, app, json, request, jsonify
from app import db
from app.models import Meme, Tokens
# from near_api import NearRpcProvider, transactions, KeyPair, Account
from near_api.providers import JsonProvider
from near_api.signer import KeyPair
from near_api.account import Account
from near_api.transactions import Transaction, SignedTransaction



load_dotenv()

# Access environment variables
CONTRACT_ID = os.getenv("CONTRACT_ID")
OWNER_ACCOUNT_ID= os.getenv("OWNER_ACCOUNT_ID ")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")





main_bp = Blueprint("main", __name__)

@main_bp.route("/getTrending", methods=["GET"])
def get_top_trending_memes():
    try:
        trending_memes = Meme.query.order_by(Meme.created_at.desc()).limit(10).all()

        results = []
        for meme in trending_memes:
            results.append({
                "id": meme.id,
                "title": meme.title,
                "picture": meme.picture,
                "upvotes": meme.up_vote,
                "comments": meme.comments,
                "created_at": meme.created_at.isoformat(),
                "image_cid": meme.image_cid,
                "metadata_cid": meme.metadata_cid
            })


        return jsonify({"status": 200, "data": results})
    except Exception as e:
        return jsonify({"status": 500, "error": str(e)})


@main_bp.route("/mintHistory", methods=["GET"])
def mint_history():
    try:
        wallet_id = request.args.get("wallet_id")

        if not wallet_id:
            return jsonify({"status": 400, "success": False, "error": "Wallet ID is required"})

        # Get all tokens minted by this wallet
        tokens = Tokens.query.filter_by(wallet_id=wallet_id).order_by(Tokens.minted_at.desc()).limit(10).all()

        if not tokens:
            return jsonify({"status": 200, "success": True, "data": []})

        results = []
        for token in tokens:
            results.append({
                "token_id": token.id,
                "meme_id": token.meme_id,
                "token_name": token.token_name,
                "supply": token.supply,
                "minted_at": token.minted_at.isoformat() if isinstance(token.minted_at, datetime) else token.minted_at,
                "status": token.status
            })

        return jsonify({"status": 200, "success": True, "data": results})

    except Exception as e:
        return jsonify({"status": 500, "success": False, "error": str(e)})





@main_bp.route("/mintToken", methods=["POST"])
def mint_token():
    try:
        data = request.json
        wallet_id = data.get("wallet_id")
        meme_id = str(data.get("meme_id"))
        #tx_hash = data.get("tx_hash")

        if not all([wallet_id, meme_id]):
            return jsonify({"status": 400, "error": "Missing required fields"})

        # Check existing mints
        existing = Tokens.query.filter_by(
            wallet_id=wallet_id,
            meme_id=meme_id,
            status="completed"
        ).first()

        if existing:
            return jsonify({"status": 400, "error": "Already minted"})

        # # Verify transaction (pseudo-code)
        # if not verify_transaction(tx_hash, wallet_id, meme_id):
        #     return jsonify({"status": 400, "error": "Invalid transaction"})

        # Record in database
        new_token = Tokens(
            meme_id=meme_id,
            wallet_id=wallet_id,
            token_name=f"Meme_{meme_id}_Token",
            status="completed",
            minted_at=datetime.now()
        )
        db.session.add(new_token)
        db.session.commit()

        return jsonify({"status": 200, "success": True})

    except Exception as e:
        return jsonify({"status": 500, "error": str(e)})
