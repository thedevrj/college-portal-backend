from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("vigilance", "0002_complaint_deleted_at_complaint_is_deleted_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="complaint",
            options={
                "permissions": [
                    (
                        "manage_complaints",
                        "Can view and update vigilance complaint case statuses through the API",
                    ),
                ],
            },
        ),
    ]
