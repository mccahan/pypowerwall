# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tedapi.proto
# Protobuf Python Version: 4.25.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ctedapi.proto\x12\x06tedapi\"O\n\x07Message\x12(\n\x07message\x18\x01 \x01(\x0b\x32\x17.tedapi.MessageEnvelope\x12\x1a\n\x04tail\x18\x02 \x01(\x0b\x32\x0c.tedapi.Tail\"\xe0\x01\n\x0fMessageEnvelope\x12\x17\n\x0f\x64\x65liveryChannel\x18\x01 \x01(\x05\x12#\n\x06sender\x18\x02 \x01(\x0b\x32\x13.tedapi.Participant\x12&\n\trecipient\x18\x03 \x01(\x0b\x32\x13.tedapi.Participant\x12\'\n\x06\x63onfig\x18\x0f \x01(\x0b\x32\x12.tedapi.ConfigTypeH\x00\x88\x01\x01\x12\'\n\x07payload\x18\x10 \x01(\x0b\x32\x11.tedapi.QueryTypeH\x01\x88\x01\x01\x42\t\n\x07_configB\n\n\x08_payload\"g\n\x0bParticipant\x12\r\n\x03\x64in\x18\x01 \x01(\tH\x00\x12\x16\n\x0cteslaService\x18\x02 \x01(\x05H\x00\x12\x0f\n\x05local\x18\x03 \x01(\x05H\x00\x12\x1a\n\x10\x61uthorizedClient\x18\x04 \x01(\x05H\x00\x42\x04\n\x02id\"\x15\n\x04Tail\x12\r\n\x05value\x18\x01 \x01(\x05\"t\n\tQueryType\x12+\n\x04send\x18\x01 \x01(\x0b\x32\x18.tedapi.PayloadQuerySendH\x00\x88\x01\x01\x12(\n\x04recv\x18\x02 \x01(\x0b\x32\x15.tedapi.PayloadStringH\x01\x88\x01\x01\x42\x07\n\x05_sendB\x07\n\x05_recv\"\xac\x01\n\x10PayloadQuerySend\x12\x10\n\x03num\x18\x01 \x01(\x05H\x00\x88\x01\x01\x12+\n\x07payload\x18\x02 \x01(\x0b\x32\x15.tedapi.PayloadStringH\x01\x88\x01\x01\x12\x11\n\x04\x63ode\x18\x03 \x01(\x0cH\x02\x88\x01\x01\x12#\n\x01\x62\x18\x04 \x01(\x0b\x32\x13.tedapi.StringValueH\x03\x88\x01\x01\x42\x06\n\x04_numB\n\n\x08_payloadB\x07\n\x05_codeB\x04\n\x02_b\"l\n\nConfigType\x12)\n\x04send\x18\x01 \x01(\x0b\x32\x19.tedapi.PayloadConfigSendH\x00\x12)\n\x04recv\x18\x02 \x01(\x0b\x32\x19.tedapi.PayloadConfigRecvH\x00\x42\x08\n\x06\x63onfig\".\n\x11PayloadConfigSend\x12\x0b\n\x03num\x18\x01 \x01(\x05\x12\x0c\n\x04\x66ile\x18\x02 \x01(\t\"E\n\x11PayloadConfigRecv\x12\"\n\x04\x66ile\x18\x01 \x01(\x0b\x32\x14.tedapi.ConfigString\x12\x0c\n\x04\x63ode\x18\x02 \x01(\x0c\"*\n\x0c\x43onfigString\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x64 \x01(\t\",\n\rPayloadString\x12\r\n\x05value\x18\x01 \x01(\x05\x12\x0c\n\x04text\x18\x02 \x01(\t\"\x1c\n\x0bStringValue\x12\r\n\x05value\x18\x01 \x01(\tb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tedapi_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_MESSAGE']._serialized_start=24
  _globals['_MESSAGE']._serialized_end=103
  _globals['_MESSAGEENVELOPE']._serialized_start=106
  _globals['_MESSAGEENVELOPE']._serialized_end=330
  _globals['_PARTICIPANT']._serialized_start=332
  _globals['_PARTICIPANT']._serialized_end=435
  _globals['_TAIL']._serialized_start=437
  _globals['_TAIL']._serialized_end=458
  _globals['_QUERYTYPE']._serialized_start=460
  _globals['_QUERYTYPE']._serialized_end=576
  _globals['_PAYLOADQUERYSEND']._serialized_start=579
  _globals['_PAYLOADQUERYSEND']._serialized_end=751
  _globals['_CONFIGTYPE']._serialized_start=753
  _globals['_CONFIGTYPE']._serialized_end=861
  _globals['_PAYLOADCONFIGSEND']._serialized_start=863
  _globals['_PAYLOADCONFIGSEND']._serialized_end=909
  _globals['_PAYLOADCONFIGRECV']._serialized_start=911
  _globals['_PAYLOADCONFIGRECV']._serialized_end=980
  _globals['_CONFIGSTRING']._serialized_start=982
  _globals['_CONFIGSTRING']._serialized_end=1024
  _globals['_PAYLOADSTRING']._serialized_start=1026
  _globals['_PAYLOADSTRING']._serialized_end=1070
  _globals['_STRINGVALUE']._serialized_start=1072
  _globals['_STRINGVALUE']._serialized_end=1100
# @@protoc_insertion_point(module_scope)
