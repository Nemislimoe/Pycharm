from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def products(request):
    # Тестові дані — в реальному проєкті беруться з БД
    product_list = [
        {
            'image_url': 'https://placehold.co/400x300?text=Товар+1',
            'name': 'Ноутбук Pro',
            'description': 'Потужний ноутбук для роботи та навчання з процесором Intel i7.',
            'price': '32 999',
        },
        {
            'image_url': 'https://placehold.co/400x300?text=Товар+2',
            'name': 'Бездротові навушники',
            'description': 'Комфортні навушники з шумозаглушенням та 30 год автономності.',
            'price': '4 499',
        },
        {
            'image_url': 'https://placehold.co/400x300?text=Товар+3',
            'name': 'Механічна клавіатура',
            'description': 'Ергономічна клавіатура з RGB-підсвіткою та Cherry MX перемикачами.',
            'price': '3 199',
        },
    ]
    return render(request, 'products.html', {'products': product_list})


def profile(request):
    return render(request, 'myapp/profile.html')


def contact(request):
    return render(request, 'contact.html')
