"use client"
import api from "../lib/api"
import { useState } from "react"
import { Account } from "../types"




// class TransferRequest(BaseModel):
//     idempotency_key: str
    
//     from_rib: str
//     to_rib: str
//     amount: Decimal = Field(gt=Decimal(0))
//     description: str | None = None

interface TransferRequest{
    idempotency_key: string;
    from_rib:string;
    to_rib:string;
    amount:string;
    description:string | null

}

export default function TransfertForm({accounts,onTransfertSuccess}:{accounts:Account[],onTransfertSuccess:()=>void}){
    const [idempotencyKey,setIdempotencyKey] = useState(()=>crypto.randomUUID())
    const [amount,setAmount] = useState("")
    const [fromRib , setFromRib] = useState("")
    const [toRib , setToRib] = useState("")
    const [description, setDescription] = useState("")
    const [error, setError] = useState("")
    const [submitting, setSubmitting] = useState(false)

    function onSubmit(e:React.FormEvent){
        e.preventDefault()
        setSubmitting(true)
        setError("")
        const requested :TransferRequest = {
            idempotency_key: idempotencyKey,
            from_rib: fromRib,
            to_rib:toRib,
            amount: String(amount),
            description: description
        }
        api.post("/transfer", requested)
        .then(()=>{
            setIdempotencyKey(crypto.randomUUID())
            onTransfertSuccess()
            setToRib("")
            setAmount("")
            setDescription("")
        })
        .catch((err)=>{setError(err.response?.data?.detail ?? "Network error")})
        .finally(()=>setSubmitting(false))

    }

    return (
        <form
            onSubmit={onSubmit}
            className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-6 shadow-sm"
        >
            <h2 className="text-base font-semibold tracking-tight text-foreground">
                Send money
            </h2>

            <div className="flex flex-col gap-1.5">
                <label htmlFor="fromRib" className="text-sm font-medium text-foreground">
                    From
                </label>
                <select
                    id="fromRib"
                    value={fromRib}
                    onChange={(e) => setFromRib(e.target.value)}
                    required
                    className="rounded-lg border border-border bg-transparent px-3 py-2 text-sm text-foreground outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/15"
                >
                    <option value="" disabled>
                        Select an account
                    </option>
                    {accounts.map((account) => (
                        <option key={account.id} value={account.rib}>
                            {account.label} — {account.balance} {account.currency}
                        </option>
                    ))}
                </select>
            </div>

            <div className="flex flex-col gap-1.5">
                <label htmlFor="toRib" className="text-sm font-medium text-foreground">
                    To (RIB)
                </label>
                <input
                    id="toRib"
                    value={toRib}
                    onChange={(e) => setToRib(e.target.value)}
                    placeholder="24-digit RIB"
                    required
                    className="rounded-lg border border-border bg-transparent px-3 py-2 font-mono text-sm text-foreground outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/15"
                />
            </div>

            <div className="flex flex-col gap-1.5">
                <label htmlFor="amount" className="text-sm font-medium text-foreground">
                    Amount
                </label>
                <input
                    id="amount"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="0.00"
                    required
                    className="rounded-lg border border-border bg-transparent px-3 py-2 font-mono text-sm text-foreground outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/15"
                />
            </div>

            <div className="flex flex-col gap-1.5">
                <label htmlFor="description" className="text-sm font-medium text-foreground">
                    Note <span className="font-normal text-muted">(optional)</span>
                </label>
                <input
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="What's this for?"
                    className="rounded-lg border border-border bg-transparent px-3 py-2 text-sm text-foreground outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/15"
                />
            </div>

            {error && (
                <p className="text-sm text-danger">{error}</p>
            )}

            <button
                type="submit"
                disabled={submitting}
                className="mt-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
                {submitting ? "Sending..." : "Send"}
            </button>
        </form>
    )
}