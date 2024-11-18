from django.shortcuts import render

def auth_login(request):
    return render(request, 'html/auth-login.html')


def product_catalogue(request):
    return render(request, 'html/product-catalogue.html')
