import * as React from 'react'
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "@/components/ui/navigation-menu"
import { ModeToggle } from "./mode-toggle"
import { Button } from "./ui/button"
import Link from "next/link"
import { useRouter } from 'next/navigation'
import {cookies} from "next/headers";

/**
 * Navbar component for the application.
 * This component renders the navigation menu and the mode toggle button.
 * It also handles the logout functionality and checks the login status.
 */
export default function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = React.useState(false)
  const router = useRouter()

  /**
   * useEffect to check the login status and update the state accordingly.
   * It runs on component mount and sets an interval to check the login status periodically.
   */
  React.useEffect(() => {
    const checkLoginStatus = () => {
      const token = cookies().get('token')
      setIsLoggedIn(!!token)
    }

    checkLoginStatus()
    const intervalId = setInterval(checkLoginStatus, 500);

    return () => {
      clearInterval(intervalId);
    }
  }, [])

  /**
   * Function to handle the logout functionality.
   * It removes the token from local storage, sets the isLoggedIn state to false,
   * and navigates to the home page.
   */
  const handleLogout = () => {
    cookies().delete('token')
    setIsLoggedIn(false)
    router.push('/')
  }

  /**
   * Render the navigation menu and the mode toggle button.
   * The mode toggle button is rendered only if the user is logged in.
   */
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between">
        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem>
              <Link href="/" legacyBehavior passHref>
                <NavigationMenuLink className="group inline-flex h-9 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50 data-[active]:bg-accent/50 data-[state=open]:bg-accent/50">
                  Home
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <Link href="/dashboard" legacyBehavior passHref>
                <NavigationMenuLink className="group inline-flex h-9 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50 data-[active]:bg-accent/50 data-[state=open]:bg-accent/50">
                  Dashboard
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <Link href="/docs" legacyBehavior passHref>
                <NavigationMenuLink className="group inline-flex h-9 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50 data-[active]:bg-accent/50 data-[state=open]:bg-accent/50">
                  Docs
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <Link href="/about" legacyBehavior passHref>
                <NavigationMenuLink className="group inline-flex h-9 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50 data-[active]:bg-accent/50 data-[state=open]:bg-accent/50">
                  About
                </NavigationMenuLink>
              </Link>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
        <div className="flex items-center space-x-4">
          {isLoggedIn ? (
            <Button variant="ghost" onClick={handleLogout}>
              Logout
            </Button>
          ) : (
            <Button variant="ghost" asChild>
              <Link href="/login">Login</Link>
            </Button>
          )}
          {!isLoggedIn && (
            <Button asChild>
              <Link href="/signup">Sign Up</Link>
            </Button>
          )}
          <ModeToggle />
        </div>
      </div>
    </header>
  )
}