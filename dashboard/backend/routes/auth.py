from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# --- OAuth Routes ---
@router.get("/login")
async def login(request: Request):
    """Initiates the Google OAuth login flow."""
    print(f"Login attempt initiated: {request.client.host}")
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth(request: Request):
    """Handles the OAuth callback and user session creation."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
         raise HTTPException(status_code=400, detail=str(e))
         
    user_info = token.get('userinfo')
    if not user_info:
        user_info = await oauth.google.userinfo(token=token)

    # Create simple session directly from OAuth user info
    request.session['user'] = {
        'email': user_info['email'],
        'name': user_info.get('name'),
        'picture': user_info.get('picture'),
        'provider': 'google',
        'provider_id': user_info.get('sub')
    }
    
    # Redirect to frontend
    return RedirectResponse(url=settings.FRONTEND_URL + "/dashboard")


@router.get("/logout")
async def logout(request: Request):
    """Clears the user session."""
    request.session.pop('user', None)
    return {"message": "Logged out"}

@router.get("/me")
async def get_current_user(request: Request):
    """Returns the current authenticated user's profile."""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
