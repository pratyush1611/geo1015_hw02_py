#-- my_code_hw02.py
#-- Assignment 02 GEO1015.2020
#-- [YOUR NAME] 
#-- [YOUR STUDENT NUMBER] 
#-- [YOUR NAME] 
#-- [YOUR STUDENT NUMBER] 
#%%
import sys
import math
import numpy
import rasterio
from rasterio import features
#%%


def output_viewshed(d, viewpoints, maxdistance, output_file):
    """
    !!! TO BE COMPLETED !!!
     
    Function that writes the output raster
     
    Input:
        d:            the input datasets (rasterio format)  
        viewpoints:   a list of the viewpoints (x, y, height)
        maxdistance:  max distance one can see
        output_file:  path of the file to write as output
        
    Output:
        none (but output GeoTIFF file written to 'output-file')
    """  
    
    # [this code can and should be removed/modified/reutilised]
    # [it's just there to help you]
    # d is the rasterio file
    #-- numpy of input
    npi  = d.read(1)
    #-- fetch the 1st viewpoint
    v = viewpoints[0]
    #-- index of this point in the numpy raster
    vrow_center, vcol_center = d.index(v[0], v[1])

    vrow_bottom,  vcol_left = d.index(v[0]-maxdistance, v[1]-maxdistance)
    vrow_top, vcol_right    = d.index(v[0]+maxdistance, v[1]+maxdistance)

    #-- the results of the viewshed in npvs, all values=0
    npvs = numpy.zeros(d.shape, dtype=numpy.int8)
    # npvs = numpy.zeros(d.shape , dtype=bool)
    #-- put that pixel with value of height
    npvs[vrow_center , vcol_center] = v[2]
    for i,(row_orig , row) in enumerate(zip(npi,npvs)):
        for j,(val_orig,val) in enumerate(zip( row_orig , row)):
            if i<vrow_top or i>vrow_bottom:
                continue
            elif j<vcol_left or j>vcol_right:
                continue
            # do circle here #actually a square for now
            npvs[i,j] = npi[i,j]

#   
# 
    # -- write this to disk

    with rasterio.open(output_file, 'w', 

                       driver='GTiff', 
                       height=npi.shape[0],
                       width=npi.shape[1], 
                       count=1, 
                       dtype=rasterio.uint8,
                       crs=d.crs, 
                       transform=d.transform) as dst:
        dst.write(npvs.astype(rasterio.uint8), 1)

    print("Viewshed file written to '%s'" % output_file)
#%%


def Bresenham_with_rasterio(d):
    # d = rasterio dataset as above
    a = (10, 10)
    b = (100, 50)
    #-- create in-memory a simple GeoJSON LineString
    v = {}
    v["type"] = "LineString"
    v["coordinates"] = []
    v["coordinates"].append(d.xy(a[0], a[1]))
    v["coordinates"].append(d.xy(b[0], b[1]))
    shapes = [(v, 1)]
    re = features.rasterize(shapes, 
                            out_shape=d.shape, 
                            # all_touched=True,
                            transform=d.transform)
    # re is a numpy with d.shape where the line is rasterised (values != 0)



