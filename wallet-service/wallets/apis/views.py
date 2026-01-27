from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from wallets.models import Wallet
from wallets.apis.serializets import WalletSerializer
from wallets.services.wallet_operations import WalletOperationService


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all().order_by('-created_at')
    serializer_class = WalletSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'], url_path='(?P<user_id>[^/]+)/debit')
    def debit(self, request, user_id=None):
        """
        Debita de la wallet del usuario (idempotent).
        
        Body:
        {
            "amount": "100.00",
            "idempotency_key": "debit-tx-123"
        }
        """
        try:
            amount = Decimal(request.data.get('amount', '0'))
            idempotency_key = request.data.get('idempotency_key')
            
            if not idempotency_key:
                return Response(
                    {"error": "idempotency_key is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if amount <= 0:
                return Response(
                    {"error": "Amount must be positive"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = WalletOperationService.debit(
                user_id=user_id,
                amount=amount,
                idempotency_key=idempotency_key
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='(?P<user_id>[^/]+)/credit')
    def credit(self, request, user_id=None):
        """
        Acredita a la wallet del usuario (idempotent).
        
        Body:
        {
            "amount": "100.00",
            "idempotency_key": "credit-tx-123"
        }
        """
        try:
            amount = Decimal(request.data.get('amount', '0'))
            idempotency_key = request.data.get('idempotency_key')
            
            if not idempotency_key:
                return Response(
                    {"error": "idempotency_key is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if amount <= 0:
                return Response(
                    {"error": "Amount must be positive"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = WalletOperationService.credit(
                user_id=user_id,
                amount=amount,
                idempotency_key=idempotency_key
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
