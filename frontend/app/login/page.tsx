"use client"

import { useRouter } from "next/navigation"
import api from "../lib/api"
import { setCredentials } from "../store/authSlice"
import { useDispatch } from "react-redux"
import { useState } from "react"

export default function Login() {
  const dispatch = useDispatch()
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    // /login only sets the auth cookie (httpOnly -- JS can't read it);
    // it doesn't return who the user is. The follow-up /me call is how
    // we actually find out, and its response arrives pre-mapped to
    // camelCase via the interceptor in lib/api.ts.
    api.post("/login", { email, password })
      .then(() => api.get("/me"))
      .then((res) => {
        dispatch(setCredentials({ user: res.data }))
        router.push("/")
      })
      .catch(() => setError("Invalid email or password"))
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 bg-background px-4">
      <div className="reveal flex items-center gap-2.5" style={{ "--reveal-delay": "0ms" } as React.CSSProperties}>
        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent text-sm font-bold text-accent-foreground">
          L
        </span>
        <span className="text-base font-semibold tracking-tight text-foreground">
          LedgerGuard
        </span>
      </div>

      <div
        className="reveal w-full max-w-sm rounded-2xl border border-border bg-surface p-8 shadow-sm"
        style={{ "--reveal-delay": "80ms" } as React.CSSProperties}
      >
        <h1 className="mb-1 text-2xl font-bold tracking-tight text-foreground">
          Welcome back
        </h1>
        <p className="mb-6 text-sm text-muted">
          Log in to your account
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="text-sm font-medium text-foreground">
              Email
            </label>
            <input
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              placeholder="you@example.com"
              className="rounded-lg border border-border bg-transparent px-3 py-2 text-sm text-foreground outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/15"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="password" className="text-sm font-medium text-foreground">
              Password
            </label>
            <input
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              placeholder="••••••••"
              className="rounded-lg border border-border bg-transparent px-3 py-2 text-sm text-foreground outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/15"
            />
          </div>

          {error && (
            <p className="text-sm text-danger">{error}</p>
          )}

          <button
            type="submit"
            className="mt-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground transition hover:opacity-90"
          >
            Log in
          </button>
        </form>
      </div>
    </div>
  )
}
