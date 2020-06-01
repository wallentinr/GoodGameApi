# chat/consumers.py
import json
import sys
import asyncio
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from channels.consumer import AsyncConsumer
from app.serializers import PartySimpleSerializer

ticketDict={}

class ChatConsumer(AsyncWebsocketConsumer):
        async def connect(self):
            self.ticket = self.scope['url_route']['kwargs']['ticket']
            if(self.ticket in ticketDict):
                user = ticketDict[self.ticket][0]
                party_list = ticketDict[self.ticket][1]
                self.scope['user'] = user
                ticketDict.pop(self.ticket)
                self.scope['parties'] = party_list
                print("check")
                sys.stdout.flush()
                for party_id in party_list:
                    print( party_id)
                    sys.stdout.flush()                
                    await self.channel_layer.group_add(str(party_id), self.channel_name)

                await self.accept()
                # Add user to the websocket group for each party
                sys.stdout.flush()
            else:
                pass


        async def disconnect(self, close_code):
            print("Disconnect function")
            sys.stdout.flush()
            for party_id in self.scope['parties']:
                self.channel_layer.group_discard(str(party_id), self.channel_name)

        async def receive(self, text_data=None, bytes_data=None):
            data = json.loads(json.loads(text_data)['message'])
            # If chat_type, which party
            # send to that party
            if (data['type'] == "leave_party"):
                print("leave_party message recieved")
                sys.stdout.flush()

                response = {'type': 'leaving_member',
                    'username':self.scope['user'].username
                }
                await self.channel_layer.group_send(str(data['id']),
                {
                    "type": "chat.message",
                    "text_data": json.dumps(response),
                })

                await self.channel_layer.group_discard(str(data['id']), self.channel_name)

            elif (data['type'] == "join_party"):
                await self.channel_layer.group_add(str(data['id']), self.channel_name)

                response = {'type': 'new_member',
                    'username':self.scope['user'].username
                }
                await self.channel_layer.group_send(str(data['id']),
                {
                    "type": "chat.message",
                    "text_data": json.dumps(response),
                })

            else:
                response = {'type': data['type'],
                    'username':self.scope['user'].username,
                            'text': data['mess'] ,
                            'id': data['id']}
                await self.channel_layer.group_send(str(data['id']),
                {
                    "type": "chat.message",
                    "text_data": json.dumps(response),
                },
                )

        async def chat_message(self, event):
            print("chat_message")
            sys.stdout.flush()
            await self.send(text_data=event["text_data"])
            print("chat_message sent")
            sys.stdout.flush()



    
#ERIKS KOD KANSKE FUNKAR NU?
#kwargs o sånt ligger i URL?
    
    # async def connect(self):
    #     print('connected LOL')
    #     await self.accept()
    #     # self.party_id = self.scope['url_route']['kwargs']['party_id']
    #     # self.party_group_name = 'chat_%s' % self.party_id

    #     # #Join room group
    #     # await self.channel_layer.group_add(
    #     #     self.party_group_name,
    #     #     self.channel_name
    #     # )
        

    # async def disconnect(self, close_code):
    #     # Leave room group
    #     await self.channel_layer.group_discard (
    #         self.party_group_name,
    #         self.channel_name
    #     )

    # # Receive message from WebSocket
    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']

    #     # Send message to room group
    #     await self.channel_layer.group_send(
    #         self.party_group_name,
    #         {
    #             'type': 'chat_message',
    #             'message': message
    #         }
    #     )

    # # Receive message from room group
    # async def chat_message(self, event):
    #     message = event['message']

    #     # Send message to WebSocket
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))