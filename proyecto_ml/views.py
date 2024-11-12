from django.shortcuts import render

def classify_image(request):
    return render(request, 'classify_image.html')
def upload_dataset(request):
    return render(request, 'upload_dataset.html')
def inicio(request):
    return render(request, 'inicio.html')