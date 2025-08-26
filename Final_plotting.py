import tkinter.filedialog
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import sys
from tkinter import *
from tkinter import filedialog 
import sys




# main
def main():
    
    # Finds the file paths of the user selected files.
    netCDF_file = get_file_path("NetCDF")
    csv_file = get_file_path("CSV")
    
    
    # Opens the files with the selected file paths.
    open_file = xr.open_dataset(netCDF_file)
    discrete_samples = pd.read_csv(csv_file)
    
    
    # Displays all the available stations from the CSV.
    available_stations = select_station(discrete_samples)
    # print()
    for i in range(len(available_stations)):
        print(available_stations[i] + ": " + str(i + 1))
    
    
    # User selects what station they want to look at.
    selected_station = available_stations[user_select_station(len(available_stations), 0)]
    
    
    # Finds the indexes of all the stations and then gets the casts for each segmented station change.
    station_indexes = station_finder(selected_station, discrete_samples)
    cast_indexes = stations_cast_finder(discrete_samples, station_indexes)
    
    #2015: "2015-07-10 22:00:00", "2015-07-15 15:14:00"
    #2016: "2016-07-28 17:03:00", "2016-07-28 19:23:00"
    #2022: "2022-08-22 07:23:00", "2022-08-23 18:13:00"
    #2023: "2023-08-29 09:09:00", "2023-08-29 11:29:03"
    # Easier variables for the plotting with x and y being salinity and depth respecitvely.
    x = open_file.sea_water_practical_salinity.swap_dims({"obs": "time"}).sel(time = slice("2023-08-29 09:09:00", "2023-08-29 11:29:03"))
    y = open_file.depth.swap_dims({"obs": "time"}).sel(time = slice("2023-08-29 09:09:00", "2023-08-29 11:29:03")) 
    #print(y)
    # All Color options for the plots.
    
    
    depth_target = 32.59889744
    depth_mask = (x == depth_target)  # Create a boolean mask where depth is 100
    salinity_at_depth = y.where(depth_mask, drop=True)  # Apply mask to salinity data
    # print(y)
    # Print the salinity at the target depth
    print("Salinity at depth 100:", salinity_at_depth.values)
    
    np.set_printoptions(threshold=np.inf)
    print(np.unique(x.values))
    print(np.unique(y.values))

    global plot_data_colors
    plot_data_colors = ['darkorchid','blue', 'orange', 'red' ,'green', 'cyan', 'indigo', 'magenta', 'lightcoral', 'orangered', 'burlywood', 'gold', 'yellowgreen', 'cadetblue', 'skyblue' ]
    #print( y.where(depth <= 100, other=np.nan))
    plt.scatter(x, y, color = plot_data_colors[0], alpha=0.05, label = 'Instrument Salinity')
    
    plot_data_colors.pop(0)

    # Plots all the casts of from the CTDS and Discrete Samples as points from the CSV.
    
    
    while (cast_indexes):
        if cast_indexes: 
            plotting = discrete_samples.loc[cast_indexes[0]:cast_indexes[1]]
            
            plt.scatter((plotting["CTD Salinity 1 [psu]"]), (plotting["CTD Depth [m]"]), color = plot_data_colors[0], label = discrete_samples._get_value(cast_indexes[0], 'Cast') + " Salinity 1")
            plot_data_colors.pop(0)
            
            plt.scatter((plotting["CTD Salinity 2 [psu]"]), (plotting["CTD Depth [m]"]), color = plot_data_colors[0], label = discrete_samples._get_value(cast_indexes[0], 'Cast') + " Salinity 2")
            plot_data_colors.pop(0)
            
            discrete_plotter(cast_indexes[0], cast_indexes[1], plotting)
            
            cast_indexes.pop(0)
            cast_indexes.pop(0)
    
    # Plots all the points from the instrument. 
    
    # Adds attributes to the graph and plots the graph
    plt.scatter
    plt.legend()
    plt.xlabel("Salinity [psu]") 
    plt.ylabel("Depth(m)") 
    plt.title("2015 Axial Base Shallow Profiler Depth vs. Salinity") 
    plt.gca().invert_yaxis()
    plt.show() 

#End of Main
   
   

# Returns the files name.
def get_file_path (filetype):
    fileDir = str()
    
    match filetype:
        case "NetCDF":
            fileDir = '*.nc'
        case "CSV":
            fileDir = '*.csv'
            
    root = tkinter.Tk()
    root.withdraw() #use to hide tkinter window
    fileName = filedialog.askopenfilename(title="Please Select A " + filetype +  " File", initialdir = "/Users/goopyink/Downloads//Cabled Array Data", filetypes=[('Allowed Types', fileDir)] )
    
    btn1 = Button(root, text ="Button 1") 
    btn1.pack(pady = 10) 
    btn1.after(300, btn1.destroy)
    
    return fileName


# Plots the discrete Samples from the CSV. 
def discrete_plotter(first, last, df):
    discrete_indexes = []
    for i in range(first, last):
        if df._get_value(i, 'Discrete Salinity [psu]') != -9999999:
            discrete_indexes.append(i)

    while(discrete_indexes):
        plotting = df.loc[discrete_indexes[0]]
        plt.scatter((plotting["Discrete Salinity [psu]"]), (plotting["CTD Depth [m]"]), color = plot_data_colors[0])
        discrete_indexes.pop(0)
        if len(discrete_indexes) == 1:
            plt.scatter((plotting["Discrete Salinity [psu]"]), (plotting["CTD Depth [m]"]), color = plot_data_colors[0], label = '2023 Discrete Salinity')
            plot_data_colors.pop(0)
            discrete_indexes.pop(0)


