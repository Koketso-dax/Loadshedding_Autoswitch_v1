'use client';

import { useState, useEffect } from 'react';
import axios, { AxiosError } from 'axios';
import { useRouter } from 'next/navigation';
import { v4 as uuidv4 } from 'uuid';

interface Device {
  id: number;
  device_key: string;
  password: string;
  // Add any other device properties here
}

export default function Dashboard() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [newDeviceKey, setNewDeviceKey] = useState(uuidv4());
  const [newDevicePassword, setNewDevicePassword] = useState('');
  const router = useRouter();

  useEffect(() => {

    const fetchDevices = async () => {
      try {
        const response = await axios.get('/api/devices');
        setDevices(response.data);
      } catch (error) {
        const axiosError = error as AxiosError;
        if (axiosError.response?.status === 401) {
          router.push('/login');
        }
      }
    };
    fetchDevices();
  }, []);

  const handleCreateDevice = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    try {
      const response = await axios.post('/api/devices', {
        device_key: newDeviceKey,
        password: newDevicePassword,
      });

      setDevices([...devices, response.data]);
      setNewDevicePassword('');
      setNewDeviceKey(uuidv4());
    } catch (error) {
      const axiosError = error as AxiosError;
      // Handle error
    }
  };

  return (
    <div className="max-w-md mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

      <form onSubmit={handleCreateDevice} className="mb-4">
        <input
          type="text"
          value={newDeviceKey}
          onChange={(event) => setNewDeviceKey(event.target.value)}
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          placeholder="New device key"
        />
        <input
          type="password"
          value={newDevicePassword}
          onChange={(event) => setNewDevicePassword(event.target.value)}
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline mt-2"
          placeholder="New device password"
        />
        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ml-2"
        >
          Create
        </button>
      </form>

      <ul>
        {devices.map((device) => (
          <li key={device.id} className="mb-2">
            {device.device_key}
          </li>
        ))}
      </ul>
    </div>
  );
}


