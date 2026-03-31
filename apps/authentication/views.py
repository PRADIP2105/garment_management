import logging
import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer, CompanySerializer
from django.shortcuts import render
from django.utils.timezone import now
from apps.companies.models import Company

# Setup logging
logger = logging.getLogger(__name__)

# Store login attempts
login_attempts_list = []

def parse_request_data(request):
    """
    Parse request data from both JSON and form-urlencoded formats.
    This ensures mobile apps sending JSON can login successfully.
    """
    data = {}
    
    # Log the raw request for debugging
    logger.info(f"Login attempt - Content-Type: {request.content_type}")
    logger.info(f"Login attempt - Raw body: {request.body}")
    
    # Try to parse JSON data first
    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body) if request.body else {}
            logger.info(f"Parsed JSON data: {data}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            data = {}
    
    # Fall back to request.data (handles both JSON and form data)
    if not data:
        data = dict(request.data)
        logger.info(f"Parsed request.data: {data}")
    
    return data


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login(request):
    """
    Login user - handles both JSON and form-urlencoded data.
    Mobile apps typically send JSON, so we handle that explicitly.
    """
    # Parse data from request (handles both JSON and form data)
    data = parse_request_data(request)
    
    # Debug: Log what we're trying to authenticate with
    username = data.get('username') or data.get('username')
    password = data.get('password')
    logger.info(f"Login attempt for username: {username}")
    
    if not username or not password:
        logger.warning("Login failed: Missing username or password")
        return Response(
            {'error': 'Invalid credentials', 'detail': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate user using Django's authenticate function
    # This uses the AUTHENTICATION_BACKENDS defined in settings.py
    user = authenticate(username=username, password=password)
    
    logger.info(f"Login request received with username: {username} and password: {password}")
    logger.info(f"Authentication result for username {username}: {user}")
    
    if user is None:
        # Check if user exists to provide better error message
        user_exists = User.objects.filter(username=username).exists()
        if user_exists:
            logger.warning(f"Login failed: Wrong password for user: {username}")
            error_detail = "Invalid password"
        else:
            logger.warning(f"Login failed: User not found: {username}")
            error_detail = "Invalid username or password"
        
        return Response(
            {'error': 'Invalid credentials', 'detail': error_detail},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        logger.warning(f"Login failed: User inactive: {username}")
        return Response(
            {'error': 'Invalid credentials', 'detail': 'User account is disabled'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    # Get user data using UserSerializer
    user_serializer = UserSerializer(user)
    user_data = user_serializer.data
    
    # Add company info if user has a company
    if user.company:
        company_serializer = CompanySerializer(user.company)
        user_data['company'] = company_serializer.data
    else:
        user_data['company'] = None
    
    logger.info(f"Login successful for user: {username}")
    logger.info(f"Login endpoint called with data: {data}")
    
    return Response({
        'message': 'Login successful',
        'user': user_data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register new user and company"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        # Get user data using UserSerializer
        user_serializer = UserSerializer(user)
        user_data = user_serializer.data

        # Add company info if user has a company
        company_data = {
            "name": request.data.get("company_name"),
            "address": request.data.get("company_address"),
            "city": request.data.get("company_city"),
            "mobile": request.data.get("company_mobile")
        }
        if company_data["name"]:
            # Assuming a Company model exists and is related to the User model
            company = Company.objects.create(**company_data, owner=user)
            user.company = company
            user.save()
            user_data['company'] = CompanySerializer(company).data
        else:
            user_data['company'] = None

        return Response({
            "user": user_data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    """Logout user by blacklisting refresh token"""
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'})
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def login_debug_view(request):
    debug_info = None
    if request.method == 'POST':
        attempt = {
            'device': request.headers.get('User-Agent', 'Unknown Device'),
            'username': request.POST.get('username', 'N/A'),
            'password': request.POST.get('password', 'N/A'),
            'date_time': now().strftime('%Y-%m-%d %H:%M:%S'),
            'page': request.path
        }
        login_attempts_list.append(attempt)
        debug_info = attempt
        logger.info(f"Login debug view called with data: {attempt}")
    return render(request, 'login_debug.html', {'debug_info': debug_info})


def login_attempts_list_view(request):
    return render(request, 'login_attempts_list.html', {'login_attempts': login_attempts_list})


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def login_attempts(request):
    """
    Retrieve all login attempts.
    """
    global login_attempts_list
    logger.info("login_attempts view called")
    return Response(login_attempts_list, status=status.HTTP_200_OK)
