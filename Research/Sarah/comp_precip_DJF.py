# -*- coding: utf-8 -*-
# ENSO composite analysis: CMAP Precip

import matplotlib.pyplot as pyplot
from mpl_toolkits.basemap import Basemap 
import numpy as np
import pandas as pd # http://pandas.pydata.org/
from netCDF4 import Dataset, num2date
from scipy.stats import ttest_ind

#close existing plot windows
pyplot.close("all")

#read nino3.4 data from a CSV (comma-separated) file into DataFrame
nino34=pd.read_csv("/data/zhuowang/a/zhuowang/ATMS491/Data/detrend.nino34.ascii.txt", sep="\s+")
yr=nino34.YR
mon=nino34.MON
anom=nino34.TOTAL

#find indices of Dec in 1979-2008
D0=np.where((mon == 12) & (yr >= 1979) & (yr <= 2008))[0] # dec(0)
nyr=len(D0) 

#calculate DJF mean
DJF0=np.zeros(nyr)
for i in range(nyr):
    DJF0[i]=np.mean(anom[D0[i]:D0[i]+3])    

#standard deviation and selection
std=np.std(DJF0)
xm=np.mean(DJF0)
#Normalize the time series and save in a new array "DJF"
DJF=np.zeros(nyr)
DJF=(DJF0-xm)/std

pos=np.where(DJF >=  1.0)[0]
neg=np.where(DJF <= -1.0)[0]

#pos and neg DJF that pass test
yr_pos=yr[D0[pos]]
print("Positive:")
print(yr_pos)
yr_neg=yr[D0[neg]]
print("Negative:")
print(yr_neg)

#CMAP precipitation: monthly (std)
#You can use "print ncFid.variables" to check the variables
ncFid = Dataset ("/data/zhuowang/b/zhuowang/Data/GPCP/precip.mon.mean.nc" , mode = "r")
lon = ncFid.variables[ "lon" ][:]
lat = ncFid.variables[ "lat" ][:]
precip = ncFid.variables[ "precip" ][:]

#dim info
precip_dim=precip.shape
nlat = len(lat)
nlon = len(lon)

#convert time to get YYYY and MM
time = ncFid.variables[ "time" ][:]
unit_time = ncFid.variables[ "time" ].units # get unit  "days since ..."
datevar=num2date(time,units = unit_time,calendar = "standard")

nlen=len(time)
yr_precip=np.zeros(nlen)
mon_precip=np.zeros(nlen)

#Extract the year and month information from datevar
#You can print out an element of datevar to see what date info is generated
for i in range(nlen):
    yr_precip[i]=datevar[i].year
    mon_precip[i]=datevar[i].month

#Values MUST be kept the same as in D0
D1=np.where((mon_precip == 12) & (yr_precip >= 1979) & (yr_precip <= 2008))[0] 

#composite members: precip_dim[1] and precip_dim[2]) are lat and lon, respectively
group_pos=np.zeros((len(pos),precip_dim[1],precip_dim[2]))
group_neg=np.zeros((len(neg),precip_dim[1],precip_dim[2]))

#ONLY works when D0 and D1 represent Dec in the same range
for i in range(len(pos)): 
    dec=D1[pos[i]]
    group_pos[i,:,:]=np.mean(precip[dec:dec+3,:,:],axis=0)

for i in range(len(neg)):
    dec=D1[neg[i]]
    group_neg[i,:,:]=np.mean(precip[dec:dec+3,:,:],axis=0)

#composite mean and difference
comp_pos=np.mean(group_pos, axis=0)
comp_neg=np.mean(group_neg, axis=0)
comp_diff=comp_pos-comp_neg

#Student's T test
t, p = ttest_ind(group_pos, group_neg, axis = 0, equal_var = False)

#plotting
fig = pyplot.figure ()
ax = fig.add_axes ([0.05 ,0.05 ,0.9 ,0.85])
m = Basemap ( projection = "cyl", lon_0=180)
m.drawcoastlines ( linewidth =1.25, color="gray")
m.drawparallels ( np.arange ( -80 ,81 ,20) , labels = [1 ,1 ,0 ,0])
m.drawmeridians ( np.arange ( -180 ,180 ,60) , labels = [0 ,0 ,0 ,1])

#comp_diff
im = m.pcolormesh( lon, lat, comp_diff, cmap = pyplot.cm.jet, vmin=-10, vmax=10)
#sinigicance level
im1 = pyplot.contour(lon, lat, p, [0.05, 2], linewidths=1, colors='k', linestyles="solid")

cb = m.colorbar(im,"bottom", size="5%", pad="10%")
pyplot.title ("Composite Difference: CMAP Precip. (DJF)")
fmt="png"
pyplot.savefig("precip_comp_diff_DJF."+fmt, format=fmt, \
               bbox_inches='tight')

pyplot.show ()
