from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("portals", "0001_initial")]

    operations = [
        migrations.AlterModelOptions(
            name="grievance",
            options={
                "ordering": ["-submitted_at"],
                "permissions": [
                    (
                        "manage_grievances",
                        "Can view and update grievance case statuses through the API",
                    ),
                ],
                "verbose_name": "Grievance",
                "verbose_name_plural": "Grievances",
            },
        ),
    ]
