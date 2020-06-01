#from django.contrib.auth.models import Group
from .models import Party, User, Message, Bracket
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser;

from app.serializers import UserSerializer,UserSimpleSerializer,  PartySerializer,PartySimpleSerializer ,MessageSerializer, BracketSerializer, ChangePasswordSerializer
from rest_framework import status
from rest_framework.response import Response

from rest_framework.authtoken.models import Token

from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .consumers import ticketDict
import sys
import secrets
import string


## User View Sets

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def myParties(self, request):
        parties = self.request.user.parties
        serializer = PartySimpleSerializer(parties, many=True)
        return Response(serializer.data)


    def list(self, request):
        
        queryset = User.objects.all()
        query = request.query_params.get('username', None)
        if query is not None:
            queryset = queryset.filter(username__icontains=query) 

        serializer = UserSimpleSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSimpleSerializer(user, context={'request': request})
        return Response(serializer.data)


    @action(detail=False, methods=['get'])
    def me(self, request):
        user = self.request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def join_party(self, request):
        party_id = request.data['party_id']
        user = self.request.user
        try:
            party_to_join = Party.objects.get(id=party_id)
        except Party.DoesNotExist:
            return Response("party does not exist", status=status.HTTP_404_NOT_FOUND)
        resp_string = ""
        resp_status = status.HTTP_100_CONTINUE
        if party_to_join.users.all().count() >= party_to_join.max_users:
            resp_string = "Party is full"
            resp_status = status.HTTP_406_NOT_ACCEPTABLE
        else:
            user.parties.add(party_to_join)
            resp_string = "Added to party" 
            resp_status = status.HTTP_202_ACCEPTED
        return Response(resp_string, resp_status)


    @action(detail=False, methods=['put'])
    def leave_party(self, request):
        party_id = request.data['party_id']
        user = self.request.user
        try:
            party_to_leave = Party.objects.get(id=party_id)
        except Party.DoesNotExist:
            return Response("party does not exist", status= status.HTTP_404_NOT_FOUND)
        user.parties.remove(party_to_leave)

        if party_to_leave.users.all().count() <= 0:
            Party.objects.filter(id=party_id).delete()

        return Response("left party")


    @action(detail=False, methods=['put'])
    def logout(self, request):
        user = self.request.user
        user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=['put'])
    def update_password(self, request):
        self.object = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({"old_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response("password updated", status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'])
    def ticket(self, request):
        ticket = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        parties = self.request.user.parties
        serializer = PartySimpleSerializer(parties, many=True)
        party_list = []
        for party in serializer.data:
            party_list.append(party["id"])
        
        ticketDict[ticket] = (self.request.user, party_list)
        print("Putting in ticket")
        sys.stdout.flush()
        return Response({ "ticket" : ticket})
        
    
## Logout View Set...thx djoser

# class Logout(APIView):
    
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
    
#     def put(self, request, format=None):
#         return Response("IDK")

#         # request.user.auth_token.delete()
#         # return Response(status=status.HTTP_204_NO_CONTENT)

## Party View Sets

class PartyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Party.objects.all().order_by('-date_added')
    serializer_class = PartySerializer
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        queryset = Party.objects.all()
        name_query = request.query_params.get('name', None)
        platform_query = request.query_params.get('platform', None)
        game_query = request.query_params.get('game', None)

        queryset = queryset.filter(name__icontains=name_query, platform__icontains=platform_query, game__icontains=game_query)
        serializer = PartySimpleSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        found = self.request.user.parties.filter(id = pk).count()
        if found != 0:
            queryset = Party.objects.all()
            party = get_object_or_404(queryset, pk=pk)
            numofusers = party.users.all().count()
            serializer = PartySerializer(party, context={'request': request})
            response = serializer.data
            response['number_of_users'] = numofusers
            return Response(response)
        else:
            return Response("Cant see information about parties you are not in!", status=status.HTTP_401_UNAUTHORIZED)


    @action(detail=True, methods=['post'])
    def post_message(self, request, pk=None):
        found = self.request.user.parties.filter(id = pk).count()
        if found != 0:
            party = Party.objects.filter(id=pk)
            message = Message.objects.create(text=request.data['text'], user=self.request.user, party=party[0])
            party[0].messages.add(message)
            return Response("message was succesfully posted")
        else:
            return Response("Cant post message in party you are not in!", status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        found = self.request.user.parties.filter(id = pk).count()
        if found != 0:
            party = Party.objects.filter(id=pk)
            users = User.objects.filter(parties__id=pk)
            serializer = UserSerializer(users, many=True, context={'request': request})
            return Response(serializer.data)
        else:
            return Response("You need to be in party to see members!", status=status.HTTP_401_UNAUTHORIZED)
            


## Bracket View Sets

class BracketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Bracket.objects.all()
    serializer_class = BracketSerializer
    permission_classes = [IsAdminUser]

## Message View Sets

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAdminUser]