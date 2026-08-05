export interface LoginRequest {
  username: string;
  password: string;
}

export interface AdminLoginResponse {
  token: string;
  role: 'admin';
}

export interface CompanyLoginResponse {
  token: string;
  role: 'company';
  company: CompanyInfo;
}

export type LoginResponse = AdminLoginResponse | CompanyLoginResponse;

export interface CompanyInfo {
  company_id: number;
  company_name: string;
}

export interface User {
  role: 'admin' | 'company';
  company?: CompanyInfo;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface AuthContextType extends AuthState {
  login: (username: string, password: string, rememberMe: boolean) => Promise<void>;
  logout: () => void;
}
