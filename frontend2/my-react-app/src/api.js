// Replace these with your own deployment endpoints (or use environment variables).
export const EC2_URL    = import.meta.env.VITE_EC2_URL    || "http://localhost:8000";
export const LAMBDA_URL = import.meta.env.VITE_LAMBDA_URL || "http://localhost:8000";
export const ECS_URL    = import.meta.env.VITE_ECS_URL    || "http://localhost:8000";

