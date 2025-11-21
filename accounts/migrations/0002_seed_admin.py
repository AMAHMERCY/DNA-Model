from django.db import migrations
from django.contrib.auth.hashers import make_password

def seed_initial_admin(apps, schema_editor):
    User = apps.get_model('accounts', 'User')

    
    if not User.objects.filter(email="admin@dnahealth.com").exists():
        User.objects.create(
            name="Super Admin",
            email="admin@dnahealth.com",
            password=make_password("Admin12345!"),  # CHANGE AFTER FIRST LOGIN
            role="admin"
        )

def remove_initial_admin(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(email="admin@dnahealth.com").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_initial_admin, remove_initial_admin),
    ]
