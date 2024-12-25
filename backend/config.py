import os

class Config:
    # Development settings
    DEV_FRONTEND_URL = "http://localhost:3000"
    DEV_BACKEND_URL = "http://127.0.0.1:5000"
    
    # Production settings
    PROD_FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://your-vercel-app.vercel.app')
    PROD_BACKEND_URL = os.getenv('BACKEND_URL', 'https://your-backend-url.com')
    
    # Environment
    ENV = os.getenv('FLASK_ENV', 'development')
    
    @property
    def FRONTEND_URL(self):
        if self.ENV == 'development':
            return self.DEV_FRONTEND_URL
        # In production, allow both the Vercel domain and your custom domain
        return [
            self.PROD_FRONTEND_URL,
            'https://your-vercel-app.vercel.app',
            'https://yourdomain.com'
        ]
    
    @property
    def BACKEND_URL(self):
        return self.DEV_BACKEND_URL if self.ENV == 'development' else self.PROD_BACKEND_URL 