import datetime
import pandas as pd
import os
from zipfile import ZipFile

import stefpeaks.conversion_factors
import stefpeaks.t2min

cf = stefpeaks.conversion_factors.cf
t2min_tz = stefpeaks.t2min.t2min_tz
t2min_cf = stefpeaks.t2min.t2min_cf

workoutFolder = 'workouts'

def calculateTSS(row):
    wt = row['WorkoutType']
    if not row['TSS']:
        tss = row['TSS']
    else:
        tss = row['TSS']
    if wt == 'Strength':
        return tss * cf['strength'] 
    if wt == 'Day Off':
        return tss
    if wt == 'Rowing':
        if row['DistanceInMeters'] > 0:
            return tss * cf['rowing']
        else:
            return tss * cf['indoor rowing']
    if wt == 'Bike':
        if row['DistanceInMeters'] > 0:
            return tss * cf['cycling']
        else:
            return tss * cf['indoor cycling']
    if wt == 'Other':
        if row['Title'] == "Alpine Skiing":
            return tss * cf['alpine skiing']
        else:
            return tss * cf['other']
    if wt == 'Walk':
        return tss * cf['hiking']
    return tss

def baseT2min(row):
    t2min = 0
    
    t2tz = list(t2min_tz.values())
    zones = [ f"HRZone{hrz}Minutes" for hrz in list(range(1,6))]
    
    for i, zone in enumerate(zones):
        t2min = t2min + row[zone] * t2tz[i]
    
    return t2min

def calculateT2min(row):

    t2min =  baseT2min(row)
    wt = row['WorkoutType']

    if wt == 'Strength':
        return row['TSS'] * t2min_cf['strength'] # take the TSS for now!
    if wt == 'Day Off':
        return t2min
    if wt == 'Rowing':
        if row['DistanceInMeters'] > 0:
            return t2min * t2min_cf['rowing']
        else:
            return t2min * t2min_cf['indoor rowing']
    if wt == 'Bike':
        if row['DistanceInMeters'] > 0:
            return t2min * t2min_cf['cycling']
        else:
            return t2min * t2min_cf['indoor cycling']
    if wt == 'Other':
        if row['Title'] == "Alpine Skiing":
            return t2min * t2min_cf['alpine skiing']
        else:
            return t2min * t2min_cf['other']
    if wt == 'Walk':
        return t2min * t2min_cf['hiking']
    return t2min


def cleanUpCsv():
    # Unzip all workout files and give them sensible names instead of workouts.csv
    workoutFolder = 'workouts'
    workoutFiles = os.listdir(workoutFolder)
    for file in workoutFiles:
        if file == '.gitkeep':
            continue
        if file[-3:] == 'zip':
            name = file[:-3]
            print(f"Found {file}.zip, unzipping csv (don't do this manually!)")
            with ZipFile(os.path.join(workoutFolder,file), 'r') as f:
                f.extractall(workoutFolder)
            os.rename(os.path.join(workoutFolder,'workouts.csv'), os.path.join(workoutFolder,name + 'csv'))
            os.remove(os.path.join(workoutFolder, file))

def getNames():
    cleanUpCsv()
    workoutFolder = 'workouts'
    workoutFiles = os.listdir(workoutFolder)
    def lastname(e):
        return e.split(' ')[1]
    names = []
    for file in workoutFiles:
        if file == '.gitkeep':
            continue
        split = file.split('-')
        name = f'{split[2]} {split[1]}'
        if name not in names:
            names.append(name)
    names.sort(key=lastname)
    return names

def summarizeDay(day):
    RowHours = 0
    PlannedRowHours = 0
    BikeHours = 0
    PlannedBikeHours = 0
    OtherHours = 0
    StrengthHours =0
    for i, w in day.iterrows():
        if w['WorkoutType'] == "Rowing":
            if not pd.isnull(w['PlannedDuration']):
                PlannedRowHours = PlannedRowHours + w['PlannedDuration']
            if not pd.isnull(w['TimeTotalInHours']):
                RowHours = RowHours + w['TimeTotalInHours']
        if w['WorkoutType'] == "Bike":
            if not pd.isnull(w['PlannedDuration']):
                PlannedBikeHours = PlannedBikeHours + w['PlannedDuration']
            if not pd.isnull(w['TimeTotalInHours']):
                BikeHours = BikeHours + w['TimeTotalInHours']
        if w['WorkoutType'] == "Strength":
            if not pd.isnull(w['PlannedDuration']):
                StrengthHours = StrengthHours + w['PlannedDuration']
        else:
            if not pd.isnull(w['TimeTotalInHours']):
                OtherHours = OtherHours + w['TimeTotalInHours']

    return (RowHours, PlannedRowHours, BikeHours, PlannedBikeHours, OtherHours, StrengthHours)

