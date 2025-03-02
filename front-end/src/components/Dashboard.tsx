import MemeCard from "./MemeCard";
import { Meme, Token } from "../utils";
import { WalletSelector } from "@near-wallet-selector/core";

// components/Dashboard.tsx
export default function Dashboard({
  wallet,
  memes,
  mintHistory,
  onMintSuccess,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  selector,
}: {
  wallet: string | null;
  memes: Meme[];
  mintHistory: Token[];
  onMintSuccess: () => void;
  selector: WalletSelector | null;
}) {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Memes Section */}
        <div>
          <h2 className="text-2xl font-bold mb-6 text-gray-800">
            Trending Memes
          </h2>
          <div className="grid grid-cols-1 gap-6">
            {memes.length === 0 ? (
              <p className="text-gray-500">No memes found</p>
            ) : (
              <>
                {memes.map((meme) => (
                  <MemeCard
                    key={meme.id}
                    meme={meme}
                    wallet={wallet}
                    mintHistory={mintHistory}
                    onMintSuccess={onMintSuccess}
                    selector={selector}
                  />
                ))}
              </>
            )}
          </div>
        </div>

        {/* Mint History */}
        <div>
          <h2 className="text-2xl font-bold mb-6 text-gray-800">
            Your Mint History
          </h2>
          <div className="bg-white rounded-lg shadow p-6">
            {mintHistory.length === 0 ? (
              <p className="text-gray-500">No mint history found</p>
            ) : (
              <div className="space-y-4">
                {mintHistory.map((history) => (
                  <div key={history.id} className="border-b pb-4">
                    <p className="font-medium">{history.token_name}</p>
                    <p className="text-sm text-gray-500">
                      Status: {history.status} •{" "}
                      {new Date(history.minted_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
