import { useState } from "react";
import axios from "axios";

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthResponse {
  message: string;
  data?: {
    user: User;
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  };
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const register = async (
    username: string,
    email: string,
    password: string,
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post<AuthResponse>("/api/auth/register", {
        username,
        email,
        password,
      });
      setUser(response.data.data?.user ?? null);
      if (response.data.data?.access_token) {
        localStorage.setItem("access_token", response.data.data.access_token);
      }
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "An unknown error occurred during registration";
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const login = async (identifier: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post<AuthResponse>("/api/auth/login", {
        username: identifier,
        password,
      });
      setUser(response.data.data?.user ?? null);
      if (response.data.data?.access_token) {
        localStorage.setItem("access_token", response.data.data.access_token);
      }
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "An unknown error occurred during login";
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(
        "/api/auth/logout",
        {},
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        },
      );
      setUser(null);
      localStorage.removeItem("access_token");
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "An error occurred during logout";
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get<AuthResponse>("/api/auth/me", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      setUser(response.data.data?.user ?? null);
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "An unknown error occurred while fetching the profile";
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const refreshToken = async () => {
    try {
      const response = await axios.post<AuthResponse>(
        "/api/auth/refresh",
        {},
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        },
      );
      if (response.data.data?.access_token) {
        localStorage.setItem("access_token", response.data.data.access_token);
      }
      return response.data;
    } catch (error: unknown) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "An unknown error occurred while refreshing the token";
      setError(errorMessage);
      throw error;
    }
  };

  return {
    user,
    loading,
    error,
    register,
    login,
    logout,
    getProfile,
    refreshToken,
  };
}
