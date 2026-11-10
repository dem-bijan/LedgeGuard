"use client"

import type { User, Account } from "../types"
import { useEffect, useState, type CSSProperties } from "react"
import api from "../lib/api"
import TransfertForm from "./TransferForm"
import PendingTransfers from "./PendingTransfers"

export default function DashboardContent({ user }: { user: User }) {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)

  function fetchAccounts() {
    api
      .get("/accounts")
      .then((res) => {
        setAccounts(res.data)
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchAccounts()
  }, [])

  const initials = user.fullName
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase()

  // Staggered entrance: each delay() call hands an element its own spot
  // in the same reveal sequence, via the --reveal-delay custom property
  // the .reveal keyframe in globals.css reads.
  const delay = (ms: number): CSSProperties =>
    ({ "--reveal-delay": `${ms}ms` }) as CSSProperties

  return (
    <div className="min-h-screen bg-background">
      <header className="reveal border-b border-border bg-surface" style={delay(0)}>
        <div className="mx-auto flex max-w-2xl items-center gap-2.5 px-4 py-4">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent text-sm font-bold text-accent-foreground">
            L
          </span>
          <span className="text-base font-semibold tracking-tight text-foreground">
            LedgerGuard
          </span>
        </div>
      </header>

      <div className="mx-auto max-w-2xl px-4 py-12">
        <div
          className="reveal mb-10 flex items-center gap-4"
          style={delay(60)}
        >
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-semibold text-accent-foreground">
            {initials}
          </div>
          <div>
            <p className="text-lg font-semibold tracking-tight text-foreground">
              {user.fullName}
            </p>
            <p className="text-sm text-muted">{user.email}</p>
          </div>
        </div>

        <div className="reveal" style={delay(120)}>
          <h1 className="mb-1 text-2xl font-bold tracking-tight text-foreground">
            Your accounts
          </h1>
          <p className="mb-6 text-sm text-muted">
            Balances across every account you own
          </p>
        </div>

        {loading && (
          <p className="reveal text-sm text-muted" style={delay(160)}>
            Loading accounts...
          </p>
        )}

        {!loading && accounts.length === 0 && (
          <div
            className="reveal rounded-2xl border border-dashed border-border p-8 text-center text-sm text-muted"
            style={delay(160)}
          >
            No accounts yet.
          </div>
        )}

        {!loading && accounts.length > 0 && (
          <div className="mb-10 flex flex-col gap-3">
            {accounts.map((account, i) => (
              <div
                key={account.id}
                className="reveal flex items-center justify-between rounded-2xl border border-border bg-surface p-5 transition hover:border-accent/40"
                style={delay(160 + i * 50)}
              >
                <div>
                  <p className="font-medium text-foreground">
                    {account.label}
                  </p>
                  <p className="font-mono text-xs text-muted">
                    {account.rib}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-mono text-xl font-semibold tabular-nums text-foreground">
                    {account.balance}
                  </p>
                  <p className="text-xs font-medium text-muted">
                    {account.currency}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
        <div className="reveal mb-10" style={delay(160 + accounts.length * 50 + 50)}>
          <PendingTransfers />
        </div>

        <div className="reveal" style={delay(160 + accounts.length * 50 + 100)}>
          <TransfertForm accounts={accounts} onTransfertSuccess={fetchAccounts}></TransfertForm>
        </div>
      </div>
    </div>
  )
}
