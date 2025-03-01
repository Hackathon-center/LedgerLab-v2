import { useState, useEffect } from "react";
import { connect, WalletConnection } from "near-api-js";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import axios from "axios";
import Dashboard from "./components/Dashboard";
import MemeDetail from "./components/MemeDetail";
import Navbar from "./components/Navbar";

import { Meme, Token } from "./utils";

const config = {
  networkId: "testnet",
  nodeUrl: "https://rpc.testnet.near.org",
  walletUrl: "https://wallet.testnet.near.org",
  helperUrl: "https://helper.testnet.near.org",
};

function App() {
  const [wallet, setWallet] = useState<WalletConnection | null>(null);
  const [memes, setMemes] = useState<Meme[]>([]);
  const [mintHistory, setMintHistory] = useState<Token[]>([]);

  useEffect(() => {
    initNear();
    fetchTrendingMemes();
  }, []);

  const initNear = async () => {
    const near = await connect(config);
    const wallet = new WalletConnection(near, "meme-app");
    setWallet(wallet);

    if (wallet.isSignedIn()) {
      fetchMintHistory(wallet.getAccountId());
    }
  };

  const fetchTrendingMemes = async () => {
    try {
      const res = await axios.get("/getTrending");
      setMemes(res.data.data);
    } catch (error) {
      console.error("Error fetching memes:", error);
    }
  };

  const fetchMintHistory = async (walletId: string) => {
    try {
      const res = await axios.get(`/mintHistory?wallet_id=${walletId}`);
      setMintHistory(res.data.data);
    } catch (error) {
      console.error("Error fetching mint history:", error);
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar wallet={wallet} onSignOut={() => setWallet(null)} />

        <Routes>
          <Route
            path="/"
            element={
              <Dashboard
                wallet={wallet}
                memes={memes}
                mintHistory={mintHistory}
                onMintSuccess={() =>
                  wallet && fetchMintHistory(wallet.getAccountId())
                }
              />
            }
          />
          <Route path="/meme/:id" element={<MemeDetail wallet={wallet} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
