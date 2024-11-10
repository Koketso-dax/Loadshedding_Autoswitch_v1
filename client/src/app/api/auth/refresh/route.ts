import { NextResponse } from 'next/server'
import axios from 'axios'

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000'

export async function POST(request: Request) {
  try {
    const authorization = request.headers.get('Authorization')
    if (!authorization) {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 })
    }

    const { data, status } = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': authorization
      },
    })
    return NextResponse.json(data, { status })
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      return NextResponse.json(error.response.data, { status: error.response.status })
    }
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 })
  }
}
