"use client"

import { useEffect ,useState
} from "react"
import { PendingTransfer } from "../types"
import api from "../lib/api"








export default function PendingTransfers(){
    const [pendingTransfers , setPendingTransfers] = useState<PendingTransfer[]>([])
    const [error, setError] = useState("")
    const [loading , setLoading] = useState(true)

    function fetchPendingTransfers(){
         api.get("/pending-transfers")
        .then((res)=>{
            setPendingTransfers(res.data)
        })
        .catch((err)=>{
            setError( err.response?.data?.detail ?? "Something went wrong")
        })
        .finally(()=>{
            setLoading(false)
        })

    }

    useEffect(()=>fetchPendingTransfers()
        ,[])

    // TODO (you write this one): call POST /pending-transfers/{id}/cancel,
    // then refetch so the list reflects the new "cancelled" status.
    function cancelTransfer(id: string) {
        api.post("/pending-transfers/"+id+"/cancel")
        .then(fetchPendingTransfers)
        .catch((err)=>{
            setError( err.response?.data?.detail ?? "Something went wrong")
        })

    }

    return (<div>
        <h1 className="mb-1 text-xl font-bold tracking-tight text-foreground">Pending transfers</h1>

        {error && (
          <p className="text-sm text-danger">{error}</p>
        )}

        {!loading && pendingTransfers.length === 0 && (
          <div
            className="reveal rounded-2xl border border-dashed border-border p-8 text-center text-sm text-muted">
            No pending transfers.
          </div>
        )}

        {!loading && pendingTransfers.length > 0 && (
          <div className="mb-10 flex flex-col gap-3">
            {pendingTransfers.map((transfer) => (
              <div
                key={transfer.id}
                className="reveal flex items-center justify-between rounded-2xl border border-border bg-surface p-5 transition hover:border-accent/40"
              >
                <div>
                  <p className="font-medium text-foreground">
                    {transfer.amount}
                  </p>
                  <p className="font-mono text-xs text-muted">
                    {transfer.toRib}
                  </p>
                  <p className="text-xs text-muted">
                    Available at {new Date(transfer.executeAt).toLocaleString()}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-mono text-xl font-semibold tabular-nums text-foreground">
                    {transfer.status}
                  </p>
                  <p className="mb-2 text-xs font-medium text-muted">
                    {transfer.description}
                  </p>
                  <button
                    onClick={() => cancelTransfer(transfer.id)}
                    className="rounded-lg border border-border px-3 py-1.5 text-xs font-semibold text-foreground transition hover:border-danger hover:text-danger"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

    </div>)
}