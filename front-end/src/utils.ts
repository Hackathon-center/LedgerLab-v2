export interface Meme {
  comments: number | null;
  created_at: Date;
  id: number;
  image_cid: string;
  metadata_cid: string;
  picture: string;
  title: string;
  upvotes: number | null;
  tokens?: Token[];
}

export interface Token {
  id: number;
  meme_id: number;
  wallet_id: string;
  token_name: string;
  supply: number | null;
  minted_at: Date;
  status: string;
  meme?: Meme;
}
