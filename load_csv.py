import datetime
import pandas as pd
from bokeh.plotting import figure, output_file, save, show
from bokeh.models import ColumnDataSource, HoverTool, LinearAxis, Range1d, TabPanel, Tabs, DataTable, DateFormatter, TableColumn
import os
from zipfile import ZipFile
from stefpeaks.importWorkout import *

print("Please input a name or number:")
names = getNames()
for i,n in enumerate(names):
    print(f'{i+1}: {n}')
name = ' '
while name == ' ':
    inp = input()
    if inp.isnumeric():
        name = names[int(inp)-1]
    elif isinstance(inp, str):
        name = inp
    else:
        print("input something valid")
print(f"Analyzing data for: {name}")

workoutsDataFrame, TSSDataFrame = importWorkout(name)
wf = workoutsDataFrame

df = TSSDataFrame
source = ColumnDataSource(
    data = {
        'index': df.index.values,
        'TSS': df['TSS'].values,
        'CTL': df['CTL'].values,
        'ATL': df['ATL'].values,
        'TSB': df['TSB'].values,
        'CTSS': df['CTSS'].values,
        'CCTL': df['CCTL'].values,
        'CATL': df['CATL'].values,
        'CTSB': df['CTSB'].values,
    }
)

dfw = df.groupby([pd.Grouper(freq='W')])

tools = ['xwheel_zoom', 'xpan', 'save']
p1 = figure(sizing_mode="stretch_both", x_axis_type='datetime', y_range=(0, 250), tools=tools, active_scroll='xwheel_zoom')
p1.line(source=source, x='index', y='CTL', legend_label='Fitness - CTL', color='royalblue', width=2)
p1.varea(source=source, x='index', y1=0, legend_label='Fitness - CTL', y2="CTL", alpha=0.1, fill_color='royalblue')
p1.line(source=source, x='index', y='ATL', legend_label='Fatigue - ATL', color='hotpink', width=2)
p1.scatter(x=workoutsDataFrame['WorkoutDatetime'].values, y=workoutsDataFrame['TSS'].values, color='red', legend_label='Training Stress Score - TSS')
#p1.vbar(x=dfw['TSS'].sum().index, top=dfw['TSS'].sum().values/6, bottom=0)


p2 = figure(sizing_mode="stretch_both", x_axis_type='datetime', y_range=p1.y_range, x_range=p1.x_range, tools=tools, active_scroll='xwheel_zoom')
p2.line(source=source, x='index', y='CCTL', legend_label='Fitness - CTL', color='royalblue', width=2)
p2.varea(source=source, x='index', y1=0, legend_label='Fitness - CTL', y2="CCTL", alpha=0.1, fill_color='royalblue')
p2.line(source=source, x='index', y='CATL', legend_label='Fatigue - ATL', color='hotpink', width=2)
p2.scatter(x=workoutsDataFrame['WorkoutDatetime'].values, y=workoutsDataFrame['TSS'].values, color='red', legend_label='Training Stress Score modified - TSS')

ax2 = LinearAxis(y_range_name="TSB", axis_label="Form")
ax2.axis_label_text_color ="gold"
ax22 = LinearAxis(y_range_name="CTSB", axis_label="Form")
ax22.axis_label_text_color ="gold"
p1.add_layout(ax2, 'right')
p2.add_layout(ax22, 'right')

p1.extra_y_ranges['TSB'] = Range1d(-100, 100)
p1.line(source=source, x='index', y='TSB', legend_label='Form - TSB', color='gold', width=2, y_range_name="TSB")
p2.extra_y_ranges['CTSB'] = Range1d(-100, 100)
p2.line(source=source, x='index', y='CTSB', legend_label='Form - TSB', color='gold', width=2, y_range_name="CTSB")

p1.legend.location = "top_left"
p1.legend.click_policy="hide"
p2.legend.location = "top_left"
p2.legend.click_policy="hide"

hover = HoverTool(tooltips=[('Date', '@index{%F}'), ('Fitness - CTL', '@CTL'), ('Fatigue - ATL', '@ATL'), ('Form - TSB', '@TSB')],formatters={'@index': 'datetime'}) 
p1.add_tools(hover) 
p2.add_tools(hover) 

# Table for all the workouts
wtableData = dict(
        WorkoutDays = wf['WorkoutDay'].values,
        Titles = wf['Title'].values,
        Types = wf['WorkoutType'].values,
        PlannedDurations = wf['PlannedDuration'].values,
        Distances = wf['PlannedDistanceInMeters'].values,
        Durations = wf['TimeTotalInHours'].values,
        TSSs = wf['TSS'].values,
        CTSSs = wf['CTSS'].values,
    )
wtableSource = ColumnDataSource(wtableData)

wcolumns = [
        TableColumn(field="WorkoutDays", title="Date", formatter=DateFormatter()),
        TableColumn(field="Titles", title="Title"),
        TableColumn(field="Type", title="Type"),
        TableColumn(field="PlannedDurations", title="Planned Duration"),
        TableColumn(field="Distances", title="Planned Distance"),
        TableColumn(field="Durations", title="Duration (h)"),
        TableColumn(field="TSSs", title="TSS"),
        TableColumn(field="CTSSs", title="CTSS"),
    ]
wdata_table = DataTable(source=wtableSource, columns=wcolumns, sizing_mode="stretch_both")

# Table for all the days
dtableData = dict(
        
        Days = df.index.values,
        RowHours = df['RowHours'].values,
        PlannedRowHours = df['PlannedRowHours'].values,
        BikeHours = df['BikeHours'].values,
        PlannedBikeHours = df['PlannedBikeHours'].values,
        OtherHours = df['OtherHours'].values,
        StrengthHours = df['StrengthHours'].values,
    )
dtableSource = ColumnDataSource(dtableData)

dcolumns = [
        TableColumn(field="Days", title="Date", formatter=DateFormatter()),
        TableColumn(field="RowHours", title="Time Rowed (h)"),
        TableColumn(field="PlannedRowHours", title="Planned Row Time (h)"),
        TableColumn(field="BikeHours", title="Time Biked (h)"),
        TableColumn(field="PlannedBikeHours", title="Planned Bike Time (h)"),
        TableColumn(field="StrengthHours", title="Strength Training Time"),
        TableColumn(field="OtherHours", title="Other Training Time(h)"),
    ]
ddata_table = DataTable(source=dtableSource, columns=dcolumns, sizing_mode="stretch_both")

tab1 = TabPanel(child=p1, title="TSS")
tab2 = TabPanel(child=p2, title="TSS Modified with conversion factor")
tab3 = TabPanel(child=wdata_table, title="Workout Table")
tab4 = TabPanel(child=ddata_table, title="Day Table")

t = Tabs(tabs=[tab1, tab2, tab3, tab4], sizing_mode="stretch_both")

fileName=f"TSS_plot_{name}.html"
plotFolder = 'plots'
plotPath = os.path.join(plotFolder, fileName)
output_file(filename=plotPath, title=f"{name} - Stef Peaks")
show(t)
save(t)
print('Showing plot in browser')
print(f'Storing plot at: {plotPath}')