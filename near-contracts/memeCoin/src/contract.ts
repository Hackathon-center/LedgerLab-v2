// import {
//   NearBindgen,
//   near,
//   call,
//   view,
//   initialize,
//   LookupMap,
//   UnorderedMap,
// } from "near-sdk-js";

// class NFTMetadata {
//   id: number;
//   name: string;
//   symbol: string;
//   media: string;

//   constructor(id: number, name: string, symbol: string, media: string) {
//     this.id = id;
//     this.name = name;
//     this.symbol = symbol;
//     this.media = media;
//   }
// }

// class TokenMetadata {
//   title: string;
//   description: string;
//   media: string;
//   copies: number;
//   issued_at: string;
//   expires_at: string;
//   starts_at: string;

//   constructor(title: string, description: string, media: string) {
//     this.title = title;
//     this.description = description;
//     this.media = media;
//     this.copies = 1;
//     this.issued_at = null;
//     this.expires_at = null;
//     this.starts_at = null;
//   }
// }

// class Meme {
//   id: number;
//   picture: string;
//   title: string;
//   trend_score: number;
//   created_at: bigint;
//   content_identifier: string;
//   minted: boolean;

//   constructor(
//     id: number,
//     picture: string,
//     title: string,
//     trend_score: number,
//     content_identifier: string
//   ) {
//     this.id = id;
//     this.picture = picture;
//     this.title = title;
//     this.trend_score = trend_score;
//     this.created_at = near.blockTimestamp();
//     this.content_identifier = content_identifier;
//     this.minted = false;
//   }
// }

// class Token {
//   token_id: string;
//   owner_id: string;
//   metadata: TokenMetadata;
//   meme_id: number;
//   token_name: string;
//   supply: number;
//   minted_at: bigint;
//   status: string;

//   constructor(
//     token_id: string,
//     owner_id: string,
//     metadata: TokenMetadata,
//     meme_id: number,
//     token_name: string,
//     supply: number
//   ) {
//     this.token_id = token_id;
//     this.owner_id = owner_id;
//     this.metadata = metadata;
//     this.meme_id = meme_id;
//     this.token_name = token_name;
//     this.supply = supply;
//     this.minted_at = near.blockTimestamp();
//     this.status = "minted";
//   }
// }

// @NearBindgen({ requireInit: true })
// class MemeNFTContract {
//   owner_id: string;
//   metadata: NFTMetadata;
//   tokens_per_owner: LookupMap<string[]>;
//   tokens_by_id: LookupMap<Token>;
//   token_metadata_by_id: UnorderedMap<TokenMetadata>;
//   memes: UnorderedMap<Meme>;
//   token_id_counter: number;

//   constructor() {
//     this.owner_id = "";
//     this.metadata = null;
//     this.tokens_per_owner = new LookupMap("tokens_per_owner");
//     this.tokens_by_id = new LookupMap("tokens_by_id");
//     this.token_metadata_by_id = new UnorderedMap("token_metadata_by_id");
//     this.memes = new UnorderedMap("memes");
//     this.token_id_counter = 0;
//   }

//   @initialize({})
//   init({ owner_id, metadata }: { owner_id: string; metadata: NFTMetadata }) {
//     this.owner_id = owner_id;
//     this.metadata = metadata;
//   }

//   // Add memes to the contract
//   @call({ payableFunction: false })
//   add_memes({
//     memes,
//   }: {
//     memes: Array<{
//       id: number;
//       picture: string;
//       title: string;
//       trend_score: number;
//       content_identifier: string;
//     }>;
//   }) {
//     this.assert_owner();

//     for (let i = 0; i < memes.length; i++) {
//       const memeData = memes[i];
//       const existingMeme = this.memes.get(memeData.id.toString());

//       if (!existingMeme) {
//         const newMeme = new Meme(
//           memeData.id,
//           memeData.picture,
//           memeData.title,
//           memeData.trend_score,
//           memeData.content_identifier
//         );
//         this.memes.set(memeData.id.toString(), newMeme);
//       } else {
//         existingMeme.trend_score = memeData.trend_score;
//         this.memes.set(memeData.id.toString(), existingMeme);
//       }
//     }
//   }

//   //  mint a specific meme
//   @call({ payableFunction: true })
//   mint_meme({ meme_id }: { meme_id: string }) {
//     const meme = this.memes.get(meme_id);

//     if (!meme) {
//       throw new Error("Meme not found");
//     }

//     if (meme.minted) {
//       throw new Error("Meme already minted");
//     }

//     const token_id = (this.token_id_counter++).toString();
//     const caller = near.predecessorAccountId();

//     const metadata = new TokenMetadata(
//       meme.title,
//       `Reddit meme NFT with trend score ${meme.trend_score}`,
//       meme.picture
//     );

//     const token_name = `MEME-${meme.id}`;
//     const supply = 1;

//     const token = new Token(
//       token_id,
//       caller,
//       metadata,
//       meme.id,
//       token_name,
//       supply
//     );

