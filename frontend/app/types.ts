// Frontend-side shape of a User. Fields are camelCase on purpose -- the
// backend sends snake_case JSON (full_name, etc). mapUser() in lib/maps.ts
// is the one place that translates between the two conventions, so this
// interface should always describe the *frontend's* idiomatic shape, not
// a mirror of the raw API response.
export interface User {
  id: string;
  email: string;
  fullName: string;
  role: string;
}


export interface Account{
    id: string;
    rib: string;
    label: string;
    currency: string;
    balance: string
}

export interface PendingTransfer{
  id: string;
  idempotencyKey: string | null;
  description: string | null;
  status: string;
  executeAt: string;
  amount: string;
  toRib: string;
}

export interface TransferRequest{
    idempotency_key: string;
    from_rib:string;
    to_rib:string;
    amount:string;
    description:string | null
    confirm_flagged_recipient: boolean | false

}