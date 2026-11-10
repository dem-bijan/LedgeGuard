import type { PendingTransfer, User } from "../types";

// The one translation boundary between the backend's snake_case JSON and
// the frontend's camelCase User type. Called from both the client-side
// axios path (api.ts's response interceptor) and the server-side path
// (lib/getCurrentUser.ts) -- shaping is just data transformation, so the
// same function works regardless of how the raw data was fetched.
export function mapUser(data: { id: string; email: string; full_name: string; role: string }): User {
  return {
    id: data.id,
    email: data.email,
    fullName: data.full_name,
    role: data.role,
  };
}


export function mapPendingTransfer(data:{id:string, idempotency_key:string|null , description:string|null , status:string, execute_at:string  , amount:string , to_rib:string }): PendingTransfer{
  return {
    id: data.id,
  idempotencyKey: data.idempotency_key,
  description: data.description,
  status: data.status,
  executeAt: data.execute_at,
  amount: data.amount,
  toRib: data.to_rib
  }
}