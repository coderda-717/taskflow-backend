from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, UserSerializer

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        user = request.user
        data = request.data
        
        # Check if username is being changed and if it's already taken
        new_username = data.get('username')
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                return Response(
                    {'error': 'Username already taken'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.username = new_username
        
        # Update basic fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            # Check if email is already taken by another user
            if data['email'] != user.email:
                if User.objects.filter(email=data['email']).exists():
                    return Response(
                        {'error': 'Email already taken'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            user.email = data['email']
        
        # Handle password change
        if 'new_password' in data and data['new_password']:
            current_password = data.get('current_password')
            
            if not current_password:
                return Response(
                    {'error': 'Current password is required to change password'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify current password
            if not user.check_password(current_password):
                return Response(
                    {'error': 'Current password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate new password length
            if len(data['new_password']) < 8:
                return Response(
                    {'error': 'New password must be at least 8 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(data['new_password'])
        
        # Save user
        user.save()
        
        # Return updated user data
        serializer = UserSerializer(user)
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)