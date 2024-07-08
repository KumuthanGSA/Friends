from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
# local imports
from .serializers import AdminRegisterSerializer, SearchSerializer
from .models import User
# Create your views here.


class AdminRegisterView(APIView):
    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'detail': "Admin user created successfully"}, status=status.HTTP_201_CREATED)
        
        return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Find the user with the provided email
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'detail': 'Email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check the password
        if not user.check_password(password):
            return Response({'detail': 'Wrong password'}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response_data = {
            'access_token': str(access),
            'refresh_token': str(refresh)
        }
        return Response({'detail': "Logged in successfully", 'data': response_data}, status=status.HTTP_200_OK)           
     

class LogoutView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            #Block refresh token
            RefreshToken(refresh_token).blacklist()
            return Response({"detail": "Logged out successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class SearchView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request):
        email = request.data.get("email")
        name =  request.data.get("name")
        if email:
            try:
                user = User.objects.get(email=email)
                serializer = SearchSerializer(user)
            
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"detail": str()}, status=status.HTTP_400_BAD_REQUEST)
            
        users = User.objects.filter(Q(name__icontains=name))
        serializer = SearchSerializer(users, many=True)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(users, request)
        if page is not None:
            serializer = SearchSerializer(users, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(paginator.get_paginated_response(serializer.data))
            
        
            
        
