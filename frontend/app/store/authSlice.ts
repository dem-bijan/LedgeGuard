import {createSlice , PayloadAction} from "@reduxjs/toolkit"
import type {User} from "../types"



interface AuthState{
    user : User| null;
}

const initialState:AuthState ={user: null }

const authSlice = createSlice({
    name:"auth",
    initialState,
    reducers:{
        setCredentials(state , aciton: PayloadAction<{user:User}>){
            state.user = aciton.payload.user
        },
        logout(state){

            state.user = null
        },
    }
})



export const {setCredentials , logout}= authSlice.actions


export default authSlice.reducer
