"use client";

import { useEffect, useState } from "react";



export default function HealthStatus() {
    const [status, setStatus] = useState(null);
    useEffect(() => {
        const fetchHealthStatus = async () => {
            try {
                const response = await fetch("http://localhost:8000/health");
                const data = await response.json();
                setStatus(data);
            } catch (error) {
                console.error("Error fetching health status:", error);
            }
        };

        fetchHealthStatus();
    }, []);

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-4xl font-bold mb-4">{JSON.stringify(status)}</h1>
        </div>
    );
}