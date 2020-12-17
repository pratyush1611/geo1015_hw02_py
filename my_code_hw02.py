#-- my_code_hw02.py
#-- Assignment 02 GEO1015.2020
#-- Pratyush Kumar
#-- 5359252
#-- Georgios Triantafyllou
#-- 5381738

import sys
import math
import numpy
import rasterio
from rasterio import features

def circle_make(d, v, maxdistance ):
    """returns an array containing a circle and a list containing the boundary of the circle

    Args:
        d (rasterio dataset): raster
        v (viewpoint): viewpoint
        maxdistance (float): distance of radius
    """
    #-- index of this point in the numpy raster
    vrow_bottom,  vcol_left = d.index(v[0]-maxdistance, v[1]-maxdistance)
    vrow_top, vcol_right    = d.index(v[0]+maxdistance, v[1]+maxdistance)


    #-- the results of the viewshed in npvs, all values=0
    # npvs = numpy.ones(d.shape, dtype=numpy.int8)
    npvs = numpy.zeros(d.shape, dtype=bool) #full of false
    circle_boundary_list=[]

    # make a circle inside npvs  
    for i in range(vrow_top, vrow_bottom+1):
        for j in range(vcol_left, vcol_right+1):
            # compare distance
            if ((math.pow((d.xy(i,j)[0] - v[0]),2) + math.pow( (d.xy(i,j)[1] - v[1]) , 2)  ) < math.pow(maxdistance,2)):
                try :
                    npvs[i,j] = True
                except:
                    pass
    # use the npvs to calculate the boundary of circle
    # check the npvs row wise, take first and last pixel in a circle per row, 
    # which form boundary
    for indeX , i in enumerate(npvs):
        indices = numpy.argwhere(i==True)
        if len(indices)>1:
            ind_first= (indeX, indices[0][0])
            ind_last = (indeX, indices[-1][0])
            circle_boundary_list.append(ind_first)
            circle_boundary_list.append(ind_last)

        elif len(indices)==1:
            ind_first= (indeX, indices[0][0])
            print(ind_first)
            circle_boundary_list.append(ind_first)

    # check the npvs row wise, take first and last pixel in a circle per column, 
    # which form boundary
    #  find boundaries by going from top to down
    for indY , j in enumerate(npvs[0]):
        col = npvs[:,indY]
        indices= numpy.argwhere(col==True)

        if len(indices)>1:
            ind_first= (indices[0][0],  indY)
            ind_last = (indices[-1][0], indY)
            circle_boundary_list.append(ind_first)
            circle_boundary_list.append(ind_last)

        elif len(indices)==1:
            ind_first= ( indices[0][0] , indY)
            print(ind_first)
            circle_boundary_list.append(ind_first)

    circ_bnd = []                                                                                                                                 
    for dat in circle_boundary_list:                                                                                                                                
        if dat not in circ_bnd:                                                                                                                     
            circ_bnd.append(dat)  
    
    del circle_boundary_list
    del npvs
    return  circ_bnd
#%%
def viewshedinator(d, v, maxdistance, npvs):
    # get brasenhams line and check in the line for elevation as compared to the tangent
    center = d.index(v[0], v[1])

    npi = d.read(1)

    # get the boundaries of the circle
    circ_bnd = circle_make(d, (v[0],v[1]) , maxdistance )
    cent_height = v[2] + npi[ center[0] , center[1] ]
    
    #-- put center  pixel with value of height
    npvs[center[0],center[1]] = 2

    for pt in circ_bnd:
        # set tan as pointing down
        # set altitude as way below sea level
        temp_tan = -1000
        temp_alt = -1000
        # get the indices of bresenham line from bound to center for every point in bound
        bresen_index = Bresenham_with_rasterio(d, center , pt)

        for point in bresen_index[1:]:

            pt_alt = npi[point[0],point[1]]

                # set tan values
            if pt_alt>temp_alt:
                proj_dist = projected_dist(center, tuple(bresen_index[-1]) , tuple(point))
                del_alt = pt_alt - cent_height
                if pt_alt> cent_height:
                    # update temp alt
                    temp_alt = pt_alt
                if del_alt>0:
                    tan = math.atan(del_alt/proj_dist)
                elif del_alt<0:
                    tan = math.atan(del_alt/proj_dist)
                elif del_alt==0: # point on same elevation as the center
                    tan=0
                # check tan values
                if tan>temp_tan and npvs[point[0],point[1]] != 2:
                    # update the tan value
                    temp_tan = tan
                    npvs[point[0],point[1]] = 1 #visible point

                elif npvs[point[0],point[1]] == 3: # not visible
                    npvs[point[0],point[1]] = 0
            elif npvs[point[0],point[1]] == 3: # if in the line it is not yet set, its not visible
                npvs[point[0],point[1]] = 0 

    return npvs


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
    v = viewpoints[0]
    npvs = numpy.ones(d.shape , dtype= numpy.int8 ) * 3
    for v in viewpoints:
        npvs= viewshedinator(d, v, maxdistance , npvs)

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



def projected_dist(center, bound, point):
    d1 = numpy.array([bound[1] - center[1] , bound[0] - center[0]])
    d1_leng = math.sqrt(d1@(d1))
    d1_unit = d1/d1_leng
    d2 = numpy.array( [point[1] - center[1]  ,  point[0] - center[0]] ) 

    # projection of d2 on d1
    ret = d2@(d1_unit)
    return ret



def Bresenham_with_rasterio(d, center, point_on_boundary):
    """
    returns a list of indices which are part of a line from center to the boundary
    the center and boundary need to be given in form of indices 

    Args:
        d (rasterio data): raster sent as a rasterio data
        center (tuple): indices of the center aka viewpoint
        point_on_boundary (tuple): indices of the point on boundary of the visible area

    Returns:
        list: [description]
    """
    a = center
    b = point_on_boundary

    #-- create in-memory a simple GeoJSON LineString
    v = {}
    v["type"] = "LineString"
    v["coordinates"] = []
    v["coordinates"].append(d.xy(a[0], a[1])) # takes the index
    v["coordinates"].append(d.xy(b[0], b[1])) # takes the  index
    shapes = [(v, 1)]
    rasterized_line = features.rasterize(shapes, 
                            out_shape=d.shape, 
                            all_touched=True,
                            transform=d.transform)

    # re is a numpy with d.shape where the line is rasterised (values != 0
    indexlist = numpy.argwhere(rasterized_line==1)
    finlist=[tuple(i) for i in indexlist]
    del indexlist

    # cases of the output list of indices
    # 1: the point is in q1 as compared to the center
    if a[0]<b[0] and a[1]<b[1]:
        # do nothing, the rasterized line assumes that it has been provided in first quadrant
        pass
    # 2: the point is in q2 as compared to center
    elif a[0]>b[0] and a[1]<=b[1]:
        # invert the x values to make it like q1
        finlist = sorted(finlist , key = (lambda x: (-x[0], x[1]) ) )
    # 4: point is in q3 wrt center
    elif a[0]>b[0] and a[1]>=b[1]:
        # invert both the x and y values to make it like q1
        finlist = sorted(finlist , key = (lambda x: (-x[0], -x[1]) ) )
    # 3: the point is in q4 wrt center
    elif a[0]<=b[0] and a[1]>b[1]:
        # invert only y value to make like q1
        finlist = sorted(finlist , key = (lambda x: (x[0], -x[1]) ) )

    return finlist

