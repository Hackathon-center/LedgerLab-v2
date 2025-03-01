/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-unused-vars */
// App.tsx
import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import axios from "axios";
import Dashboard from "./components/Dashboard";
import MemeDetail from "./components/MemeDetail";
import Navbar from "./components/Navbar";
import { Meme, Token } from "./utils";
import {
  WalletSelector,
  setupWalletSelector,
  AccountState,
} from "@near-wallet-selector/core";
import { setupMyNearWallet } from "@near-wallet-selector/my-near-wallet";
import { setupSender } from "@near-wallet-selector/sender";
import { setupModal } from "@near-wallet-selector/modal-ui";
import "@near-wallet-selector/modal-ui/styles.css";

function App() {
  const [memes, setMemes] = useState<Meme[]>([]);
  const [mintHistory, setMintHistory] = useState<Token[]>([]);
  const [selector, setSelector] = useState<WalletSelector | null>(null);
  const [accountId, setAccountId] = useState<string | null>(null);
  const [modal, setModal] = useState<any>(null);

  useEffect(() => {
    const initializeWalletSelector = async () => {
      const selector = await setupWalletSelector({
        network: "testnet",
        modules: [setupMyNearWallet(), setupSender()],
      });

      const modal = setupModal(selector, {
        contractId: import.meta.env.VITE_CONTRACT_ID,
      });

      setSelector(selector);
      setModal(modal);

      const state = selector.store.getState();
      setAccountId(state.accounts[0]?.accountId || null);

      const subscription = selector.store.observable.subscribe((state) => {
        setAccountId(state.accounts[0]?.accountId || null);
      });

      //fetchTrendingMemes();

      return () => subscription.unsubscribe();
    };

    initializeWalletSelector();
  }, []);

  const fetchTrendingMemes = async () => {
    try {
      const res = await axios.get("http://localhost:5000/getTrending");
      setMemes(res.data.data);
    } catch (error) {
      console.error("Error fetching memes:", error);
    }
  };

  const fetchMintHistory = async (walletId: string) => {
    try {
      const res = await axios.get(
        `http://localhost:5000/mintHistory?wallet_id=${walletId}`
      );
      setMintHistory(res.data.data);
    } catch (error) {
      console.error("Error fetching mint history:", error);
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navbar
          accountId={accountId}
          onSignIn={() => modal.show()}
          onSignOut={() => {
            modal.hide();
            window.location.reload();
          }}
        />

        <Routes>
          <Route
            path="/"
            element={
              <Dashboard
                wallet={accountId}
                memes={memes}
                mintHistory={mintHistory}
                onMintSuccess={() => accountId && fetchMintHistory(accountId)}
              />
            }
          />
          <Route path="/meme/:id" element={<MemeDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
