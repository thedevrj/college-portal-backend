import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "college_backend_portal.settings")
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile

user = User(username="test_user_null_bug")
user.save()  # This will trigger post_save and get_or_create
print("User created successfully.")
