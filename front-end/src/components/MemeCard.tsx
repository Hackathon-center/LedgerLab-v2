import axios from "axios";
import { WalletConnection } from "near-api-js";
import { useState } from "react";
import { Meme, Token } from "../utils";
// components/MemeCard.tsx
export default function MemeCard({
  meme,
  wallet,
  mintHistory,
  onMintSuccess,
}: {
  meme: Meme;
  wallet: WalletConnection | null;
  mintHistory: Token[];
  onMintSuccess: () => void;
}) {
  const [isMinting, setIsMinting] = useState(false);
  const alreadyMinted = mintHistory.some((h: Token) => h.meme_id === meme.id);

  const handleMint = async () => {
    if (!wallet?.isSignedIn()) return;

    try {
      setIsMinting(true);
      await axios.post("/mintToken", {
        wallet_id: wallet.getAccountId(),
        meme_id: meme.id,
      });
      onMintSuccess();
    } catch (error) {
      console.error("Minting failed:", error);
    } finally {
      setIsMinting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <img
        src={`https://ipfs.io/ipfs/${meme.image_cid}`}
        alt={meme.title}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2">{meme.title}</h3>

        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-500">
            <p>Upvotes: {meme.up_vote}</p>
            <p>Comments: {meme.comments}</p>
          </div>

          {wallet?.isSignedIn() && (
            <button
              onClick={handleMint}
              disabled={alreadyMinted || isMinting}
              className={`px-4 py-2 rounded ${
                alreadyMinted
                  ? "bg-gray-300 cursor-not-allowed"
                  : "bg-green-500 hover:bg-green-600 text-white"
              }`}
            >
              {alreadyMinted ? "Minted" : isMinting ? "Minting..." : "Mint NFT"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
