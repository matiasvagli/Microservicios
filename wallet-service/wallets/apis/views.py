from rest_framework import viewsets, permissions #importar viewsets y permisos de DRF
from wallets.models import Wallet #importar el modelo Wallet
from wallets.apis.serializets import WalletSerializer #importar el serializador WalletSerializer

#definir el viewset para el modelo Wallet (CRUD completo)
class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all() .order_by('-created_at') 
    serializer_class = WalletSerializer #especificar el serializador
    permission_classes = [permissions.AllowAny] #permitir acceso a cualquier usuario (ahay que cambiar a jwt auth luego)