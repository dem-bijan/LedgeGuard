
import { getCurrentUser } from "./lib/getCurrentUser"
import { redirect } from "next/navigation"
import DashboardContent from "./components/DashboardContent"

// Deliberately a Server Component, not a Client Component checking Redux.
// A client-side check has an unavoidable gap: Redux starts empty, so for
// a moment even a logged-in user would look logged-out, causing a flash
// of a redirect before the real state arrives. Checking server-side means
// the page that reaches the browser is already correct -- there's nothing
// to flash.
export default async function Dashboard(){
    const user = await getCurrentUser()

    if(!user){
        redirect("/login")
    }


    return <DashboardContent user={user} />




}
