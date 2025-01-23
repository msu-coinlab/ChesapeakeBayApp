from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
from django.utils import timezone


class User(AbstractUser):
    pass

class State(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=2)

    def __str__(self):
        return self.name

class County(models.Model):
    name = models.CharField(max_length=100)
    fips = models.IntegerField()
    state = models.CharField(max_length=2)
    def __str__(self):
        return self.name

class ScenarioInfo(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    data_revision = models.IntegerField()
    condition = models.IntegerField()
    type_id = models.IntegerField()
    backout= models.IntegerField()
    point_src = models.IntegerField()
    atm_dep = models.IntegerField()
    climate_change = models.IntegerField()
    soil = models.IntegerField()
    base_load = models.IntegerField()
    def __str__(self):
        return self.name

class GeographicArea(models.Model):
    name = models.CharField(max_length=100)
    fips = models.IntegerField()
    county = models.IntegerField()
    state = models.CharField(max_length=2)
    ncounties = models.IntegerField()
    geo_data= models.JSONField(default=dict, null=True, blank=True)
    def __str__(self):
        return '{}, {}'.format(self.name, self.state)

class LandRiverSegment(models.Model):
    name = models.CharField(max_length=100)
    fips = models.IntegerField()
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    geographic_area = models.ForeignKey(GeographicArea, on_delete=models.CASCADE, null=True, blank=True)
    acres = models.DecimalField(max_digits=10, decimal_places=3)
    geo_data = models.JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.name)
    
class Sector(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class BmpCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class BmpType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BmpUnit(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class AnimalGrp(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Agency(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.name

class LoadSrc(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    sector= models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    def __str__(self):
        return self.name

class Bmp(models.Model):
    short_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    bmp_category = models.ForeignKey(BmpCategory, on_delete=models.CASCADE)
    bmp_type = models.ForeignKey(BmpType, on_delete=models.CASCADE)
    sector= models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True)
    #unit = models.ForeignKey(BmpUnit, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class BaseScenario(models.Model):
    STATUS_PENDING = 'P'
    STATUS_EVALUATING = 'E'
    STATUS_COMPLETE = 'C'
    STATUS_FAILED = 'F'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_EVALUATING, 'Evaluating'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_FAILED, 'Failed')
    ]
    scenario_info = models.ForeignKey(ScenarioInfo, on_delete=models.CASCADE, verbose_name='Wastewater Data Set')
    geographic_areas = models.ManyToManyField(GeographicArea, related_name='base_geographic_areas', verbose_name='Geographic Scale (counties)')
    geographic_areas_by_state = models.JSONField(default=dict, null=True, blank=True)
    data = models.JSONField(default=dict, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    uuid = models.UUIDField(null=True, blank=True, default=uuid4)
    error = models.TextField(null=True, blank=True)
    base_file = models.FileField( upload_to='base_files', null=True, blank=True)
    manure_nutrients_file = models.FileField( upload_to='base_files', null=True, blank=True)
    reportloads_file = models.FileField( upload_to='base_files', null=True, blank=True)


class BmpCost(models.Model):
    bmp = models.ForeignKey(Bmp, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=20)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    bmp_state = models.CharField(max_length=20)


class Scenario(models.Model):
    STATUS_PENDING = 'P'
    STATUS_RETRIEVING= 'R'
    STATUS_EVALUATING = 'E'
    STATUS_COMPLETE = 'C'
    STATUS_FAILED = 'F'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RETRIEVING, 'Retrieving'),
        (STATUS_EVALUATING, 'Evaluating'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_FAILED, 'Failed')
    ]
    name = models.CharField(max_length=100, verbose_name='Optimization Scenario Name')
    scenario_info = models.ForeignKey(ScenarioInfo, on_delete=models.CASCADE, verbose_name='Wastewater Data Set')#Wastewater Data Set')
    geographic_areas = models.ManyToManyField(GeographicArea, related_name='geographic_areas', verbose_name='Geographic Scale (counties)')
    base_scenario = models.ForeignKey(BaseScenario, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,verbose_name='Date modified (EST)')
    loads = models.JSONField(default=dict, null=True, blank=True)
    bmps = models.JSONField(default=dict, null=True, blank=True)
    costs = models.JSONField(default=dict, null=True, blank=True)
    bmp_constraints = models.JSONField(default=dict, null=True, blank=True)
    advanced_constraints = models.JSONField(default=dict, null=True, blank=True)
    misc_data = models.JSONField(default=dict, null=True, blank=True)
    manure_counties = models.JSONField(default=dict, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_with = models.ManyToManyField(User, related_name='shared_with_users', null=True, blank=True)

    def __str__(self):
        return self.name

class Result(models.Model):
    uuid = models.UUIDField(null=True, blank=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    loads = models.JSONField(default=dict, null=True, blank=True)
    bmps = models.JSONField(default=dict, null=True, blank=True)
    costs = models.JSONField(default=dict, null=True, blank=True)
    bmp_constraints = models.JSONField(default=dict, null=True, blank=True)
    advanced_constraints = models.JSONField(default=dict, null=True, blank=True)
    data = models.JSONField(default=dict, null=True, blank=True)
    info = models.JSONField(default=dict, null=True, blank=True)
    land_file = models.FileField( upload_to='results', null=True, blank=True)
    animal_file = models.FileField( upload_to='results', null=True, blank=True)
    manure_file = models.FileField( upload_to='results', null=True, blank=True)

class Execution(models.Model):
    STATUS_PENDING = 'P'
    STATUS_EVALUATING = 'E'
    STATUS_COMPLETE = 'C'
    STATUS_FAILED = 'F'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_EVALUATING, 'Evaluating'),
        (STATUS_COMPLETE, 'Complete'),
        (STATUS_FAILED, 'Failed')
    ]

    uuid = models.UUIDField(null=True, blank=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    loads = models.JSONField(default=dict, null=True, blank=True)
    bmps = models.JSONField(default=dict, null=True, blank=True)
    costs = models.JSONField(default=dict, null=True, blank=True)
    bmp_constraints = models.JSONField(default=dict, null=True, blank=True)
    advanced_constraints = models.JSONField(default=dict, null=True, blank=True)
    data = models.JSONField(default=dict, null=True, blank=True)
    info = models.JSONField(default=dict, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)


class ExecutionFile(models.Model):
    TYPE_CSV = 'C'
    TYPE_PARQUET = 'P'
    TYPE_CHOICES = [
        (TYPE_CSV, 'CSV'),
        (TYPE_PARQUET, 'Parquet'),
    ]
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE, related_name='files')
    f_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=TYPE_CSV)
    execution_file = models.FileField(
        upload_to='api/exec_files',
    )