# Indexes through the file finding the cast.
# Create a list of colors to select for the graph overlay. 
# Returns cast indexes. 
# Depricated
def cast_finder(df, castName):
    try: 
        cast_index = 0
        castFound = False
        while(not castFound):
            #print(castName)
            if castName == df._get_value(cast_index, 'Cast'):
                
                try:
                    castFound = True
                    cast_indexes = [cast_index]
                    endIndexFound = False
                    
                    while(not endIndexFound):
                        final_index = cast_index
                        if castName == df._get_value(cast_index, 'Cast'):
                            final_index = cast_index
                            
                        else:
                            endIndexFound = True
                            cast_indexes.append(final_index - 1)
                            return cast_indexes
                        cast_index += 1
                except KeyError: 
                    cast_indexes.append(final_index)
                    return cast_indexes 

            else:
                cast_index += 1
    except KeyError: 
        print("\n\n-------Cast " + castName +  " not Found-------\n\n")
        return None



# Returns the station selected from the user. 
def user_select_station(available_stations_length, runCount):
    if runCount == 5:
        print("We cannot find the station you have been looking for, please try again later.")
        sys.exit()
    try:
        station_not_approved = True
        print()
        get_station_index = int(input("Enter the corresponding number to select the station you are looking for: "))
        while(station_not_approved):
            if get_station_index < available_stations_length and get_station_index > 0:
                station_not_approved = False
            else:
                get_station_index = int(input("Please Enter the corresponding Number to select the station you are looking for: "))
        
        return get_station_index - 1
        
    except ValueError:
        print()
        print("Please enter an integer value such as 1")
        return user_select_station(available_stations_length, runCount + 1)




# returns the indexes of all casts in a station
def stations_cast_finder(df, station_indexes = [] ):
    try: 

        cast_indexes = []

        castName = df._get_value(station_indexes[0], 'Cast')
        i = station_indexes[0]
        final_index = station_indexes[len(station_indexes) - 1]
        current = 0
        
        while(i < final_index):
            if i < final_index: 
                if i < station_indexes[current] or i > station_indexes[current + 1] :
                    current += 2        
                    i = station_indexes[current]
                    castName = df._get_value(station_indexes[current], 'Cast')

                if castName == df._get_value(i, 'Cast') and df._get_value(i, 'Cast')[0:3] == "CTD" and df._get_value(i,'CTD Salinity 2 [psu]' ) != -9999999:

                    if not cast_indexes or cast_indexes[len(cast_indexes) - 1] + 1 != i and len(cast_indexes) % 2 != 0:
                        cast_indexes.append(i)
                    else: 
                        if len(cast_indexes) % 2 != 0 and len(cast_indexes) > 1:
                            cast_indexes.pop(len(cast_indexes) - 1)
                        cast_indexes.append(i)
                        
                elif df._get_value(i, 'Cast')[0:3] == "CTD" and df._get_value(i,'CTD Salinity 2 [psu]' ) != -9999999:    
                    cast_indexes.append(i)
                    castName = df._get_value(i, 'Cast')
                    
            i += 1
            if i == final_index :
                if df._get_value(i, 'Cast')[0:3] == "CTD" and df._get_value(i,'CTD Salinity 2 [psu]' ) != -9999999:
                    cast_indexes.pop(len(cast_indexes) - 1)
                    cast_indexes.append(i)

                cast_indexes.pop(1)

                return cast_indexes


    except KeyError or TypeError: 
        print("\n\n-------Station " + castName +  " not Found-------\n\n")
        return None

# Locates all stations within csv, returns options to the user to select a station. 
def station_finder(stationName, df, i=0, stationFound=False):
    try: 
        row_Count = len(df.index)
        station_indexes = []
        while(i < row_Count):
            if stationName == df._get_value(i, 'Station'):
                if not station_indexes:
                    station_indexes.append(i)

                elif station_indexes[len(station_indexes) - 1] + 1 != i and len(station_indexes) % 2 != 0:

                    station_indexes.append(i)
                else: 
                    if len(station_indexes) % 2 != 0 and len(station_indexes) > 1:
                        station_indexes.pop(len(station_indexes) - 1)
                    station_indexes.append(i)

                if i == row_Count - 1:
                    station_indexes.append(i)
                    station_indexes.pop(1)
                    return station_indexes
                i += 1
            else:
                
                if i == row_Count - 1:
                    if not station_indexes:
                        print("\n\n-------Station " + stationName +  " not Found-------\n\n")
                        return None
                    station_indexes.pop(1)
                    return station_indexes
               
                i += 1

    except KeyError: 
        print("\n\n-------Station " + stationName +  " not Found-------\n\n")
        return None


# Returns the list of all unique stations. 
def select_station(df):
    df.sort_values(['Station'])
    row_count = len(df.index)
    station_options = []
    prev_station = None
    for i in range(row_count): 
        if df._get_value(i, 'Station') != prev_station:
            station_options.append(df._get_value(i, 'Station'))
            prev_station = df._get_value(i, 'Station')
    
    return station_options
    
    

# Depricated     
def Reverse(lst):
   new_lst = lst[::-1]
   return new_lst


# Runs main 
if __name__ == '__main__':
    main()
