"use client"

import {Provider, useDispatch} from "react-redux"
import type { User } from "../types"
import {store} from "./store"
import { useEffect } from "react"
import { setCredentials } from "./authSlice"



function StoreProvider({children , initialUser}:{children: React.ReactNode , initialUser:User | null}){
    return(<Provider store={store}>
        <RehydrateAuth initialUser={initialUser}>{children}</RehydrateAuth>
        </Provider>)
}

// Seeds Redux from the user the server already fetched (via layout.tsx),
// rather than calling /me again client-side. If initialUser is null, we
// deliberately don't retry here -- the server just checked this exact
// cookie moments ago, so a client-side retry would almost certainly get
// the same answer. Nothing to dispatch just means "not logged in", which
// is already the slice's default state.
function RehydrateAuth({children , initialUser}:{children : React.ReactNode , initialUser:User|null}){
    const dispatch = useDispatch()
    useEffect(()=>{
        if(initialUser){
            dispatch(setCredentials({user: initialUser}))
        }
    },[])

    return <>{children}</>
}

export default StoreProvider