class BmpCostCustom(models.Model):
    bmp_cost = models.ForeignKey(BmpCost, on_delete=models.CASCADE)
    original_cost = models.DecimalField(max_digits=8, decimal_places=2)
    new_cost = models.DecimalField(max_digits=8, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class BmpConstraint(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    bmp_cost = models.ForeignKey(BmpCost, on_delete=models.CASCADE)
    max_units = models.DecimalField(max_digits=10, decimal_places=2)

class Pollutant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.name

class JsonFile(models.Model):
    name = models.CharField(max_length=100)
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    json_file = models.JSONField(default=dict, null=True, blank=True)
    zip_file = models.FileField( upload_to='results/zips', null=True, blank=True)


    def __str__(self):
        return self.name


class Results(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Solution(models.Model):
    uuid = models.UUIDField(null=True, blank=True)
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE)
    data = models.JSONField(default=dict, null=True, blank=True)
    info = models.JSONField(default=dict, null=True, blank=True)
    added = models.BooleanField(default=False, null=True, blank=True)
    evaluated = models.BooleanField(default=False, null=True, blank=True)
    optimized = models.BooleanField(default=False, null=True, blank=True)
    land_file = models.FileField( upload_to='results', null=True, blank=True)
    animal_file = models.FileField( upload_to='results', null=True, blank=True)
    manure_file = models.FileField( upload_to='results', null=True, blank=True)
    reportloads_file = models.FileField( upload_to='results', null=True, blank=True)
    sector_loads_file = models.FileField( upload_to='results', null=True, blank=True)
    land_json = models.JSONField(default=dict, null=True, blank=True)
    animal_json = models.JSONField(default=dict, null=True, blank=True)
    manure_json = models.JSONField(default=dict, null=True, blank=True)


class SolutionFile(models.Model):
    TYPE_CSV = 'C'
    TYPE_PARQUET = 'P'
    TYPE_CHOICES = [
        (TYPE_CSV, 'CSV'),
        (TYPE_PARQUET, 'Parquet'),
    ]
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE, related_name='files')
    f_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=TYPE_CSV)
    base_file = models.FileField(
        upload_to='api/solution_files',
    )



class BaseFile(models.Model):
    TYPE_CSV = 'C'
    TYPE_PARQUET = 'P'
    TYPE_CHOICES = [
        (TYPE_CSV, 'CSV'),
        (TYPE_PARQUET, 'Parquet'),
    ]
    base = models.ForeignKey(BaseScenario, on_delete=models.CASCADE, related_name='files')
    f_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=TYPE_CSV)
    base_file = models.FileField(
        upload_to='api/base_files',
    )



def default_in_one_week():
    return timezone.now().date() + timezone.timedelta(days=7)


def default_in_one_day():
    return timezone.now().date() + timezone.timedelta(days=1)

