from django.http import HttpResponse

def index(request):
    return HttpResponse("""
        <h1>TaskFlow Backend</h1>
        <p>This is a backend-focused Django project demonstrating:</p>
        <ul>
            <li>Task management with comment system</li>
            <li>Model-level permission logic</li>
            <li>Soft deletion and edit time windows</li>
            <li>Automated tests and CI pipeline</li>
        </ul>
        <p>Available routes:</p>
        <ul>
            <li>/admin/ — Django admin</li>
            <li>/tasks/ — Task-related views</li>
        </ul>
    """)