"use client"

import type { User, Account } from "../types"
import { useEffect, useState } from "react"
import api from "../lib/api"
import TransfertForm from "./TransferForm"

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

  return (
    <div className="min-h-screen bg-zinc-50 px-4 py-10 dark:bg-black">
      <div className="mx-auto max-w-2xl">
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
          Welcome back, {user.fullName}
        </h1>
        <p className="mb-8 text-sm text-zinc-500 dark:text-zinc-400">
          Here are your accounts
        </p>

        {loading && (
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading accounts...</p>
        )}

        {!loading && accounts.length === 0 && (
          <div className="rounded-2xl border border-dashed border-zinc-200 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-400">
            No accounts yet.
          </div>
        )}

        {!loading && accounts.length > 0 && (
          <div className="flex flex-col gap-3">
            {accounts.map((account) => (
              <div
                key={account.id}
                className="flex items-center justify-between rounded-2xl bg-white p-5 shadow-sm dark:bg-zinc-900"
              >
                <div>
                  <p className="font-medium text-zinc-900 dark:text-zinc-50">
                    {account.label}
                  </p>
                  <p className="font-mono text-xs text-zinc-400 dark:text-zinc-500">
                    {account.rib}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                    {account.balance}
                  </p>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400">
                    {account.currency}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
        <TransfertForm accounts={accounts} onTransfertSuccess={fetchAccounts}></TransfertForm>
      </div>
    </div>
  )
}
