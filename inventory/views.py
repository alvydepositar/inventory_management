from django.shortcuts import render

def auth_login(request):
    return render(request, 'html/auth-login.html')
