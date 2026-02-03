from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
import requests
from django.conf import settings


def home(request):
    """Home page - redirect to dashboard if authenticated"""
    return render(request, 'web/home.html')


def login_view(request):
    """Login page"""
    return render(request, 'web/login.html')


def register_view(request):
    """Registration page"""
    return render(request, 'web/register.html')


def dashboard(request):
    """Dashboard page"""
    return render(request, 'web/dashboard.html')


def workers(request):
    """Workers management page"""
    return render(request, 'web/workers.html')


def suppliers(request):
    """Suppliers management page"""
    return render(request, 'web/suppliers.html')


def materials(request):
    """Materials management page"""
    return render(request, 'web/materials.html')


def work_distribution(request):
    """Work distribution page"""
    return render(request, 'web/work_distribution.html')


def work_return(request):
    """Work return page"""
    return render(request, 'web/work_return.html')


def stock(request):
    """Stock management page"""
    return render(request, 'web/stock.html')


def direct_login_test(request):
    """Direct login test - bypasses all form issues"""
    from django.http import HttpResponse
    with open('direct_login_test.html', 'r') as f:
        content = f.read()
    return HttpResponse(content)


def logout_view(request):
    """Logout user"""
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')