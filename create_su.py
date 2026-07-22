import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "palenque_flow.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username="jason_admin").exists():
    User.objects.create_superuser("jason_admin", "admin@olascafe.com", "AdminOlas2026!")
    print("Superuser created successfully.")
else:
    print("Superuser already exists.")
