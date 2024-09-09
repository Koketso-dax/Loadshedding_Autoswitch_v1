import { NextResponse } from 'next/server';
import axios from 'axios';
import { cookies } from 'next/headers';

export async function GET() {
  try {
    const token = cookies().get('token')?.value;
    const response = await axios.get('http://web-01.koketsodiale.tech/api/devices', {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": `application/json`,
      },
    });
    return NextResponse.json(response.data);
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to retrieve devices' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
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
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: 'Failed to add device' }, { status: 500 });
  }
}
