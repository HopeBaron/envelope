import json
from channels.layers import get_channel_layer
from django.utils.decorators import async_only_middleware
from django.core.serializers.json import DjangoJSONEncoder


@async_only_middleware
def ChannelNotifyMiddleware(get_response):

    async def middleware(request):
        user = request.user
        ignored_methods = ('GET')
        response = await get_response(request)
        
        if request.method in ignored_methods:
            return response
        data = json.dumps(response.data, cls=DjangoJSONEncoder)
        channel_layer = get_channel_layer()
        await channel_layer.group_send('users', { 'type': 'broadcast', 'data': data},)
        return response

    return middleware
