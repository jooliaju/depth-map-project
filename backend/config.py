import os

class Config:
    # Development settings
    DEV_FRONTEND_URL = "http://localhost:3000"
    DEV_BACKEND_URL = "http://127.0.0.1:5000"
    
    # Production settings
    PROD_FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://depth-map-project.vercel.app/')
    PROD_BACKEND_URL = os.getenv('BACKEND_URL', 'https://depth-map-api.onrender.com')
    
    # Environment
    ENV = os.getenv(key = 'FLASK_ENV', default = 'development')
    
    @property
    def FRONTEND_URL(self):
        return self.DEV_FRONTEND_URL if self.ENV == 'development' else self.PROD_FRONTEND_URL
    
    @property
    def BACKEND_URL(self):
        return self.DEV_BACKEND_URL if self.ENV == 'development' else self.PROD_BACKEND_URL 