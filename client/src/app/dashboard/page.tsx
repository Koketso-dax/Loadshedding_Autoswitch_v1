'use client';

import ViewDevices from './ViewDevices';
import CreateDevice from './CreateDevice';
import { redirect } from "next/navigation";
import React from 'react';

export default function Dashboard() {
  const access_token = localStorage.getItem('token')
  
  if(!access_token) redirect('/login');

  return (
    <div className="max-w-md mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

      {access_token && <CreateDevice accessToken={access_token} />}

      {access_token && <ViewDevices accessToken={access_token} />}
    </div>
  );
}
