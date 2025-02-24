import { useState } from "react";
import axios from "axios";

interface Metric {
  id: number;
  device_id: number;
  timestamp: string;
  value: number;
}

interface PaginatedResponse {
  items: Metric[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

/* eslint-disable */
export function useDeviceData() {
  const [data, setData] = useState<PaginatedResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getDeviceData = async (deviceId: number, page: number = 1, perPage: number = 10) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<PaginatedResponse>(
        `/api/data/${deviceId}?page=${page}&per_page=${perPage}`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
        }
      );
      setData(response.data);
      return response.data;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred while fetching device data";
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  }

  return { data, loading, error, getDeviceData }
}