def importWorkout(name: str):

    name = name.title()
    workoutFiles = os.listdir(workoutFolder)
    selectedFiles = []
    for file in workoutFiles:
        if all(x in file for x in name.split(' ')):
            selectedFiles.append(file)

    if selectedFiles == []:
        print('No files found!')
    print(f'Found the following files:')
    for file in selectedFiles:
        print(file)


    print('Loading all files and building dataframes...')
    workoutsDataFrame = pd.DataFrame()
    #append all files together
    for file in selectedFiles:
                df_temp = pd.read_csv(os.path.join(workoutFolder, file))
                workoutsDataFrame = pd.concat([workoutsDataFrame, df_temp], ignore_index=True)
    workoutsDataFrame = workoutsDataFrame.drop_duplicates()
    wf = workoutsDataFrame

    # Some trainings are marked with TSS while they have not been completed.
    # This leads to duplicate entries (predicted and actual TSS on the same day)
    wf.loc[(wf['TSS'] > 0) & (wf['TimeTotalInHours'] < 0.01), "TSS"] = 0

    # Weightlifting TSS is severely underestimated by HR data, so overwrite with a prediction
    wf.loc[(wf['WorkoutType'] == 'Strength') & (wf['PlannedDuration'] > 0.1),"TSS"] = 50
    wf.loc[(wf['WorkoutType'] == 'Strength') & (wf['PlannedDuration'] > 0.9),"TSS"] = 100
    wf.loc[(wf['WorkoutType'] == 'Strength') & (wf['PlannedDuration'] > 1.1),"TSS"] = 150


    # Make a new dataframe which is one row per day, instead of per workout
    workoutDays = []
    ctss = [] # Converted TSS (with conversion factor)
    t2min = []
    for i, row in workoutsDataFrame.iterrows():
        workoutDays.append(datetime.datetime.strptime(row['WorkoutDay'],'%Y-%m-%d')) 
        ctss.append(calculateTSS(row))
        t2min.append(calculateT2min(row))
    workoutsDataFrame['WorkoutDatetime'] = workoutDays
    workoutsDataFrame['CTSS'] = ctss
    workoutsDataFrame['T2MIN'] = t2min


    workoutsDataFrame= workoutsDataFrame.sort_values(by='WorkoutDatetime', ascending=False)
    wf = wf.sort_values(by='WorkoutDatetime', ascending=False)

    sdate = workoutsDataFrame['WorkoutDay'].min()
    edate = workoutsDataFrame['WorkoutDay'].max()

    daysDataFrame = pd.DatetimeIndex.to_frame(pd.date_range(sdate,edate)) # Create a new dataframe based on days


    TSSDataFrame = daysDataFrame.copy()
    TSS = []
    CTSS = []
    T2MIN = []
    RowHours = []
    PlannedRowHours = []
    BikeHours = []
    PlannedBikeHours = []
    OtherHours = []
    StrengthHours =[]


    # Some trickery, select all days from the wf and su values
    for i, row in TSSDataFrame.iterrows():
        tss = workoutsDataFrame[workoutsDataFrame['WorkoutDay'] == i.strftime('%Y-%m-%d')]['TSS'].sum()
        ctss = workoutsDataFrame[workoutsDataFrame['WorkoutDay'] == i.strftime('%Y-%m-%d')]['CTSS'].sum()
        t2min = workoutsDataFrame[workoutsDataFrame['WorkoutDay'] == i.strftime('%Y-%m-%d')]['T2MIN'].sum()

        RH, PRH, BH, PBH, OH, SH = summarizeDay(wf[wf['WorkoutDay'] == i.strftime('%Y-%m-%d')])
        RowHours.append(RH)
        PlannedRowHours.append(PRH)
        BikeHours.append(BH)
        PlannedBikeHours.append(PBH)
        OtherHours.append(OH)
        StrengthHours.append(SH)

        TSS.append(tss)
        CTSS.append(ctss)
        T2MIN.append(t2min)

    TSSDataFrame['TSS'] = TSS
    TSSDataFrame['CTL'] = TSSDataFrame["TSS"].rolling(pd.Timedelta(42,"D")).mean()
    TSSDataFrame['ATL'] = TSSDataFrame["TSS"].rolling(pd.Timedelta(7,"D")).mean()
    TSSDataFrame['TSB'] = TSSDataFrame['CTL'] - TSSDataFrame['ATL']
    TSSDataFrame['CTSS'] = CTSS
    TSSDataFrame['CCTL'] = TSSDataFrame["CTSS"].rolling(pd.Timedelta(42,"D")).mean()
    TSSDataFrame['CATL'] = TSSDataFrame["CTSS"].rolling(pd.Timedelta(7,"D")).mean()
    TSSDataFrame['CTSB'] = TSSDataFrame['CCTL'] - TSSDataFrame['CATL']
    TSSDataFrame['T2MIN'] = T2MIN
    TSSDataFrame['T2CTL'] = TSSDataFrame["T2MIN"].rolling(pd.Timedelta(42,"D")).mean()
    TSSDataFrame['T2ATL'] = TSSDataFrame["T2MIN"].rolling(pd.Timedelta(7,"D")).mean()
    TSSDataFrame['T2TSB'] = TSSDataFrame['T2CTL'] - TSSDataFrame['T2ATL']

    TSSDataFrame['RowHours'] = RowHours
    TSSDataFrame['PlannedRowHours'] = PlannedRowHours
    TSSDataFrame['BikeHours'] = BikeHours
    TSSDataFrame['PlannedBikeHours'] = PlannedBikeHours
    TSSDataFrame['OtherHours'] = OtherHours
    TSSDataFrame['StrengthHours'] = StrengthHours

    return workoutsDataFrame, TSSDataFrame