from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .signals import order_created

from .models import *
import datetime

class BaseFileSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        base_id = self.context['base_id']
        return BaseFile.objects.create(base_id=base_id,  **validated_data)

    class Meta:
        model = BaseFile 
        fields = ['id', 'base_file']


class BaseSerializer(serializers.ModelSerializer):

    files = BaseFileSerializer(many=True, read_only=True)
    class Meta:
        model = BaseScenario 
        fields = [ 'scenario_info', 'geographic_areas', 'geographic_areas_by_state', 'data', 'created', 'completed', 'status', 'uuid', 'error', 'base_file', 'manure_nutrients_file', 'reportloads_file'] 
    def save(self, **kwargs):

        self.instance = BaseScenario.objects.create(**self.validated_data)

        return self.instance


class ExecutionFileSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        execution_id = self.context['execution_id']
        return ExecutionFile.objects.create(execution_id=execution_id, **validated_data)

    class Meta:
        model = ExecutionFile 
        fields = ['id', 'data']

class ExecutionSerializer(serializers.ModelSerializer):

    files = ExecutionFileSerializer(many=True, read_only=True)
    class Meta:
        model = Execution 
        fields = [ 'uuid', 'scenario', 'created_at', 'loads', 'bmps', 'costs', 'bmp_constraints', 'advanced_constraints', 'data', 'info', 'status']

    def save(self, **kwargs):
        self.instance = Execution.objects.create(
                **self.validated_data)

        return self.instance


class SolutionFileSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        execution_id = self.context['execution_id']
        return SolutionFile.objects.create(execution_id=execution_id, **validated_data)

    class Meta:
        model = SolutionFile 
        fields = ['id', 'reportloads_file']

class SolutionSerializer(serializers.ModelSerializer):

    files = SolutionFileSerializer(many=True, read_only=True)
    class Meta:
        model = Solution 
        fields = [ 'uuid', 'execution', 'data', 'info', 'added', 'evaluated', 'optimized', 'land_file', 'animal_file', 'manure_file', 'reportloads_file', 'sector_loads_file', 'land_json', 'animal_json', 'manure_json']


    def save(self, **kwargs):
        self.instance = Solution.objects.create(
                **self.validated_data)

        return self.instance


