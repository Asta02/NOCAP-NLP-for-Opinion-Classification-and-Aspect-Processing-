'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion } from 'framer-motion';
import { Loader2, Eye, EyeOff, Building2, ShieldCheck } from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login, isAuthenticated, user } = useAuth();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
      rememberMe: false,
    },
  });

  React.useEffect(() => {
    if (isAuthenticated && user) {
      if (user.role === 'admin') {
        router.replace('/admin/dashboard');
      } else {
        router.replace('/dashboard');
      }
    }
  }, [isAuthenticated, user, router]);

  const onSubmit = async (data: LoginFormData) => {
    setIsSubmitting(true);
    try {
      await login(data.username, data.password, data.rememberMe || false);
      toast.success('Login successful');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Invalid credentials');
    } finally {
      setIsSubmitting(false);
    }
  };

  const rememberMe = watch('rememberMe');

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-700 via-primary-800 to-darkblue-900 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-20 left-20 w-72 h-72 bg-white/5 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
        </div>
        <div className="relative z-10 flex flex-col justify-center px-16 xl:px-24 text-white">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="w-14 h-14 bg-white/10 rounded-2xl flex items-center justify-center mb-8 backdrop-blur-sm">
              <ShieldCheck className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-4xl xl:text-5xl font-bold leading-tight mb-6">
              AI Employee<br />Feedback Analysis
            </h1>
            <p className="text-lg text-primary-100 leading-relaxed max-w-md">
              Transform employee feedback into actionable insights. Our AI-powered decision support system helps you build a better workplace.
            </p>
            <div className="mt-10 flex items-center gap-8">
              <div className="text-center">
                <p className="text-3xl font-bold">1000+</p>
                <p className="text-sm text-primary-200">Reviews Analyzed</p>
              </div>
              <div className="w-px h-12 bg-white/20" />
              <div className="text-center">
                <p className="text-3xl font-bold">25+</p>
                <p className="text-sm text-primary-200">Companies</p>
              </div>
              <div className="w-px h-12 bg-white/20" />
              <div className="text-center">
                <p className="text-3xl font-bold">AI</p>
                <p className="text-sm text-primary-200">Powered</p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-gradient-to-br from-neutral-50 via-white to-primary-50/30 px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex w-14 h-14 bg-gradient-to-br from-primary to-primary-700 rounded-2xl items-center justify-center mb-4 shadow-lg">
              <ShieldCheck className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-neutral-900">AI Feedback Analysis</h1>
          </div>

          <div className="bg-white rounded-2xl shadow-xl border border-neutral-100 p-8">
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-neutral-900">Welcome back</h2>
              <p className="text-sm text-neutral-500 mt-1">Sign in to access your dashboard</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="username" className="text-sm font-medium text-neutral-700">
                  Username
                </Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  className="h-12 rounded-xl border-neutral-200 focus:border-primary focus:ring-primary/20"
                  {...register('username')}
                />
                {errors.username && (
                  <p className="text-xs text-error">{errors.username.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-neutral-700">
                  Password
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    className="h-12 rounded-xl border-neutral-200 focus:border-primary focus:ring-primary/20 pr-10"
                    {...register('password')}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-xs text-error">{errors.password.message}</p>
                )}
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="rememberMe"
                    checked={rememberMe}
                    onCheckedChange={(checked) => setValue('rememberMe', checked as boolean)}
                  />
                  <Label
                    htmlFor="rememberMe"
                    className="text-sm text-neutral-600 cursor-pointer"
                  >
                    Remember me
                  </Label>
                </div>
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full h-12 bg-primary hover:bg-primary-700 text-white rounded-xl font-medium transition-all shadow-lg shadow-primary/25"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            <div className="mt-8 pt-6 border-t border-neutral-100">
              <p className="text-xs text-center text-neutral-400 mb-4">Quick access with demo credentials</p>
              <div className="grid grid-cols-2 gap-3">
                <div
                  className="bg-gradient-to-br from-primary-50 to-primary-100/50 rounded-xl p-4 cursor-pointer hover:shadow-md transition-shadow border border-primary-100"
                  onClick={() => { setValue('username', 'admin'); setValue('password', 'admin123'); }}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
                      <ShieldCheck className="w-4 h-4 text-primary" />
                    </div>
                    <p className="font-semibold text-neutral-800 text-sm">Admin</p>
                  </div>
                  <p className="text-xs text-neutral-500 font-mono">admin / admin123</p>
                </div>
                <div
                  className="bg-gradient-to-br from-success-50 to-success-100/50 rounded-xl p-4 cursor-pointer hover:shadow-md transition-shadow border border-success-100"
                  onClick={() => { setValue('username', 'google'); setValue('password', 'company123'); }}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-7 h-7 rounded-lg bg-success/10 flex items-center justify-center">
                      <Building2 className="w-4 h-4 text-success" />
                    </div>
                    <p className="font-semibold text-neutral-800 text-sm">Company</p>
                  </div>
                  <p className="text-xs text-neutral-500 font-mono">google / company123</p>
                </div>
              </div>
            </div>
          </div>

          <p className="text-center text-xs text-neutral-400 mt-6">
            Powered by AI & Natural Language Processing
          </p>
        </motion.div>
      </div>
    </div>
  );
}
