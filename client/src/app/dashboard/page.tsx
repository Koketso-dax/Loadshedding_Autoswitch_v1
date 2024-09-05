'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface Device {
  id: number;
  device_key: string;
  // Add any other device properties here
}

export default function Dashboard() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [newDeviceKey, setNewDeviceKey] = useState('');
  const [newDevicePassword, setNewDevicePassword] = useState('');

  useEffect(() => {
    const fetchDevices = async () => {
      const response = await axios.get('/api/devices');
      setDevices(response.data);
    };

    fetchDevices();
  }, []);

  const handleCreateDevice = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const response = await axios.post('/api/devices', {
      device_key: newDeviceKey,
      password: newDevicePassword,
    });

    setDevices([...devices, response.data]);
    setNewDeviceKey('');
    setNewDevicePassword('');
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
