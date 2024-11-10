import { NextResponse } from 'next/server'
import axios from 'axios'

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000'

export async function GET(
  request: Request,
  { params }: { params: { deviceId: string } }
) {
  try {
    const authorization = request.headers.get('Authorization')
    if (!authorization) {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const page = searchParams.get('page') || '1'
    const per_page = searchParams.get('per_page') || '10'

    const { data, status } = await axios.get(
      `${API_BASE_URL}/data/${params.deviceId}?page=${page}&per_page=${per_page}`,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': authorization
        },
      }
    )
    return NextResponse.json(data, { status })
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return NextResponse.json(error.response.data, { status: error.response.status })
    }
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 })
  }
}
