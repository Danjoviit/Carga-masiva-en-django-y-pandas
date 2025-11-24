from rest_framework import serializers
from .models import Archivo

from rest_framework.parsers import MultiPartParser, FormParser
class RacSerializer(serializers.ModelSerializer):

    nombre = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Archivo
        fields = '__all__'

    def validate_cedula(self, value):

        if not value.isdigit():
            raise serializers.ValidationError("La cédula debe contener solo números.")
        

        if not (4 <= len(value) <= 12): 
             raise serializers.ValidationError("La cédula debe tener entre 4 y 12 dígitos.")
             
        return value

class ExcelUploadSerializer(serializers.Serializer):

    parser_classes = (MultiPartParser, FormParser)

    excel_file = serializers.FileField()
