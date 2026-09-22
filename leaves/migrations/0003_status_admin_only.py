from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('leaves', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaverequest',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                default='pending',
                editable=False,
                help_text='Controlled by the admin approval workflow. Employees cannot change this field.',
                max_length=20,
            ),
        ),
    ]
