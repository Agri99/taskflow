# accounts/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Get the standard token first
        token = super().get_token(user)

        # Add custom claims
        from rbac.services import user_has_perm
        token['can_view_audit'] = user_has_perm(user, 'rbac.view_auditentry')

        return token