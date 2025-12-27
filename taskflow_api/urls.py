from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from tasks.views import TaskViewSet, TaskCategoryViewSet
from users.views import UserRegistrationView, UserProfileView

# Root view with HTML
def api_root(request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TaskFlow API</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 800px;
                width: 100%;
                padding: 40px;
            }
            h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-align: center;
            }
            .subtitle {
                color: #666;
                text-align: center;
                margin-bottom: 40px;
                font-size: 1.1em;
            }
            .status {
                background: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 50px;
                display: inline-block;
                margin-bottom: 30px;
                font-weight: 600;
            }
            .section {
                margin-bottom: 30px;
            }
            .section h2 {
                color: #333;
                font-size: 1.3em;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }
            .endpoint {
                background: #f8f9fa;
                padding: 12px 20px;
                margin: 8px 0;
                border-radius: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: transform 0.2s;
            }
            .endpoint:hover {
                transform: translateX(5px);
                background: #e9ecef;
            }
            .endpoint-name {
                font-weight: 600;
                color: #333;
            }
            .endpoint-path {
                color: #667eea;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }
            .method {
                background: #667eea;
                color: white;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 0.75em;
                font-weight: 600;
                margin-left: 10px;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e9ecef;
                color: #666;
            }
            a {
                color: #667eea;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 TaskFlow API</h1>
            <p class="subtitle">Your Task Management Backend</p>
            <div style="text-align: center;">
                <span class="status">✓ Server Running</span>
            </div>

            <div class="section">
                <h2>📋 Task Endpoints</h2>
                <div class="endpoint">
                    <span class="endpoint-name">All Tasks</span>
                    <div>
                        <span class="endpoint-path">/api/tasks/</span>
                        <span class="method">GET/POST</span>
                    </div>
                </div>
                <div class="endpoint">
                    <span class="endpoint-name">Today's Tasks</span>
                    <div>
                        <span class="endpoint-path">/api/tasks/today/</span>
                        <span class="method">GET</span>
                    </div>
                </div>
                <div class="endpoint">
                    <span class="endpoint-name">Upcoming Tasks</span>
                    <div>
                        <span class="endpoint-path">/api/tasks/upcoming/</span>
                        <span class="method">GET</span>
                    </div>
                </div>
                <div class="endpoint">
                    <span class="endpoint-name">Statistics</span>
                    <div>
                        <span class="endpoint-path">/api/tasks/statistics/</span>
                        <span class="method">GET</span>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📁 Category Endpoints</h2>
                <div class="endpoint">
                    <span class="endpoint-name">All Categories</span>
                    <div>
                        <span class="endpoint-path">/api/categories/</span>
                        <span class="method">GET/POST</span>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🔐 Authentication</h2>
                <div class="endpoint">
                    <span class="endpoint-name">Register</span>
                    <div>
                        <span class="endpoint-path">/api/auth/register/</span>
                        <span class="method">POST</span>
                    </div>
                </div>
                <div class="endpoint">
                    <span class="endpoint-name">Login</span>
                    <div>
                        <span class="endpoint-path">/api/auth/login/</span>
                        <span class="method">POST</span>
                    </div>
                </div>
                <div class="endpoint">
                    <span class="endpoint-name">User Profile</span>
                    <div>
                        <span class="endpoint-path">/api/auth/profile/</span>
                        <span class="method">GET</span>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>⚙️ Admin Panel</h2>
                <div class="endpoint">
                    <span class="endpoint-name">Django Admin</span>
                    <div>
                        <span class="endpoint-path"><a href="/admin/" target="_blank">/admin/</a></span>
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>Built with Django REST Framework</p>
                <p style="margin-top: 10px;">
                    <a href="/api/" target="_blank">View API Root</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', TaskCategoryViewSet, basename='category')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/', include(router.urls)),
    
    # Authentication
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', UserProfileView.as_view(), name='user_profile'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)