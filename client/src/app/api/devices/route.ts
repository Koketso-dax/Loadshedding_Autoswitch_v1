import { NextResponse } from 'next/server';
import axios from 'axios';
import {cookies} from 'next/headers';

export async function GET() {
  const token = cookies().get('token')?.value;
  const response = await axios.get('http://web-01.koketsodiale.tech/api/devices', {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": `application/json`,
    },
  });
  return NextResponse.json(response.data);
}

export async function POST(request: Request) {
  const { device_key, password } = await request.json();
  const token = cookies().get('token')?.value;
  const response = await axios.post(
    'http://web-01.koketsodiale.tech/api/devices',
    { device_key, password },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": `application/json`,
      },
    }
  );
  return NextResponse.json(response.data);
}
