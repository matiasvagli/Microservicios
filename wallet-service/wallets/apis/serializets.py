from rest_framework import serializers #para serializar y deserializar datos
from wallets.models import Wallet #importar el modelo Wallet

#definir el serializador para el modelo Wallet (damos forma a los datos)
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet #especificar el modelo
        fields = ['id', 'user_id', 'account_number', 'balance', 'currency', 'created_at', 'updated_at'] #campos a incluir
        read_only_fields = ['id', 'account_number', 'created_at', 'updated_at'] #campos de solo lectura

        