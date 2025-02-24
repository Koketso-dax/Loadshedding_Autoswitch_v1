import React, { useEffect, useState } from "react";
import { useDeviceData } from "../hooks/use-device-data";

interface DeviceDataDisplayProps {
  deviceId: number;
}

export default function DeviceDataDisplay({ deviceId }: DeviceDataDisplayProps) {
  const { data, loading, error, getDeviceData } = useDeviceData();
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  useEffect(() => {
    getDeviceData(deviceId, page, perPage);
  }, [deviceId, page, perPage])

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  }

  const handlePerPageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setPerPage(Number(event.target.value));
    setPage(1); // Reset to first page when changing items per page
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!data) return <div>No data available</div>

  return (
    <div>
      <h2>Device Data (ID: {deviceId})</h2>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map((metric) => (
            <tr key={metric.id}>
              <td>{new Date(metric.timestamp).toLocaleString()}</td>
              <td>{metric.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div>
        <button 
          onClick={() => handlePageChange(page - 1)} 
          disabled={page === 1}
        >
          Previous
        </button>
        <span>Page {page} of {data.pages}</span>
        <button 
          onClick={() => handlePageChange(page + 1)} 
          disabled={page === data.pages}
        >
          Next
        </button>
        <select value={perPage} onChange={handlePerPageChange}>
          <option value="10">10 per page</option>
          <option value="20">20 per page</option>
          <option value="50">50 per page</option>
        </select>
      </div>
    </div>
  )
}