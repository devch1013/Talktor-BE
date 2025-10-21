from rest_framework.renderers import serializers


class BaseSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    message = serializers.CharField()
    data = serializers.JSONField()