//     this.tokens_by_id.set(token_id, token);

//     const tokens = this.tokens_per_owner.get(caller) || [];
//     tokens.push(token_id);
//     this.tokens_per_owner.set(caller, tokens);

//     this.token_metadata_by_id.set(token_id, metadata);

//     meme.minted = true;
//     this.memes.set(meme_id, meme);

//     return {
//       id: parseInt(token_id),
//       meme_id: meme.id,
//       wallet_id: caller,
//       token_name: token_name,
//       supply: supply,
//       minted_at: token.minted_at,
//       status: token.status,
//     };
//   }

//   // get tokens owned by a specific account
//   @view({})
//   get_tokens_by_owner({ account_id }: { account_id: string }): Token[] {
//     const token_ids = this.tokens_per_owner.get(account_id) || [];
//     const tokens: Token[] = [];

//     for (let i = 0; i < token_ids.length; i++) {
//       const token = this.tokens_by_id.get(token_ids[i]);
//       tokens.push(token);
//     }

//     return tokens;
//   }

//   // Get specific token details
//   @view({})
//   get_token_details({ token_id }: { token_id: string }) {
//     const token = this.tokens_by_id.get(token_id);
//     if (!token) {
//       throw new Error("Token not found");
//     }

//     const meme = this.memes.get(token.meme_id.toString());

//     return {
//       id: parseInt(token_id),
//       meme_id: token.meme_id,
//       wallet_id: token.owner_id,
//       token_name: token.token_name,
//       supply: token.supply,
//       minted_at: token.minted_at,
//       status: token.status,
//       content_identifier: meme.content_identifier,
//       picture: meme.picture,
//       title: meme.title,
//       trend_score: meme.trend_score,
//     };
//   }

//   // verify the caller is the owner
//   assert_owner() {
//     const caller = near.predecessorAccountId();
//     if (caller !== this.owner_id) {
//       throw new Error("Only the owner can call this method");
//     }
//   }
// }

class TokenMetadata {
  title: string;
  description: string;
  media: string;
  copies: number;
  issued_at: string | null; // Allow null
  expires_at: string | null; // Allow null
  starts_at: string | null; // Allow null

  constructor(title: string, description: string, media: string) {
    this.title = title;
    this.description = description;
    this.media = media;
    this.copies = 1;
    this.issued_at = null;
    this.expires_at = null;
    this.starts_at = null;
  }
}

class Token {
  token_id: string;
  owner_id: string;
  metadata: TokenMetadata;
  meme_id: number;
  token_name: string;
  supply: number;
  minted_at: bigint;
  status: string;

  constructor(
    token_id: string,
    owner_id: string,
    metadata: TokenMetadata,
    meme_id: number,
    token_name: string,
    supply: number
  ) {
    this.token_id = token_id;
    this.owner_id = owner_id;
    this.metadata = metadata;
    this.meme_id = meme_id;
    this.token_name = token_name;
    this.supply = supply;
    this.minted_at = near.blockTimestamp();
    this.status = "minted";
  }
}

import { NearBindgen, near, call, view, UnorderedMap } from "near-sdk-js";

@NearBindgen({})
class MemeNFTContract {
  tokens_by_id: UnorderedMap<Token>;
  tokens_per_owner: UnorderedMap<string[]>;
  token_id_counter: number;

  constructor() {
    this.tokens_by_id = new UnorderedMap("tokens_by_id");
    this.tokens_per_owner = new UnorderedMap("tokens_per_owner");
    this.token_id_counter = 0;
  }

  @call({ payableFunction: true })
  mint_meme({
    meme_id,
    image_cid,
    title,
  }: {
    meme_id: string;
    image_cid: string;
    title: string;
  }) {
    const caller = near.predecessorAccountId();
    const token_id = (this.token_id_counter++).toString();

    // Construct TokenMetadata instance
    const metadata = new TokenMetadata(
      title,
      `A trending meme NFT with ID ${meme_id}`,
      `https://gateway.ipfs.io/ipfs/${image_cid}`
    );

    const token = new Token(
      token_id,
      caller,
      metadata,
      parseInt(meme_id),
      `Meme_${meme_id}_Token_for_${caller}`,
      1
    );

    // Store token
    this.tokens_by_id.set(token_id, token);

    // Update ownership
    const tokens = this.tokens_per_owner.get(caller) || [];
    tokens.push(token_id);
    this.tokens_per_owner.set(caller, tokens);

    return {
      status: 200,
      success: true,
      transaction: {
        token_id,
        meme_id: parseInt(meme_id),
        wallet_id: caller,
      },
    };
  }

  @view({})
  get_token({ token_id }: { token_id: string }) {
    return this.tokens_by_id.get(token_id) || null;
  }

  @view({})
  get_tokens_by_owner({ owner_id }: { owner_id: string }) {
    return this.tokens_per_owner.get(owner_id) || [];
  }
}
