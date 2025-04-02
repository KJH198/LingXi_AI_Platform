from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
import json
from .models import User

@csrf_exempt
def register(request):
    """
    Register a new user.

    Request body should contain:
    - username: The username of the user.
    - password: The password of the user.
    - phone_number: The phone number of the user.
    - email (optional): The email address of the user.

    Returns:
    - 201: User registered successfully.
    - 400: Invalid request data or user already exists.
    - 405: Invalid request method.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        phone_number = data.get('phone_number')
        email = data.get('email')

        if not username or not password or not phone_number:
            return JsonResponse({'error': 'Username, password and phone number are required'}, status=400)

        try:
            user = User.objects.create_user(username=username, password=password, phone_number=phone_number,
                                            email=email)
            return JsonResponse({'message': 'User registered successfully', 'user_id': user.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def user_login(request):
    """
    Log in a user.

    Request body should contain:
    - username: The username of the user.
    - password: The password of the user.

    Returns:
    - 200: Login successful.
    - 401: Invalid username or password.
    - 405: Invalid request method.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'user_id': user.id}, status=200)
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=401)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def update_user_info(request):
    """
    Update user information.

    Request body may contain:
    - username: The new username of the user.
    - phone_number: The new phone number of the user.
    - email: The new email address of the user.

    Returns:
    - 200: User information updated successfully.
    - 400: Username or phone number already exists.
    - 401: User is not authenticated.
    - 405: Invalid request method.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User is not authenticated'}, status=401)
        data = json.loads(request.body)
        user = request.user
        username = data.get('username')
        phone_number = data.get('phone_number')
        email = data.get('email')

        if username:
            try:
                existing_user = User.objects.exclude(id=user.id).get(username=username)
                return JsonResponse({'error': 'Username already exists'}, status=400)
            except User.DoesNotExist:
                user.username = username
        if phone_number:
            try:
                existing_user = User.objects.exclude(id=user.id).get(phone_number=phone_number)
                return JsonResponse({'error': 'Phone number already exists'}, status=400)
            except User.DoesNotExist:
                user.phone_number = phone_number
        if email:
            user.email = email

        user.save()
        return JsonResponse({'message': 'User information updated successfully'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=405)