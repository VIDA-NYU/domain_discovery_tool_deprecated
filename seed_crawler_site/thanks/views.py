from django.shortcuts import render

# Create your views here.

def show_thanks(request):
    return render(request, 'thanks.html')
