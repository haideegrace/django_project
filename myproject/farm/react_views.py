"""
React Frontend Serving View
Serves the React single-page application for all non-API routes
"""

from django.http import FileResponse
from django.views import View
from django.conf import settings
from pathlib import Path
import os


class ReactAppView(View):
    """
    Serves the React app's index.html for all non-API routes.
    This enables React Router to handle all client-side routing.
    """

    def get(self, request, *args, **kwargs):
        """
        Serve index.html from the built React app.
        """
        # Try to get index.html from static files (production)
        index_path = Path(settings.STATIC_ROOT) / "index.html"
        
        # Fallback to frontend build directory (development)
        if not index_path.exists():
            index_path = Path(settings.BASE_DIR.parent) / "frontend" / "build" / "index.html"
        
        # If still not found, return 404
        if not index_path.exists():
            from django.http import HttpResponse
            return HttpResponse(
                "<h1>React App Not Built</h1><p>Run 'npm run build' in frontend directory</p>",
                status=404,
                content_type="text/html"
            )
        
        # Serve the index.html file
        try:
            return FileResponse(
                open(index_path, 'rb'),
                content_type='text/html'
            )
        except Exception as e:
            from django.http import HttpResponse
            return HttpResponse(
                f"<h1>Error serving React app</h1><p>{str(e)}</p>",
                status=500,
                content_type="text/html"
            )
