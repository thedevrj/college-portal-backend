from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0014_alter_portalaccess_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="token_version",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Increment to revoke all JWTs issued to this user.",
            ),
        ),
    ]
