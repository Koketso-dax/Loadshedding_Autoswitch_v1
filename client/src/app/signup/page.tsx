'use client'

import React,{ useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useRouter } from 'next/navigation'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { useToast } from "@/hooks/use-toast"

const signUpSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/, 
      'Password must contain at least one uppercase letter, one lowercase letter, one number and one special character'),
})

type SignUpValues = z.infer<typeof signUpSchema>

export default function SignUpPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const form = useForm<SignUpValues>({
    resolver: zodResolver(signUpSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  })

  async function onSubmit(data: SignUpValues) {
    setIsLoading(true)
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Registration failed')
      }

      toast({
        title: "Registration Successful",
        description: "You can now log in with your new account.",
      })
      router.push('/login')
    } catch (error) {
      console.error(error);
      toast({
        title: "Registration Failed",
        description: `There was a problem registering your account.`,
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto max-w-md py-12">
      <h1 className="text-2xl font-bold mb-6">Sign Up</h1>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Username</FormLabel>
                <FormControl>
                  <Input placeholder="Enter your username" {...field} />
                </FormControl>
                <FormDescription>
                  This will be your public display name.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input type="password" placeholder="Enter your password" {...field} />
                </FormControl>
                <FormDescription>
                  Must be at least 8 characters with 1 uppercase, 1 lowercase, 1 number, and 1 special character.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Signing up...' : 'Sign Up'}
          </Button>
        </form>
      </Form>
    </div>
  )
}