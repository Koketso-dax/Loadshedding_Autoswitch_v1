import { NextResponse } from "next/server";
import axios from "axios";

const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:5000";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { data, status } = await axios.post(
      `${API_BASE_URL}/auth/login`,
      body,
      {
        headers: { "Content-Type": "application/json" },
      },
    );
    return NextResponse.json(data, { status });
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return NextResponse.json(error.response.data);
    }
    return NextResponse.json(
      { message: "Internal server error" },
      { status: 500 },
    );
  }
}
