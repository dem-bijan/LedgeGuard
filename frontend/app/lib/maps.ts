import type { User } from "../types";

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
