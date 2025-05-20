// app/login/page.tsx
import Link from 'next/link'
import { LoginForm } from '@/components/login-form'
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Github, Mail, Linkedin } from 'lucide-react'

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-xl border-0">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center">Welcome Back</CardTitle>
            <CardDescription className="text-center">
              Choose your preferred login method
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <Button 
                  variant="outline" 
                  className="w-full hover:bg-gray-100 transition-colors"
                >
                  <Mail className="h-5 w-5 text-gray-600" />
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full hover:bg-gray-100 transition-colors"
                >
                  <Github className="h-5 w-5 text-gray-800" />
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full hover:bg-gray-100 transition-colors"
                >
                  <Linkedin className="h-5 w-5 text-blue-600" />
                </Button>
              </div>
              
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-4 text-gray-500 font-medium">
                    or continue with email
                  </span>
                </div>
              </div>

              <LoginForm />
              
              <div className="flex flex-col space-y-3 text-sm text-center">
                <Link 
                  href="/forgot-password"
                  className="text-blue-600 hover:text-blue-800 transition-colors hover:underline"
                >
                  Forgot your password?
                </Link>
                <div className="text-gray-600">
                  New here?{' '}
                  <Link 
                    href="/signup"
                    className="text-blue-600 font-medium hover:text-blue-800 transition-colors hover:underline"
                  >
                    Create an account
                  </Link>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}