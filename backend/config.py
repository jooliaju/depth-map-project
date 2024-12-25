import os

class Config:
    # Development settings
    DEV_FRONTEND_URL = "http://localhost:3000"
    DEV_BACKEND_URL = "http://127.0.0.1:5000"
    
    # Production settings
    PROD_FRONTEND_URL = os.getenv('FRONTEND_URL')
    PROD_BACKEND_URL = os.getenv('BACKEND_URL')
    
    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    
    @property
    def FRONTEND_URL(self):
        if self.ENV == 'development':
            return self.DEV_FRONTEND_URL
        return [
            self.PROD_FRONTEND_URL,
            'https://depth-map-project.vercel.app',
            'http://localhost:3000'
        ]
    
    @property
    def BACKEND_URL(self):
        return self.DEV_BACKEND_URL if self.ENV == 'development' else self.PROD_BACKEND_URL 