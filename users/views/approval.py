# users/views/approval.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import UserModel
from users.serializers import UserApprovalSerializer, PendingUsersSerializer
from users.authentication import JWTAuthentication

class ApproveUserView(APIView):
    """s
    Handles user approval by super_admin.
    """
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = UserApprovalSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Check if the approver is a super_admin
            approver = UserModel.get_user_by_id(data["approver_id"])
            if not approver or approver["role_type"] != "super_admin":
                return Response({"error": "Only a super admin can approve users."}, status=status.HTTP_403_FORBIDDEN)

            # Approve the user
            rows_updated = UserModel.approve_user(data["user_id"])
            if rows_updated:
                return Response({"message": "User approved successfully."}, status=status.HTTP_200_OK)

            return Response({"error": "User not found or already approved."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PendingUsersView(APIView):
    """
    Retrieves a list of users pending approval.
    Only accessible by super_admins.
    """
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Check if the user is a super_admin
        if request.user["role_type"] != "super_admin":
            return Response({"error": "Only super admins can view pending approvals."}, status=status.HTTP_403_FORBIDDEN)

        # Fetch pending users
        pending_users = UserModel.get_pending_users()
        serializer = PendingUsersSerializer(pending_users, many=True)
        return Response(serializer.data)