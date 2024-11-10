import { useState } from 'react'
import axios from 'axios'

interface Device {
  id: number
  device_key: string
  // Add other device properties as needed
}

export function useDevices() {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const addDevice = async (device_key: string, password: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.post<{ message: string, device_id: number }>('/api/devices', { device_key, password }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      // Refresh the devices list after adding a new device
      await getDevices()
      return response.data
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred while adding the device'
      setError(errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const getDevices = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get<Device[]>('/api/devices', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      setDevices(response.data)
      return response.data
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred while fetching devices'
      setError(errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const getDevice = async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get<Device>(`/api/devices/${id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      return response.data
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred while fetching the device'
      setError(errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const removeDevice = async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.delete<{ message: string }>(`/api/devices/${id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      // Refresh the devices list after removing a device
      await getDevices()
      return response.data
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred while removing the device'
      setError(errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }

  return { devices, loading, error, addDevice, getDevices, getDevice, removeDevice }
}
