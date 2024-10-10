"use client";

import React from "react";
import ViewDevices from "./ViewDevices";
import CreateDevice from "./CreateDevice";

interface DashboardClientProps {
  accessToken: string;
}

export default function DashboardClient({ accessToken }: DashboardClientProps) {
  return (
    <div className="max-w-md mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <CreateDevice accessToken={accessToken} />
      <ViewDevices accessToken={accessToken} />
    </div>
  );
}
