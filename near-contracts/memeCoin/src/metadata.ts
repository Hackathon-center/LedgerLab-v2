export class NFTMetadata {
  spec: string;
  name: string;
  symbol: string;
  icon: string | null;
  base_uri: string | null;
  reference: string | null;
  reference_hash: string | null;
}

export class TokenMetadata {
  title: string;
  description: string;
  media: string;
  media_hash: string | null;
  copies: number;
  issued_at: number | null;
  expires_at: number | null;
  starts_at: number | null;
  updated_at: number | null;
  extra: string | null;
  reference: string | null;
  reference_hash: string | null;

  constructor(
    title: string,
    description: string,
    media: string,
    copies: number = 1,
    extra?: { [key: string]: any }
  ) {
    this.title = title;
    this.description = description;
    this.media = media;
    this.copies = copies;
    this.media_hash = null;
    this.issued_at = Date.now();
    this.expires_at = null;
    this.starts_at = null;
    this.updated_at = null;
    this.extra = extra ? JSON.stringify(extra) : null;
    this.reference = null;
    this.reference_hash = null;
  }
}

export class Token {
  token_id: string;
  owner_id: string;
  approved_account_ids: { [account: string]: number };
  metadata: TokenMetadata;

  constructor(
    token_id: string,
    owner_id: string,
    creator_id: string,
    metadata: TokenMetadata
  ) {
    this.token_id = token_id;
    this.owner_id = owner_id;
    this.approved_account_ids = { [creator_id]: Date.now() };
    this.metadata = metadata;
  }
}
