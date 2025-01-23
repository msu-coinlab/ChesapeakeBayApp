from django.contrib import admin
from core.models import User, ScenarioInfo, GeographicArea, BaseScenario, Scenario, BmpCategory, BmpType, Agency, Bmp, BmpCostCustom, State, BmpUnit, BmpCost, Execution, Solution, LoadSrc, AnimalGrp, Sector, LandRiverSegment 

class AnimalGrpAdmin(admin.ModelAdmin):
    pass
class AgencyAdmin(admin.ModelAdmin):
    pass
class BaseScenarioAdmin(admin.ModelAdmin):
    pass
class BmpAdmin(admin.ModelAdmin):
    pass
class BmpCategoryAdmin(admin.ModelAdmin):
    pass
class BmpCostAdmin(admin.ModelAdmin):
    pass
class BmpCostCustomAdmin(admin.ModelAdmin):
    pass
class BmpTypeAdmin(admin.ModelAdmin):
    pass
class BmpUnitAdmin(admin.ModelAdmin):
    pass
class ExecutionAdmin(admin.ModelAdmin):
    pass
class GeographicAreaAdmin(admin.ModelAdmin):
    pass

class LoadSrcAdmin(admin.ModelAdmin):
    pass

class ScenarioAdmin(admin.ModelAdmin):
    pass
class ScenarioInfoAdmin(admin.ModelAdmin):
    pass
class SectorAdmin(admin.ModelAdmin):
    pass
class StatesAdmin(admin.ModelAdmin):
    pass
class UserAdmin(admin.ModelAdmin):
    pass

class LandRiverSegmentAdmin(admin.ModelAdmin):
    pass

class SolutionAdmin(admin.ModelAdmin):
    pass
admin.site.register(User, UserAdmin)
admin.site.register(ScenarioInfo, ScenarioInfoAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(BaseScenario, BaseScenarioAdmin)
admin.site.register(GeographicArea, GeographicAreaAdmin)
admin.site.register(Scenario, ScenarioAdmin)
admin.site.register(State, StatesAdmin)
admin.site.register(Agency, AgencyAdmin)
admin.site.register(AnimalGrp, AnimalGrpAdmin)
admin.site.register(BmpCategory, BmpCategoryAdmin)
admin.site.register(BmpType, BmpTypeAdmin)
admin.site.register(Bmp, BmpAdmin)
admin.site.register(BmpUnit, BmpAdmin)
admin.site.register(BmpCost, BmpCostAdmin)
admin.site.register(BmpCostCustom, BmpCostCustomAdmin)

admin.site.register(Execution, ExecutionAdmin)
admin.site.register(Solution, SolutionAdmin)
admin.site.register(LoadSrc, LoadSrcAdmin)
admin.site.register(LandRiverSegment, LandRiverSegmentAdmin)

