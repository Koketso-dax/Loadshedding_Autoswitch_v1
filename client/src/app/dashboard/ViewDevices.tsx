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
    <div>
      {devices.map(device => (
        <div key={device.id}>{device.name}</div>
      ))}
    </div>
  );
};

export default ViewDevices;
