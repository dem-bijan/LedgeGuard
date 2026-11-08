import axios from "axios"

import { mapUser } from "./maps"

// withCredentials: true makes the browser send the httpOnly auth cookie
// on every request through this instance. No token is attached manually
// here on purpose -- the backend reads it straight from the cookie, and
// JS never has access to it at all (that's the whole point of httpOnly).
const api = axios.create({
    baseURL:process.env.NEXT_PUBLIC_API_URL,
    withCredentials: true
})

// Reshapes /me's response into the frontend's camelCase User shape, in
// one place, so every caller (StoreProvider, Login, ...) gets already-
// mapped data automatically instead of calling mapUser() themselves.
// Scoped to the /me URL specifically -- this instance also carries
// /login, /accounts, /transfer, etc, which have unrelated shapes.
api.interceptors.response.use((response)=>{
    if(response.config.url === "/me"){
        response.data = mapUser(response.data);
    }
    return response
})

export default api
