from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer
from apps.companies.serializers import UserProfileSerializer
from apps.companies.models import UserProfile


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register new user and company"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Get user profile
        profile = UserProfile.objects.select_related('company', 'user').get(user=user)
        profile_data = UserProfileSerializer(profile).data
        
        return Response({
            'message': 'Registration successful',
            'user': profile_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Get user profile
        try:
            profile = UserProfile.objects.select_related('company', 'user').get(user=user)
            profile_data = UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'message': 'Login successful',
            'user': profile_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
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