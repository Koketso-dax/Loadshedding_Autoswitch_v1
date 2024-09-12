// ViewDevices.tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

interface Device {
  id: number;
  device_key: string;
  name: string;
}

interface ViewDevicesProps {
  accessToken: string;
}

const ViewDevices: React.FC<ViewDevicesProps> = ({ accessToken }) => {
  const [devices, setDevices] = useState<Device[]>([]);

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        // Make the GET request to retrieve all devices for the user
        const response = await axios.get('http://web-01.koketsodiale.tech/api/devices', {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });

        // Set the devices state with the response data
        setDevices(response.data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchDevices();
  }, [accessToken]);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {devices.map(device => (
        <div key={device.id} className="bg-white shadow-md rounded-lg p-4">
          <h2 className="text-lg font-bold mb-2">{device.name}</h2>
          <p className="text-gray-700 mb-2">Device Key: {device.device_key}</p>
          {/*<p className="text-gray-700">Measurements: {device.measurements.join(', ')}</p>*/}
        </div>
      ))}
    </div>
  );
};

export default ViewDevices;
