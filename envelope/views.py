from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework_nested import routers
from rest_framework.decorators import action
from .serializers import *
from .models import *


class ChatViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def perform_create(self, serializer):
        users = serializer.validated_data['users']
        me = self.request.user.id
        if me not in users:
            users.append(me)
        super().perform_create(serializer)
class IsSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        target = view.get_object().id
        me = request.user.id
        return me == target

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSelf]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_url_kwarg = 'user_pk'

    def get_permissions(self):
        if self.action == "create":
            return []
        return super().get_permissions()
    
    def get_object(self):
        """ 
        modifies the original get_object method to allow for @me short hand for the current user.
        """
        user_id = self.kwargs[self.lookup_url_kwarg]
        invoker_id = self.request.user.id
        is_me = user_id == '@me'
        self.kwargs[self.lookup_url_kwarg] = invoker_id if is_me else user_id
        return super().get_object()
    
    @action(detail=True)
    def memberships(self, *args, **kwargs):
        user = self.get_object()
        page = self.paginate_queryset(user.memberships)
        if page is not None:
            serializer = MembershipSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MembershipSerializer(user.memberships, many=True)
        return Response(serializer.data)
        
        


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    def get_queryset(self):
        return Message.objects.filter(chat=self.kwargs['chat_pk'])

    def perform_create(self, serializer):
        chat_pk = self.kwargs['chat_pk']
        serializer.save(chat_id=chat_pk, author=self.request.user)


class MembershipViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MembershipSerializer
    queryset = Membership.objects.all()

    def get_queryset(self):
        return Membership.objects.filter(chat=self.kwargs['chat_pk'])

    def perform_create(self, serializer):
        chat_pk = self.kwargs["chat_pk"]
        serializer.save(chat_id=chat_pk)


router = routers.SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'chats', ChatViewSet, basename='chat')
chats_router = routers.NestedSimpleRouter(router, r'chats', lookup='chat')
chats_router.register(r'memberships', MembershipViewSet,
                      basename='chat-memberships')
chats_router.register(r'messages', MessageViewSet, basename='chat-messages')
