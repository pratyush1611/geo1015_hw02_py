#-- my_code_hw02.py
#-- Assignment 02 GEO1015.2020
#-- Pratyush Kumar
#-- 5359252
#-- Giorgos Triantafyllou
#-- [YOUR STUDENT NUMBER] 
#%%
import sys
import math
import numpy
import rasterio
from rasterio import features
#%%


def circle_make(d, v, maxdistance ):
    npi  = d.read(1)
    #-- index of this point in the numpy raster
    vrow_center, vcol_center = d.index(v[0], v[1])
    vrow_bottom,  vcol_left = d.index(v[0]-maxdistance, v[1]-maxdistance)
    vrow_top, vcol_right    = d.index(v[0]+maxdistance, v[1]+maxdistance)

    #-- the results of the viewshed in npvs, all values=0
    # npvs = numpy.ones(d.shape, dtype=numpy.int8)
    npvs = numpy.zeros(d.shape, dtype=bool) #full of false
    circle_boundary_list=[]

    """
    for i , _ in enumerate(npvs):
        for j,__ in enumerate(_):
            if i<vrow_top or i>vrow_bottom:
                continue
            elif j<vcol_left or j>vcol_right:
                continue
            # do circle here #actually a square for now
            # npvs[i,j] = npi[i,j]
            # circle compute
            if ((math.pow((d.xy(i,j)[0] - v[0]),2) + math.pow( (d.xy(i,j)[1] - v[1]) , 2)  ) < math.pow(maxdistance,2)):
                npvs[i,j] = True
                # circle_boundary_list.append()

    # flag=True
    # for i , _ in enumerate(npvs):
    #     for j,__ in enumerate(_):
    #         if i<vrow_top or i>vrow_bottom:
    #             continue
    #         elif j<vcol_left or j>vcol_right:
    #             continue
    

    flag=True
    for i , _ in enumerate(npvs):
        for j,__ in enumerate(_):
            if i<vrow_top or i>vrow_bottom:
                continue
            elif j<vcol_left or j>vcol_right:
                continue
            # within the bounding box of the circle
            if npvs[i,j]== True:
                flag=False
                # circle has been hit
                circle_boundary_list.append((i,j))
            # if npvs[i, len(_)-j]==True:
            #     flag=False
            #     circle_boundary_list.append((i,j))
            if flag != True:
                continue
    flag=True
    for i , _ in enumerate(npvs[::-1]):
        for j,__ in enumerate(_):
            if i<vrow_top or i>vrow_bottom:
                continue
            elif j<vcol_left or j>vcol_right:
                continue
            # within the bounding box of the circle
            if npvs[i,j]== True:
                flag=False
                # circle has been hit
                circle_boundary_list.append((i,len(_)-j))
            if flag != True:
                continue

    """

    # make a circle    # 
    for i in range(vrow_top, vrow_bottom+1):
        for j in range(vcol_left, vcol_right+1):
            # compare distance
            if ((math.pow((d.xy(i,j)[0] - v[0]),2) + math.pow( (d.xy(i,j)[1] - v[1]) , 2)  ) < math.pow(maxdistance,2)):
                npvs[i,j] = True

    for indeX , i in enumerate(npvs):
        # for j in range(vcol_left, vcol_right+1):
        indices = np.argwhere(i==True)
        if len(indices)>1:
            ind_first= (indeX, indices[0][0])
            ind_last = (indeX, indices[-1][0])
            circle_boundary_list.append(ind_first)
            circle_boundary_list.append(ind_last)

        elif len(indices)==1:
            ind_first= (indeX, indices[0][0])
            print(ind_first)
            circle_boundary_list.append(ind_first)

    #-- put center  pixel with value of height
    npvs[vrow_center , vcol_center] = v[2]
    return npvs, circle_boundary_list
#%%
def viewshedinator(d, v, maxdistance):
    # get brasenhams line and check in the line for elevation as compared to the tangent
    vrow_center, vcol_center = d.index(v[0], v[1])
    vrow_bottom,  vcol_left = d.index(v[0]-maxdistance, v[1]-maxdistance)
    vrow_top, vcol_right    = d.index(v[0]+maxdistance, v[1]+maxdistance)

  


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
    npi  = d.read(1)
    #-- fetch the 1st viewpoint
    # v = viewpoints[0]
    
    npvs_array = [circle_make(d, v, maxdistance) for v in viewpoints]
    npvs=npvs_array[1]
    
    # #write this to disk
    with rasterio.open(output_file, 'w', 

                       driver='GTiff', 
                       height=npi.shape[0],
                       width=npi.shape[1], 
                       count=1, 
                       dtype=rasterio.uint8,
                       crs=d.crs, 
                       transform=d.transform) as dst:
        dst.write(npvs.astype(rasterio.uint8), 1)

    print(npvs)
    print("Viewshed file written to '%s'" % output_file)

    return(npvs)
#%%


def Bresenham_with_rasterio(d, center, point_on_boundary):
    # d = rasterio dataset as above
    a = center
    b = point_on_boundary

    #-- create in-memory a simple GeoJSON LineString
    v = {}
    v["type"] = "LineString"
    v["coordinates"] = []
    v["coordinates"].append(d.xy(a[0], a[1]))
    v["coordinates"].append(d.xy(b[0], b[1]))
    shapes = [(v, 1)]
    rasterized_line = features.rasterize(shapes, 
                            out_shape=d.shape, 
                            # all_touched=True,
                            transform=d.transform)

    # re is a numpy with d.shape where the line is rasterised (values != 0
    indexlist = numpy.argwhere(rasterized_line==1)
    
    # cases of the output list of indices
    # 1: the point is in q1 as compared to the center
    if a[0]<b[0] and a[1]<b[1]:
        # do nothing, the rasterized line assumes that it has been provided in first quadrant
        finlist = indexlist
    # 2: the point is in q2 as compared to center
    elif a[0]>b[0] and a[1]<b[1]:
        # invert the x values to make it like q1
        finlist = sorted(indexlist.tolist() , key = (lambda x: (-x[0], x[1]) ) )
    # 4: point is in q3 wrt center
    elif a[0]>b[0] and a[1]>b[1]:
        # invert both the x and y values to make it like q1
        finlist = sorted(indexlist.tolist() , key = (lambda x: (-x[0], -x[1]) ) )
    # 3: the point is in q4 wrt center
    elif a[0]<b[0] and a[1]>b[1]:
        # invert only y value to make like q1
        finlist = sorted(indexlist.tolist() , key = (lambda x: (x[0], -x[1]) ) )

    del indexlist

    return finlist



# %%
