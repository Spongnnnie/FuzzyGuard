from django.shortcuts import render, redirect
from .forms import UserInfoForm
from .fuzzy_logic import password_recommendation_system
from .fuzzy_logic import evaluate_password_strength
import random
import json
import string
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserInfoSerializer
from .models import UserInfo

# Define membership functions
def membership_functions():
    x_strength = np.arange(0, 11, 1)
    weak = fuzz.trimf(x_strength, [0, 0, 5])
    moderate = fuzz.trimf(x_strength, [3, 5, 8])
    strong = fuzz.trimf(x_strength, [6, 10, 10])
    return x_strength, weak, moderate, strong

# Evaluate fuzzy rules
def evaluate_rules(length, complexity, diversity):
    x_strength, weak, moderate, strong = membership_functions()
    length_level = fuzz.interp_membership(x_strength, strong, length)
    complexity_level = fuzz.interp_membership(x_strength, strong, complexity)
    diversity_level = fuzz.interp_membership(x_strength, strong, diversity)
    weak_level = min(length_level, complexity_level, diversity_level)
    moderate_level = np.mean([length_level, complexity_level, diversity_level])
    strong_level = max(length_level, complexity_level, diversity_level)
    password_strength = fuzz.defuzz(x_strength, np.fmax(weak, np.fmax(moderate, strong)), 'centroid')
    return password_strength

# Generate password based on user information
def generate_password(info):
    words = [info['name'], info['maiden_name'], info['nickname'], info['profession']]
    random.shuffle(words)
    password = ''.join([word[:random.randint(2, 4)] for word in words])
    password += str(random.randint(10, 99))
    password = ''.join(random.sample(password, len(password)))
    return password

# Evaluate complexity and diversity of the password
def evaluate_complexity(password):
    length = len(password)
    diversity = len(set(password))
    complexity = sum([1 for char in password if char.isdigit()]) + sum([1 for char in password if not char.isalnum()])
    return length, complexity, diversity


# Create your views here.
def password_recommendation_system(info):
    password = generate_password(info)
    length, complexity, diversity = evaluate_complexity(password)
    strength = evaluate_rules(length, complexity, diversity)

    if strength >= 7:
        strength_label = "Strong"
    elif strength >= 4:
        strength_label = "Moderate"
    else:
        strength_label = "Weak"

    return password, strength_label

def index(request):
    if request.method == 'POST':
        form = UserInfoForm(request.POST)
        if form.is_valid():
            info = form.cleaned_data
            password, strength_label = password_recommendation_system(info)
            return render(request, 'password_app/result.html', {'password': password, 'strength': strength_label})
    else:
        form = UserInfoForm()

    return render(request, 'password_app/index.html', {'form': form})

def recommend_password(request):
    if request.method == 'POST':
        length_input = int(request.POST['length'])
        complexity_input = int(request.POST['complexity'])
        
        # Evaluate password strength
        strength_score = evaluate_password_strength(length_input, complexity_input)
        
        # Categorize based on the strength score
        if strength_score < 25:
            password_strength = 'Very Weak'
        elif strength_score < 50:
            password_strength = 'Weak'
        elif strength_score < 75:
            password_strength = 'Moderate'
        elif strength_score < 90:
            password_strength = 'Strong'
        else:
            password_strength = 'Very Strong'
        
        context = {
            'strength_score': strength_score,
            'password_strength': password_strength,
        }
        return render(request, 'index.html', context)
    
    return render(request, 'index.html')

def check_password_strength(request):
    if request.method == 'POST':
        password = request.POST['password']
        length_input = len(password)
        complexity_input = sum(c.isupper() for c in password) + sum(c.isdigit() for c in password) + sum(c in '!@#$%^&*()-_=+[]{}|;:<>,.?/~`' for c in password)
        
        # Evaluate password strength
        strength_score = evaluate_password_strength(length_input, complexity_input)
        
        # Categorize based on the strength score
        if strength_score < 25:
            password_strength = 'Very Weak'
        elif strength_score < 50:
            password_strength = 'Weak'
        elif strength_score < 75:
            password_strength = 'Moderate'
        elif strength_score < 90:
            password_strength = 'Strong'
        else:
            password_strength = 'Very Strong'
        
        context = {
            'strength_score': strength_score,
            'password_strength': password_strength,
        }
        return render(request, 'index.html', context)
    
    return render(request, 'index.html')


@api_view(['POST'])
def generate_passwords(request):
    serializer = UserInfoSerializer(data=request.data)
    if serializer.is_valid():
        info = serializer.validated_data
        suggestions = password_recommendation_system(info, num_suggestions=3)
        return Response(suggestions)
    return Response(serializer.errors, status=400)

def check_password_strength(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        password = data.get('password', '')

        # Example: Define the fuzzy logic evaluation
        length = len(password)
        contains_upper = any(char.isupper() for char in password)
        contains_lower = any(char.islower() for char in password)
        contains_digit = any(char.isdigit() for char in password)
        contains_special = any(char in "!@#$%^&*()-_+=" for char in password)

        # Fuzzy logic setup
        x_strength = np.arange(0, 11, 1)
        strength_low = fuzz.trimf(x_strength, [0, 0, 5])
        strength_medium = fuzz.trimf(x_strength, [0, 5, 10])
        strength_high = fuzz.trimf(x_strength, [5, 10, 10])

        score = (length / 2) + (contains_upper + contains_lower + contains_digit + contains_special) * 2
        strength_level = fuzz.interp_membership(x_strength, strength_low, score), \
                         fuzz.interp_membership(x_strength, strength_medium, score), \
                         fuzz.interp_membership(x_strength, strength_high, score)

        if strength_level[2] > strength_level[1] and strength_level[2] > strength_level[0]:
            strength = "Strong"
        elif strength_level[1] > strength_level[0]:
            strength = "Moderate"
        else:
            strength = "Weak"

        return JsonResponse({'strength': strength})