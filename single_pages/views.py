from django.shortcuts import render
from shop.models import Item

def landing(request):
    recent_items = Item.objects.order_by('-pk')[:3]
    return render(request, 'single_pages/landing.html',{
        'recent_items' : recent_items,
    })

def about_company(request):
    return render(request, 'single_pages/about_company.html')