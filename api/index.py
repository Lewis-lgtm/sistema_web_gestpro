from app import app  # Assumindo que 'app' é a instância do Flask no seu arquivo principal.

def handler(request):
    return app(request)
