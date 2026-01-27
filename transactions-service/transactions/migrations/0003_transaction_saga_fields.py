# Generated migration for Transaction saga fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_outbox'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='saga_step',
            field=models.CharField(
                choices=[
                    ('PENDING', 'Pending'),
                    ('DEBITING', 'Debiting'),
                    ('CREDITING', 'Crediting'),
                    ('COMPENSATING', 'Compensating'),
                    ('COMPLETED', 'Completed'),
                    ('FAILED', 'Failed')
                ],
                default='PENDING',
                max_length=16
            ),
        ),
        migrations.AddField(
            model_name='transaction',
            name='debit_idempotency_key',
            field=models.CharField(
                blank=True,
                max_length=64,
                null=True,
                unique=True
            ),
        ),
        migrations.AddField(
            model_name='transaction',
            name='credit_idempotency_key',
            field=models.CharField(
                blank=True,
                max_length=64,
                null=True,
                unique=True
            ),
        ),
    ]
