/* eslint-disable @typescript-eslint/no-unused-vars */

// components/Navbar.tsx
export default function Navbar({
  accountId,
  onSignIn,
  onSignOut,
}: {
  accountId: string | null;
  onSignIn: () => void;
  onSignOut: () => void;
}) {
  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">MemeNFT</h1>

        {accountId ? (
          <div className="flex items-center gap-4">
            <span className="text-gray-600">{accountId}</span>
            <button
              onClick={onSignOut}
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        ) : (
          <button
            onClick={onSignIn}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Connect Wallet
          </button>
        )}
      </div>
    </nav>
  );
}
