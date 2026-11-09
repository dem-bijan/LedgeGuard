import type { Metadata } from "next";
import { Instrument_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import StoreProvider from "./store/StoreProvider";
import { getCurrentUser } from "./lib/getCurrentUser";

const instrumentSans = Instrument_Sans({
  variable: "--font-instrument-sans",
  subsets: ["latin"],
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "LedgerGuard",
  description: "A secure, auditable ledger for everyday banking.",
};

// Every route under this layout depends on getCurrentUser()'s per-request
// cookie read, so none of them can be statically prerendered -- tell
// cacheComponents that up front instead of letting it flag each one.
export const instant = false;

export default async function RootLayout({ children }: LayoutProps<"/">) {
  // Fetched once, here, server-side -- then handed down to StoreProvider
  // as a prop so it can seed Redux directly, instead of the client
  // re-fetching /me itself on mount. One real network call per visit,
  // not two.
  const user = await getCurrentUser()
  return (
    <html
      lang="en"
      className={`${instrumentSans.variable} ${plexMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col"><StoreProvider initialUser={user}>{children}</StoreProvider></body>
    </html>
  );
}
