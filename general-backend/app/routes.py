from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models import Meme, Tokens
from near_api import NearRpcProvider, transactions, KeyPair, Account


# should be put in .env once contract deployed
CONTRACT_ID = ""
OWNER_ACCOUNT_ID = ""
PRIVATE_KEY = ""





main_bp = Blueprint("main", __name__)

@main_bp.route("/getTrending", methods=["GET"])
def get_top_trending_memes():
    pass

@main_bp.route("/mintHistory", methods=["GET"])
def mint_history():
    pass


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
            minted_at=datetime.timestamp(),
            status="pending"
        )
        db.session.add(new_token)
        db.session.commit()


        # NEAR initialization
        provider = NearRpcProvider("https://rpc.testnet.near.org")
        key_pair = KeyPair(PRIVATE_KEY)
        account = Account(provider, OWNER_ACCOUNT_ID, key_pair)


        # call the contracts mint method
        result = account.function_call(
            contract_id=CONTRACT_ID,
            method_name="mint_meme",
            args={"meme_id": meme_id},
            gas=30000000000000,
            amount=0.1
        )

        new_token.status = "completed"
        db.session.commit()

        return jsonify({"status" : 200 , "success" : True , "transaction" : result})
    except Exception as e :

        new_token.status = "failed"
        db.session.commit()

        return jsonify({"status" : 500 , "success" : False , "error" : str(e)})


