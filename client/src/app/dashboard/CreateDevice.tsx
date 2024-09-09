// CreateDevice.tsx
'use client';

import { useState } from 'react';
import axios, { AxiosError } from 'axios';

interface Device {
  id: number;
  device_key: string;
}

interface CreateDeviceProps {
  accessToken: string;
}

const CreateDevice: React.FC<CreateDeviceProps> = ({ accessToken }) => {
  const [newDevicePassword, setNewDevicePassword] = useState('');
  const [newDeviceKey, setNewDeviceKey] = useState('');

  const handleCreateDevice = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    try {
      const response = await axios.post('http://web-01.koketsodiale.tech/api/devices', {
        device_key: newDeviceKey,
        password: newDevicePassword,
      }, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      setNewDevicePassword('');
      setNewDeviceKey('');
    } catch (error) {
      const axiosError = error as AxiosError;
      // Handle error
    }
  };

  return (
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
  );
};

export default CreateDevice;
