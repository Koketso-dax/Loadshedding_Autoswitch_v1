/**
 * Acts as a proxy to the Flask backend, handling
 * the authentication flow on the client side.
 */
import { NextApiRequest, NextApiResponse } from "next";
import axios from "axios";

const API_BASE_URL = process.env.API_Base_URL;

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  const { auth } = req.query;
  const endpoint = Array.isArray(auth) ? auth.join("/") : auth;

  try {
    const { data, status } = await axios({
      method: req.method,
      url: `${API_BASE_URL}/auth/${endpoint}`,
      data: req.body,
      headers: {
        "Content-Type": "application/json",
        ...(req.headers.authorization && {
          Authorization: req.headers.authorization,
        }),
      },
    });

    res.status(status).json(data);
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      res.status(error.response.status).json(error.response.data);
    }
  }
}
