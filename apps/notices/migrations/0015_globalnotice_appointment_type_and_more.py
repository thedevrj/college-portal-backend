from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notices', '0014_globalnotice_internal_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='globalnotice',
            name='appointment_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Teaching', 'Teaching'),
                    ('Non-Teaching', 'Non-Teaching'),
                    ('Resourse Person', 'Resourse Person'),
                    ('Others', 'Others'),
                ],
                max_length=50,
                null=True,
                verbose_name='Appointment Choice',
            ),
        ),
        migrations.AddField(
            model_name='historicalglobalnotice',
            name='appointment_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Teaching', 'Teaching'),
                    ('Non-Teaching', 'Non-Teaching'),
                    ('Resourse Person', 'Resourse Person'),
                    ('Others', 'Others'),
                ],
                max_length=50,
                null=True,
                verbose_name='Appointment Choice',
            ),
        ),
    ]
