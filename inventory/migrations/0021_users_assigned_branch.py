from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0020_stocklevel_is_active_state_sync"),
    ]

    operations = [
        migrations.AddField(
            model_name="users",
            name="assigned_branch",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_users",
                to="inventory.branches",
            ),
        ),
    ]
