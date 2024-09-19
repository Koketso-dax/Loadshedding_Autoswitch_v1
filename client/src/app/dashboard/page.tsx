import React from 'react'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import DashboardClient from './DashboardClient'

export default function Dashboard() {
  const cookieStore = cookies()
  const access_token = cookieStore.get('access_token')?.value

  if (!access_token) {
    redirect('/login')
  }

  return <DashboardClient accessToken={access_token} />
}