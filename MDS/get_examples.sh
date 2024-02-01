#! /bin/bash

#examples of copernicusmarine get 
#Sat CHL NRT
copernicusmarine get -nd  -o $PWD/ -s files  -i cmems_obs-oc_med_bgc-plankton_nrt_l3-multi-1km_P1D --force-download --show-outputnames  --force-dataset-version 202211 --overwrite


#Sat CHL DT
copernicusmarine get -nd  -o $PWD/ -s files  -i cmems_obs-oc_med_bgc-plankton_my_l3-multi-1km_P1D  --force-download --show-outputnames  --overwrite --filter '*202402*'




#examples of copernicusmarine subset
copernicusmarine subset --request-file example.json