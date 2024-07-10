from django.db.models import Q
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit
# local imports
from .serializers import AdminRegisterSerializer, SearchSerializer, FriendRequestSerializer, UserSerializer
from .models import User, FriendRequest
# Create your views here.


class AdminRegisterView(APIView):
    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)

        # Validates and save the serializer
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

        # If email given as Input
        if email:
            try:
                user = User.objects.get(email=email)
                serializer = SearchSerializer(user)
            
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except User.DoesNotExist as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        # If Username given as Input   
        users = User.objects.filter(Q(name__icontains=name))
        serializer = SearchSerializer(users, many=True)

        # Paginating the fetched User instances
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(users, request)
        if page is not None:
            serializer = SearchSerializer(users, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        return Response(paginator.get_paginated_response(serializer.data))
    

class FriendRequestViewSet(APIView):
    permission_classes = [IsAuthenticated]

    # Users can not send more than 3 friend requests within a minute.
    @method_decorator(ratelimit(key='user', rate='3/m', method='POST', block=True))
    def post(self, request):
        to_user_id = request.data.get('to_user_id')
        to_user = User.objects.get(id=to_user_id)

        # Create a friend request
        friend_request, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        if not created:
            return Response({"detail": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "Friend request send successfully!!"}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        friend_request = FriendRequest.objects.get(id=pk)

        # Change the request status to accept or reject
        if request.data.get('status') in ['accepted', 'rejected']:
            friend_request.status = request.data.get('status')
            friend_request.save()
            return Response({"detail": f"Friend request {request.data.get('status')} successfully!!"}, status = status.HTTP_200_OK)
        
        return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        # Fetch the pending FriendRequest instances
        received_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
        serializer = FriendRequestSerializer(received_requests, many=True)

        return Response({"data": serializer.data}, status = status.HTTP_200_OK)
          

class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]

    # Fetch users who have accepted friend request 
    def get(self, request):
        friends_list = User.objects.filter(sent_requests__to_user=self.request.user, sent_requests__status='accepted')
        
        serializer =  UserSerializer(friends_list, many=True)
        return Response({"data": serializer.data}, status = status.HTTP_200_OK)