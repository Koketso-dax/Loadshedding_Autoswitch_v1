import ViewDevices from './ViewDevices';
import CreateDevice from './CreateDevice';
import { cookies } from 'next/headers';

export default function Dashboard() {
  const access_token = cookies().get('access_token')?.value;

  return (
    <div className="max-w-md mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

      {access_token && <CreateDevice accessToken={access_token} />}

      {access_token && <ViewDevices accessToken={access_token} />}
    </div>
  );
}
