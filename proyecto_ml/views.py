from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
def inicial(request):
    return render(request, 'inicial.html')
