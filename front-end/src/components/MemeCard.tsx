import axios from "axios";

import { useState } from "react";
import { Meme, Token } from "../utils";
import { WalletSelector } from "@near-wallet-selector/core";
// components/MemeCard.tsx
export default function MemeCard({
  meme,
  wallet,
  mintHistory,
  selector,
  onMintSuccess,
}: {
  meme: Meme;
  wallet: string | null;
  mintHistory: Token[];
  selector: WalletSelector | null;
  onMintSuccess: () => void;
}) {
  const [isMinting, setIsMinting] = useState(false);
  const alreadyMinted = mintHistory.some((h: Token) => h.meme_id === meme.id);

  const handleMint = async () => {
    if (!wallet || !selector) return;

    try {
      setIsMinting(true);

      // Get wallet connection
      const walletConnection = await selector.wallet();

      // Convert args to Uint8Array
      // const args = Buffer.from(
      //   JSON.stringify({
      //     args: {
      //       meme_id: meme.id.toString(),
      //       image_cid: meme.image_cid,
      //       title: meme.title,
      //       receiver_id: wallet, // Add this line
      //     },
      //   })
      // );

      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const result = await walletConnection.signAndSendTransaction({
        receiverId: import.meta.env.VITE_CONTRACT_ID,
        actions: [
          {
            type: "FunctionCall",
            params: {
              methodName: "nft_mint",
              args: {
                meme_id: meme.id.toString(),
                image_cid: meme.image_cid,
                title: meme.title,
              },
              gas: "300000000000000",
              deposit: "100000000000000000000000",
            },
          },
        ],
      });

      console.log(result);

      await axios.post("http://localhost:5000//mintToken", {
        wallet_id: wallet,
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
            <p>Upvotes: {meme.upvotes}</p>
            <p>Comments: {meme.comments}</p>
          </div>

          {wallet && (
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
