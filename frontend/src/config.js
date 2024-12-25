const config = {
  development: {
    API_BASE_URL: "http://127.0.0.1:5000/api",
  },
  production: {
    API_BASE_URL:
      process.env.REACT_APP_API_URL || "https://api.yourdomain.com/api",
  },
};

const env = process.env.NODE_ENV || "development";
export default config[env];
