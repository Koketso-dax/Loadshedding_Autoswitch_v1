import { NextResponse } from 'next/server';
import axios, { AxiosError } from 'axios';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
  const { username, password } = await request.json();

  try {
    const response = await axios.post('http://web-01.koketsodiale.tech/api/auth/login', {
      username,
      password,
    });

    // Set the access token as a cookie
    cookies().set('access_token', response.data.access_token);

    return NextResponse.json(response.data, { status: response.status });
  } catch (error) {
    const axiosError = error as AxiosError;
    const errorData = axiosError.response?.data as { message: string };
    return NextResponse.json({ message: errorData.message }, { status: axiosError.response?.status });
  }
}
