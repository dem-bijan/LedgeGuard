import  {cookies } from "next/headers"
import { mapUser } from "./maps"
import type {User} from "../types"
import {cache} from "react"

// cache() deduplicates calls within a single server-side request: if both
// layout.tsx and a page both call getCurrentUser(), this only actually
// fetches /me once, not twice. It does NOT dedupe against the separate
// client-side world -- that's handled differently, by passing the result
// down as a prop (see layout.tsx + StoreProvider).
export const getCurrentUser= cache(async (): Promise<User|null> =>{
    const cookieStore = await cookies()
    const token = cookieStore.get("access_token")?.value

    // Plain fetch, not the axios instance in lib/api.ts: this runs
    // server-to-server (Next's server calling the FastAPI backend), so
    // there's no browser cookie jar for withCredentials to use -- the
    // cookie has to be attached to the request by hand.
    const data  = await fetch(process.env.NEXT_PUBLIC_API_URL+"/me" , {
        headers:{Cookie: `access_token=${token}`},
    })

    if (!data.ok){
        return null
    }
    const user  = await data.json()
    return mapUser(user)
})
