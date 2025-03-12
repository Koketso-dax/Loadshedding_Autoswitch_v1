import { useRouter } from "next/router";
import React from "react";
import DeviceDataDisplay from "@/components/DeviceDataDisplay";

export default function DeviceDataPage() {
  const router = useRouter();
  const { id } = router.query;

  if (!id || typeof id !== "string") {
    return <div>Invalid device ID</div>;
  }

  return (
    <div>
      <h1>Device Data</h1>
      <DeviceDataDisplay deviceId={parseInt(id, 10)} />
    </div>
  );
}
