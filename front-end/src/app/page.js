'use client'
import React, { useState, useEffect } from "react";
import LPPLSChart from "@/components/lppls-chart";

const App = () => {
  const [rawData, setRawData] = useState(null);

  useEffect(() => {
    // Simulated API data (replace with real API fetch)
    const fetchData = async () => {
      const data = {
        "0": { date: "2023-09-01", logPrice: 3.5, lpplsFit: 3.8 },
        "1": { date: "2023-10-01", logPrice: 4.0, lpplsFit: 3.9 },
        "2": { date: "2023-11-01", logPrice: 4.5, lpplsFit: 4.2 },
        "3": { date: "2024-03-01", logPrice: 5.8, lpplsFit: 5.7 },
        "4": { date: "2024-07-01", logPrice: 6.2, lpplsFit: 6.1 },
        "5": { date: "2024-11-01", logPrice: 6.5, lpplsFit: 6.3 },
        "t1": "2023-09-01",
        "t2": "2024-11-01",
        "tc": "2024-11-10"
      };
      setRawData(data);
    };

    fetchData();
  }, []);

  return <div><h2>LPPLS Chart</h2>{rawData && <LPPLSChart rawData={rawData} />}</div>;
};

export default App;
