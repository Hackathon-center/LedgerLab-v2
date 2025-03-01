export interface Meme {
  id: number;
  picture: string;
  title: string;
  up_vote: number | null;
  comments: number | null;
  created_at: Date;
  metadata_cid: string;
  image_cid: string;
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
