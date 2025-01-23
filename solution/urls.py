from django.urls import path
from . import views

urlpatterns = [
        path('list/<int:id>/', views.ListSolutionsHTMX.as_view(), name='list_solutions'),
        path('plot/<int:id>/', views.PlotSolutions.as_view(), name='plot_solutions'),
        #path('update/<int:pk>/', views.UpdateSolution.as_view(), name='update_solution'),
        path('view/<int:id>/', views.ViewSolution.as_view(), name='view_solution'),
        path('duplicate/<int:id>/', views.DuplicateSolution.as_view(), name='duplicate_solution'),
        path('download/<int:id>/', views.DownloadSolution.as_view(), name='download_solution'),
        path('update/<int:id>/', views.UpdateSolution.as_view(), name='update_solution'),
        path('view_by_sector/<int:id>/', views.ViewSolutionBySector.as_view(), name='view_by_sector'),
        path('scatter-plot/', views.scatter_plot, name='scatter-plot'),
        path('scatter-plot2/', views.scatter_plot2, name='scatter-plot2'),
        path('scatter-plot3/', views.scatter_plot3, name='scatter-plot3'),
        path('htmx-random-points/', views.htmx_random_points, name='htmx-random-points'),
        path('scenario-data/', views.get_scenario_data, name='scenario_data'),
        path('update_load_options/', views.get_scenario_data, name='update_load_options'),
        path('generate_land_file/', views.generate_land_file, name='generate_land_file'),
        path('generate_animal_file/', views.generate_animal_file, name='generate_animal_file'),
        path('generate_manure_file/', views.generate_manure_file, name='generate_manure_file'),
        path('temp-file/<int:solution_id>/', views.serve_temp_file, name='serve_temp_file'),
        path('temp-animal-file/<int:solution_id>/', views.serve_temp_animal_file, name='serve_temp_animal_file'),
        path('temp-manure-file/<int:solution_id>/', views.serve_temp_manure_file, name='serve_temp_manure_file'),

        path('chat/', views.ChatResponse, name='chat_response'),
]

