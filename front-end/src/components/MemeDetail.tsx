// components/MemeDetail.tsx
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import { Meme } from "../utils";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const MemeDetail = () => {
  const { id } = useParams();
  const [meme, setMeme] = useState<Meme>();

  useEffect(() => {
    const fetchMeme = async () => {
      try {
        const res = await axios.get(`/getTrending`);
        const foundMeme = res.data.data.find((m: Meme) => m.id === Number(id));
        setMeme(foundMeme);
      } catch (error) {
        console.error("Error fetching meme:", error);
      }
    };

    fetchMeme();
  }, [id]);

  if (!meme) return <div>Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <img
          src={`https://ipfs.io/ipfs/${meme.image_cid}`}
          alt={meme.title}
          className="w-full h-96 object-contain"
        />
        <div className="p-6">
          <h1 className="text-3xl font-bold mb-4">{meme.title}</h1>
          <div className="grid grid-cols-2 gap-4 text-gray-600">
            <p>Created: {new Date(meme.created_at).toLocaleDateString()}</p>
            <p>Upvotes: {meme.upvotes}</p>
            <p>Comments: {meme.comments}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemeDetail;
