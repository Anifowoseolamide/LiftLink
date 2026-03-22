import os
import django
from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rideshare.settings")
django.setup()

from accounts.models import User
from accounts.admin import CustomUserAdmin

u = User.objects.get(id=4)
print(f"Before: {u.driver_verification_status}")

admin_mock = CustomUserAdmin(User, AdminSite())
request = RequestFactory().post(f'/admin/accounts/user/{u.id}/change/', {
    'username': u.username,
    'first_name': u.first_name,
    'last_name': u.last_name,
    'email': u.email,
    'is_active': 'on',
    'is_staff': 'on',
    'is_superuser': 'on',
    'role': u.role,
    'driver_verification_status': 'ACTIVE',
    '_save': 'Save'
})
# Actually let's just test if the model form validates and saves.
# This might be complicated. Instead, let's just make a test using the actual Admin Form.
from django.contrib.auth.forms import UserChangeForm
ModelForm = admin_mock.get_form(request, obj=u)
form = ModelForm(data={
    'username': u.username,
    'driver_verification_status': 'ACTIVE',
    'role': u.role,
}, instance=u)

print("Form valid?", form.is_valid())
if not form.is_valid():
    print(form.errors)
else:
    form.save()
    u.refresh_from_db()
    print("After:", u.driver_verification_status)
