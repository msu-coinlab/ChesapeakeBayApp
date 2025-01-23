# bokeh serve multiplotall.py --port 5007 --allow-websocket-origin=127.0.0.1:8080 --allow-websocket-origin=192.168.1.3:8080 --allow-websocket-origin=cast.toscano.mx --allow-websocket-origin=localhost:5007
import pandas as pd
from bokeh.models import LabelSet, ColumnDataSource, Slider, Select
from bokeh.plotting import figure
from bokeh.layouts import gridplot, column, row
from bokeh.io import curdoc
from mcdm import vikor, topsis

class MyMCDM:
    def __init__(self, df):
        self.method = 'VIKOR'
        self.y_axis_method = 'Percentage'
        self.df = df
        self.axis_label = self._init_axis_labels()
        self.select_options = self._init_select_options()
        self.source = ColumnDataSource(df)
        self.selected_options = self.select_options[self.y_axis_method]
        self.grid_layout = self._create_grid_layout()
        self.sliders = self._init_sliders()
        self.dropdowns = self._init_dropdowns()
        self._setup_callbacks()
        self._add_layouts_to_document()

    def _init_axis_labels(self):
        return {
            'Cost': 'Cost (US Dollars)',
            'NLoadEos': 'Nitrogen Loads (lbs)',
            'PLoadEos': 'Phosphorous Loads (lbs)',
            'SLoadEos': 'Sediments Loads (lbs)',
            'NLoadEosP': 'Nitrogen Percentage Reduction (%)',
            'PLoadEosP': 'Phosphorous Percentage Reduction (%)',
            'SLoadEosP': 'Sediments Percentage Reduction (%)'
        }

    def _init_select_options(self):
        options = {
            'Percentage': [
                ['Cost', 'NLoadEosP'], ['Cost', 'PLoadEosP'], ['Cost', 'SLoadEosP'],
                ['NLoadEosP', 'PLoadEosP'], ['NLoadEosP', 'SLoadEosP'], ['PLoadEosP', 'SLoadEosP']
            ],
            'Lbs': [
                ['Cost', 'NLoadEos'], ['Cost', 'PLoadEos'], ['Cost', 'SLoadEos'],
                ['NLoadEos', 'PLoadEos'], ['NLoadEos', 'SLoadEos'], ['PLoadEos', 'SLoadEos']
            ]
        }
        return options

    def _create_grid_layout(self):
        plots = self.create_plots()
        grid = [plots[i:i+3] for i in range(0, len(plots), 3)]
        return column(gridplot(grid))

    def _init_sliders(self):
        sliders = {
            'cost': Slider(title="Cost Weight", value=0.5, start=0, end=1, step=0.01),
            'nitrogen': Slider(title="Nitrogen Weight", value=0.5, start=0, end=1, step=0.01),
            'phosphorous': Slider(title="Phosphorous Weight", value=0.5, start=0, end=1, step=0.01),
            'sediments': Slider(title="Sediments Weight", value=0.5, start=0, end=1, step=0.01)
        }
        return sliders

    def _init_dropdowns(self):
        dropdowns = {
            'method': Select(title="MCDM Method", value="VIKOR", options=["VIKOR", "TOPSIS"]),
            'y_axis_method': Select(title="Display", value="Percentage", options=["Percentage", "Lbs"])
        }
        return dropdowns

    def _setup_callbacks(self):
        for slider in self.sliders.values():
            slider.on_change("value", self.update_data)
        self.dropdowns['method'].on_change('value', self.update_method)
        self.dropdowns['y_axis_method'].on_change('value', self.update_y_axis_method)

    def _add_layouts_to_document(self):
        slider_layout = row(self.dropdowns['y_axis_method'], self.dropdowns['method'], *self.sliders.values())
        curdoc().add_root(slider_layout)
        curdoc().add_root(self.grid_layout)

    def update_method(self, attr, old, new):
        self.method = new

    # Modify the update_y_axis_method function
    def update_y_axis_method(self, attr, old, new):
        self.y_axis_method = self.dropdowns['y_axis_method'].value
        
        # Choose the options based on the new dropdown value
        self.selected_options = self.select_options[new]
        
        # Use the helper function to get the updated plots
        updated_plots = self.create_plots()
        
        # Update the layout with the new plots
        grid = []
        for i in range(0, len(updated_plots), 3):
            grid.append([updated_plots[i], updated_plots[i + 1], updated_plots[i + 2]])
    
        self.grid_layout.children[0] = gridplot(grid)
    
    # Function to update the DataFrame based on slider values
    def update_data(self, attr, old, new):
        Cost = self.sliders['cost'].value
        Nitrogen = self.sliders['nitrogen'].value
        Phosphorous = self.sliders['phosphorous'].value 
        Sediments = self.sliders['sediments'].value
        weights = [Cost, Nitrogen, Phosphorous, Sediments]
        benefit_criteria =  [False, False, False, False]
    
        df_values = self.df[['Cost','NLoadEos','PLoadEos','SLoadEos']].values
        if self.method == 'TOPSIS':
            benefit_criteria =  [True, True, True, True]
            ranking_order = topsis(df_values, weights, benefit_criteria)
            idx = self.indices_to_rankings(ranking_order)
            self.df['ranking'] = idx
            self.df['color'] = ['red' if idx[i] == 0 else 'blue' for i in range(len(ranking_order))]
        elif self.method == 'VIKOR': 
            v = 0.0
            compromise_solutions = vikor(df_values, weights, v)
            self.df['color'] = ['red' if i in compromise_solutions else 'blue' for i in range(len(self.df))]
            #df['set'] = ['Selected' if i in compromise_solutions else 'PF' for i in range(len(df))]
            self.df['set'] = self.df['color'].map({'blue': 'PF', 'red': 'Selected'})
            self.df['ranking'] = ' ' 
    
        # Update the data source with the new DataFrame
        self.source.data = self.df

    def create_plots(self):
        plots_temp = []
        for x_col, y_col in self.selected_options:
            plot = figure(title=f"{x_col} vs {y_col}")
            
            plot.circle(x=x_col, y=y_col, source=self.source, 
                        color='color', 
                        legend_field='set', size=12)
    
            labels = LabelSet(x=x_col, y=y_col, text='ranking', level='glyph',
                              x_offset=5, y_offset=5, source=self.source)
            plot.add_layout(labels)
            plot.legend.location = "bottom_right"
            
            plot.xaxis.axis_label = self.axis_label[x_col]
            plot.yaxis.axis_label = self.axis_label[y_col]
            # For axis labels
            plot.xaxis.axis_label_text_font_size = "16pt"
            plot.yaxis.axis_label_text_font_size = "16pt"
            
            # For axis tick labels
            plot.xaxis.major_label_text_font_size = "12pt"
            plot.yaxis.major_label_text_font_size = "12pt"
            
            # For plot title
            plot.title.text_font_size = "18pt"
            
            # If you have a legend
            plot.legend.label_text_font_size = "14pt"
    
            plots_temp.append(plot)
    

        return plots_temp

    def indices_to_rankings(self, indices):
        indices_list = indices.tolist()  # Convert numpy array to list
        return [indices_list.index(i) for i in range(len(indices_list))]

def read_uuid(file_path):
    uuid = ''
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Process each line (UUID) here
                uuid = line.strip()
                print(f"UUID: {uuid}")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return uuid

def read_pf(uuid):
    init_load_df = pd.read_csv(f'{uuid}/initial_loads2.csv')
    df = pd.read_csv(f'{uuid}/output.csv')
    
    
    df['color'] = 'blue' # default color
    df['ranking'] = ' ' 
    df['set'] = df['color'].map({'blue': 'PF', 'red': 'Selected'})
    for col in ['NLoadEos','PLoadEos','SLoadEos']:
        df[col+'P'] = (init_load_df[col].values[0] - df[col]) / init_load_df[col].values[0] * 100
    return df

# Function to extract query parameters
def get_query_parameters():
    args = curdoc().session_context.request.arguments
    return {key: value[0].decode() for key, value in args.items()}

# Main entry point of the Bokeh application
def main():
    params = get_query_parameters()
    uuid = params.get('uuid', 'default_value')
    print(f"UUID: {uuid}")
    uuid = read_uuid('which2.txt')
    df = read_pf(uuid)
    app = MyMCDM(df)

main()
