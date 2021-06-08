import re
from django.db import connection
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import boto3
from .models import Connection, ChatMessage

# Create your views here.

@csrf_exempt
def test(request):
    print("hello")
    print(request.body.decode("utf-8"))
    return JsonResponse({"message":"Hello Daud"}, status=200)

def _parse_body(body):
   body_unicode = body.decode('utf-8')
   return  json.loads(body_unicode)

@csrf_exempt
def connect(request):
    body = _parse_body(request.body)
    connection_id = body['connectionId']
    connections = Connection.objects.create(connection_id=connection_id)
    print(connections)
    return JsonResponse("connect successfully", status=200, safe=False)


@csrf_exempt
def disconnect(request):
    body = _parse_body(request.body)
    connection_id = body['connectionId']
    connections = Connection.objects.get(connection_id=connection_id)
    connections.delete() 
    return JsonResponse("disconnect successfully", status=200, safe=False)


# helper function
def _send_to_connection(connection_id, data):
    gatewayapi=boto3.client('apigatewaymanagementapi', endpoint_url="https://o4wgsdn9ga.execute-api.us-east-1.amazonaws.com/test",region_name="us-east-1", aws_access_key_id="AKIAWK22EWER2FJ2GIZ2",aws_secret_access_key="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", )
    response = gatewayapi.post_to_connection(ConnectionId=connection_id, Data=json.dumps(data).encode('utf-8'))
    return response


@csrf_exempt
def send_message(request):
    print("send message was successfull")
    body = _parse_body(request.body)
    dictionary_body = dict(body)
    username = dictionary_body['body']['username']
    timestamp = dictionary_body['body']['timestamp']
    content = dictionary_body['body']['content']
    ChatMessage.objects.create(username=username, timestamp=timestamp, messages=content)
    connections = Connection.objects.all()
    messages = {
        "username":username,
        "timestamp":timestamp,
        "messages":content
    }
    data = {"messages":[messages]} 
    
    for connection in connections:
        _send_to_connection(connection.connection_id, data)
    return JsonResponse({"message":"successfully sent"}, status=200, safe=False)

@csrf_exempt
def recent_messages(request):
    body = _parse_body(request.body)
    connectionId = body["connectionId"]
    connection_id = Connection.objects.get(connection_id=connectionId)
    chat_messages = ChatMessage.objects.all()
    for msg in chat_messages:
        data = {"messages": [
            {"username":msg.username, "messages":msg.messages, "timestamp":msg.timestamp}
        ]}
        return _send_to_connection(connection_id,data)
    return JsonResponse('successfully sent', status=200, safe=False)
    
    
    