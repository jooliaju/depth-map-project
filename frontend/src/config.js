const isDevelopment = process.env.NODE_ENV === "development";

const config = {
  API_BASE_URL: isDevelopment
    ? "http://127.0.0.1:5000/api"
    : "https://depth-map-api-production.up.railway.app",
};

export default config;
