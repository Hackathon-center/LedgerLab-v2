from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models import Meme, Tokens
# from near_api import NearRpcProvider, transactions, KeyPair, Account
from near_api.providers import JsonProvider
from near_api.signer import KeyPair
from near_api.account import Account
from near_api.transactions import Transaction, SignedTransaction


# should be put in .env once contract deployed
CONTRACT_ID = "D6qdR9WLs7Nx39iQeWWPr8CMm6fndbtHdP81Koa1CxLx"
OWNER_ACCOUNT_ID = "ledgerlabhack.testnet"
PRIVATE_KEY = "ed25519:4a2647HjvDJMPeV6RsoUVQgAn3t8nsgTMbD7BXocmEHUPSgVGYWSHqcCEhuLGwQLXRZozEmq7G5buA7n1yMQs3At"




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
        tokens = Tokens.query.filter_by(wallet_id=wallet_id).all()

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
    try :
        data = request.json
        wallet_id = data.get("wallet_id")
        meme_id = str(data.get("meme_id"))


        existing_mint = Tokens.query.filter_by(wallet_id=wallet_id, meme_id=meme_id).first()

        if existing_mint:
            return jsonify({"status" : 400 , "success" : False , "error" : 'You have already minted this meme!'})

        if not wallet_id or not meme_id:
            return jsonify({"status" : 400 , "success" : False , "error" : "missing details for transaction"})

        meme = Meme.query.get(meme_id)
        if not meme:
            return jsonify({"status" : 400 , "success" : False , "error" : "reletive meme not found"})


        token_name = f"Meme_{meme_id}_Token"
        new_token = Tokens(
            meme_id=meme_id,
            wallet_id=wallet_id,
            token_name=token_name,
            supply=1,
            minted_at=datetime.timestamp,
            status="pending"
        )
        db.session.add(new_token)
        db.session.commit()


        # NEAR initialization
        provider = JsonProvider("https://rpc.testnet.near.org")
        key_pair = KeyPair(PRIVATE_KEY)
        account = Account(provider, OWNER_ACCOUNT_ID, key_pair)


        # call the contracts mint method
        result = account.function_call(
            contract_id=CONTRACT_ID,
            method_name="mint_meme",
            args={"meme_id": meme_id , "image_cid" : meme.image_cid , "title" : meme.title},
            amount=0.1
        )

        new_token.status = "completed"
        db.session.commit()

        return jsonify({"status" : 200 , "success" : True , "transaction" : result})
    except Exception as e :

        new_token.status = "failed"
        db.session.commit()

        return jsonify({"status" : 500 , "success" : False , "error" : str(e)})


