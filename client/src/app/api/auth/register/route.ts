import { NextResponse } from 'next/server';
import axios, {AxiosError} from 'axios';

export async function POST(request: Request) {
  const { username, password } = await request.json();

  try {
    const response = await axios.post('https://web-01.koketsodiale.tech/api/auth/register', {
      username,
      password,
    });

    return NextResponse.json(response.data, { status: response.status });
  } catch (error) {
    const axiosError = error as AxiosError;
    const errorData = axiosError.response?.data as {message: string}
    return NextResponse.json({ message: errorData.message}, { status: axiosError.response?.status});
  }
}
