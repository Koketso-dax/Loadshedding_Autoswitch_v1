import axios from "axios";

const API_URL = "https://localhost:5000";

export interface User {
  id: string;
  username: string;
  token: string;
}

export async function login(username: string, password: string): Promise<User> {
  const response = await axios.post(`${API_URL}/login`, { username, password });
  return response.data;
}

export async function register(
  username: string,
  password: string,
): Promise<User> {
  const response = await axios.post(`${API_URL}/register`, {
    username,
    password,
  });
  return response.data;
}

export function logout(): void {
  localStorage.removeItem("user");
}

export function getCurrentUser(): User | null {
  const userStr = localStorage.getItem("user");
  if (userStr) {
    return JSON.parse(userStr);
  }
  return null;
}

export function setCurrentUser(user: User): void {
  localStorage.setItem("user", JSON.stringify(user));
}
