"use client";

import React from "react";

/**
 * @returns Styled landing text for Home
 */
export default function LandingText() {
  return (
    <div>
      <h1 className="scroll-m-20 text-4xl font-extrabold tracking-tight lg:text-5xl">
        Loadshedding Autoswitch.
      </h1>
      <p className="leading-7 [&:not(:first-child)]:mt-6">
        Protect your devices from rolling blackouts and sudden power failures.
        Monitor your power. Take back the control.
      </p>
    </div>
  );
}
