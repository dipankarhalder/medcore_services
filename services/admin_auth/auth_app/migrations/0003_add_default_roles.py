from django.db import migrations

def create_default_roles(apps, schema_editor):
    Role = apps.get_model('auth_app', 'Role')
    default_roles = [
        ('super_admin', 'Super Admin', 'System Super Administrator'),
        ('admin', 'Admin', 'System Administrator'),
        ('account_manager', 'Account Manager', 'Handles accounts and billing workflows'),
        ('accountant', 'Accountant', 'Handles financial and invoicing workflows'),
        ('department_manager', 'Department Manager', 'Manages hospital departments'),
        ('receptionist', 'Receptionist', 'Manages patient check-ins and appointments'),
        ('staff', 'Staff', 'General staff member'),
        ('Doctor', 'Doctor', 'Medical doctor role'),
    ]
    for name, display_name, description in default_roles:
        Role.objects.get_or_create(
            name=name,
            defaults={'display_name': display_name, 'description': description}
        )

def remove_default_roles(apps, schema_editor):
    Role = apps.get_model('auth_app', 'Role')
    Role.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0002_role_alter_user_role'),
    ]

    operations = [
        migrations.RunPython(create_default_roles, reverse_code=remove_default_roles),
    ]
