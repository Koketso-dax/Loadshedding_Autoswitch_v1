import { NextResponse } from 'next/server';
import axios from 'axios';

export async function GET() {
  const response = await axios.get('http://web-01.koketsodiale.tech/api/devices', {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
  });
  return NextResponse.json(response.data);
}

export async function POST(request: Request) {
  const { device_key, password } = await request.json();
  const response = await axios.post(
    'http://web-01.koketsodiale.tech/api/devices',
    { device_key, password },
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    }
  );
  return NextResponse.json(response.data);
}
