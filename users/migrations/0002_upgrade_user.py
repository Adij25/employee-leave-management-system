from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone
from django.contrib.auth.hashers import make_password


def hash_legacy_pins(apps, schema_editor):
    User = apps.get_model("users", "CustomUser")
    for user in User.objects.all():
        pin = user.pin or ""
        if len(pin) == 4 and pin.isdigit():
            user.password = make_password(pin)
            user.pin = ""
            user.save(update_fields=["password", "pin"])


class Migration(migrations.Migration):
    dependencies = [("users", "0001_initial")]

    operations = [
        migrations.AlterField(model_name="customuser", name="phone", field=models.CharField(max_length=15, unique=True)),
        migrations.AlterField(model_name="customuser", name="pin", field=models.CharField(max_length=128, blank=True, editable=False)),
        migrations.AddField(model_name="customuser", name="email", field=models.EmailField(blank=True, max_length=254)),
        migrations.AddField(model_name="customuser", name="employee_id", field=models.CharField(max_length=30, unique=True, null=True, blank=True)),
        migrations.AddField(model_name="customuser", name="department", field=models.CharField(max_length=100, blank=True)),
        migrations.AddField(model_name="customuser", name="date_joined", field=models.DateTimeField(default=timezone.now)),
        migrations.AlterField(model_name="customuser", name="first_name", field=models.CharField(max_length=50)),
        migrations.AlterField(model_name="customuser", name="last_name", field=models.CharField(max_length=50)),
        migrations.RunPython(hash_legacy_pins, migrations.RunPython.noop),
        migrations.AlterField(model_name="customuser", name="date_joined", field=models.DateTimeField(auto_now_add=True)),
    ]
