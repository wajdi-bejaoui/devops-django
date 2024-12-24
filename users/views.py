from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
from rest_framework import status
import jwt, datetime

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response

class UserView(APIView):
    # def get(self, request):
    #     token = request.COOKIES.get('jwt')
    #
    #     if not token:
    #         raise AuthenticationFailed('Unauthenticated!')
    #
    #     try:
    #         payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    #     except jwt.ExpiredSignatureError:
    #         raise AuthenticationFailed('Unauthenticated!')
    #
    #     user = User.objects.filter(id=payload['id']).first()
    #     serializer = UserSerializer(user)
    #     return Response(serializer.data)

    def get(self, request, user_id):
        # token = request.COOKIES.get('jwt')
        # print("View has been triggered")  # Print a basic message
        auth_header = request.headers.get('Authorization')  # Get the Authorization header
        # print(f"auth_header received: {auth_header}")

        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('Unauthenticated!')

        token = auth_header.split(' ')[1]  # Extract the token from 'Bearer <token>'
        # print(f"Token received: {token}")
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=user_id).first()
        if user is None:
            raise AuthenticationFailed('User not found!')

        serializer = UserSerializer(user)
        return Response(serializer.data)
    

    def get_user_from_token(self, request):
        """
        A helper function to decode the JWT token and retrieve the user.
        """
        auth_header = request.headers.get('Authorization')
        print("header",auth_header)
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('Unauthenticated!')

        token = auth_header.split(' ')[1]  # Extract the token from 'Bearer <token>'
        print(token)

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            decoded_token = jwt.decode(token, 'secret', algorithms=['HS256'])
            print(decoded_token)

            user_id = decoded_token.get('id')
            print("user_id",user_id)

            if not user_id:
                raise AuthenticationFailed('Unauthenticated!')
            return User.objects.filter(id=user_id).first()
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Unauthenticated!')
    
    def patch(self, request, user_id):
        """
        Update the user profile for the given `user_id`.
        """

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')

        user = self.get_user_from_token(request)
        print("Authenticated user:", user)

        # Check if the logged-in user is updating their own profile
        if user.id != int(user_id):
            raise AuthenticationFailed('You can only update your own profile.')

        # Extract and handle password if provided
        password = request.data.pop('password', None)
        if password:
            user.set_password(password)  # Hash the password
            user.save()  # Save the user after setting password
            print("Password updated and hashed for user.")
        
        print('user',user)
        print("request data", request.data)

        # Update other fields with the serializer (excluding password)
        serializer = UserSerializer(user, data=request.data, partial=True)  
        if serializer.is_valid():
            serializer.save()  # Save other fields without affecting the password
            print("Other fields updated:", serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        """
        Delete the user profile for the given `user_id`.
        """
        user = self.get_user_from_token(request)
        print("delete user", user)

        if user.id != int(user_id):
            raise AuthenticationFailed('You can only delete your own profile.')

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
    

