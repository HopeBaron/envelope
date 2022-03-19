from cmath import exp
from re import I
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.auth import login
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, Membership
from channels.db import database_sync_to_async


class GatewayConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    @database_sync_to_async
    def _get_memberships(self):
        user = self.scope['user']
        return list(user.memberships.select_related())

    async def _setup_channel_layer_groups(self):
        user = self.scope['user']
        channel_layer = self.channel_layer
        channel_name = self.channel_name
        user_id = user.id

        await channel_layer.group_add('users', channel_name)
        await channel_layer.group_add(f'{user_id}', channel_name)
        for membership in await self._get_memberships():
            await channel_layer.group_add(f'{membership.chat.id}', channel_name)

    async def receive_json(self, content, **kwargs):
        user = self.scope['user']
        if not user.is_anonymous:
            return
        token = content['token']
        access_token = None
        try:
            access_token = AccessToken(token)
        except TokenError:
            await self.send_json({'message': 'invalid token'})
            return
        user_id = access_token['user_id']
        user = await sync_to_async(User.objects.get)(id=user_id)
        await login(self.scope, user)
        await self._setup_channel_layer_groups()
        await sync_to_async(self.scope['session'].save)()

    async def broadcast(self, event):
        data = event['data']
        await self.send_json({'type': 'broadcast', 'data': data})
