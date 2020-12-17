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
    """returns an array containing a circle and a list containing the boundary of the circle

    Args:
        d (rasterio dataset): raster
        v (viewpoint): viewpoint
        maxdistance (float): distance of radius
    """

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

    # circle_boundary_list = numpy.unique(circle_boundary_list)
    #-- put center  pixel with value of height
    # npvs[vrow_center , vcol_center] = 2#v[2]
    return  npvs , circle_boundary_list
#%%
def viewshedinator(d, v, maxdistance, npvs):
    # get brasenhams line and check in the line for elevation as compared to the tangent
    center = vrow_center, vcol_center = d.index(v[0], v[1])
    vrow_bottom,  vcol_left = d.index(v[0]-maxdistance, v[1]-maxdistance)
    vrow_top, vcol_right    = d.index(v[0]+maxdistance, v[1]+maxdistance)

    npi = d.read(1)
    pix_x,pix_y = d.res
    # get the boundaries of the circle
    bnd_list = circle_make(d, (v[0],v[1]) , maxdistance )[1] 
    circ_bnd = []                                                                                                                                 
    for dat in bnd_list:                                                                                                                                
        if dat not in circ_bnd:                                                                                                                     
            circ_bnd.append(dat)  
        
    cent_height = v[2] + npi[ center[0] , center[1] ]
    npvs[center[0],center[1]] = 2
    # get the indices of bresenham line from bound to center for every point in bound
    for pt in circ_bnd:
        # set tan as pointing down
        temp_tan = -1000
        temp_alt = -1000
        # computer bresenham line for every point in boundary
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
    
        # for indices in bresen_index[1:] :
        #     # calculate tangent

        #     del_row = (indices[0] - center[0]) * pix_x
        #     del_col = (indices[1] - center[1]) * pix_y
        #     leng = (math.sqrt(math.pow( del_row , 2) + math.pow( del_col , 2) ))
        #     height = npi[indices[0], indices[1]]   
        #     tan_ = math.atan(leng/height)
            
        #     if tan_>=tan:
        #         # update tan value
        #         tan=tan_
        #         npvs[indices[0],indices[1]] = 1
        #     elif tan_<tan:
        #         npvs[indices[0],indices[1]] = 0

    
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

    # npvs = numpy.ones(d.shape) * 3
    # for ind in circle_make(d, v, maxdistance)[1]:
    #     npvs[ind[0],ind[1]]=100
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
# def projected_dist(center, bound, point):
#     d1 = numpy.array([bound[0] - center[0] , bound[1] - center[1]])
#     d1_leng = math.sqrt(d1 @ d1)
#     d1_unit = d1/d1_leng
#     d2 = numpy.array( [center[0] - point[0]  ,  center[1] - point[1]] ) 

#     # projection of d2 on d1
#     return d2.dot(d1_unit)

def projected_dist(start,end,current_pt):
    #extract the two vectors
    v1 = numpy.array([end[1]-start[1],end[0]-start[0]])
    v2 = numpy.array([current_pt[1]-start[1],current_pt[0]-start[0]])
    #get the length of the vector describing the line
    Lv1 = numpy.sqrt(v1.dot(v1))
    #and finally get the projected distance of current_pt on the line
    dist = v1.dot(v2)/Lv1
    return dist

"""
def Bresenham_with_rasterio(d, center, point_on_boundary):
    # returns a list of indices which are part of a line from center to the boundary
    # the center and boundary need to be given in form of indices 

    # Args:
    #     d (rasterio data): raster sent as a rasterio data
    #     center (tuple): indices of the center aka viewpoint
    #     point_on_boundary (tuple): indices of the point on boundary of the visible area

    # Returns:
    #     list: [description]
    
    # d = rasterio dataset as above
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
                            # all_touched=True,
                            transform=d.transform)

    # re is a numpy with d.shape where the line is rasterised (values != 0
    indexlist = numpy.argwhere(rasterized_line==1)
    finlist=[]
    # cases of the output list of indices
    # 1: the point is in q1 as compared to the center
    if a[0]<b[0] and a[1]<b[1]:
        # do nothing, the rasterized line assumes that it has been provided in first quadrant
        finlist = indexlist
    # 2: the point is in q2 as compared to center
    elif a[0]>b[0] and a[1]<=b[1]:
        # invert the x values to make it like q1
        finlist = sorted(indexlist.tolist() , key = (lambda x: (-x[0], x[1]) ) )
    # 4: point is in q3 wrt center
    elif a[0]>b[0] and a[1]>=b[1]:
        # invert both the x and y values to make it like q1
        finlist = sorted(indexlist.tolist() , key = (lambda x: (-x[0], -x[1]) ) )
    # 3: the point is in q4 wrt center
    elif a[0]<=b[0] and a[1]>b[1]:
        # invert only y value to make like q1
        finlist = sorted(indexlist.tolist() , key = (lambda x: (x[0], -x[1]) ) )

    del indexlist

    return finlist
"""

def Bresenham_with_rasterio(raster, start, end):
    d = raster
    a = start #format is (row,col)
    b = end #format is (row, col)
    #-- create in-memory a simple GeoJSON LineString
    v = {}
    v["type"] = "LineString"
    v["coordinates"] = []
    v["coordinates"].append(d.xy(a[0], a[1]))
    v["coordinates"].append(d.xy(b[0], b[1]))
    shapes = [(v, 1)]
    re = features.rasterize(shapes,
                            out_shape=d.shape,
                            all_touched=True,
                            transform=d.transform)
    out = numpy.argwhere(re==1)
    outlist = []
    for el in out:
        outlist.append(tuple(el))
    #depending on the orientation of the line, sort cells in right order
    if a[0]>b[0] and a[1]<=b[1]:
        outlist = sorted(outlist, key=lambda x: (-x[0], x[1]))
        #print('a')
    elif a[0]>b[0] and a[1]>=b[1]:
        outlist = sorted(outlist, key=lambda x: (-x[0], -x[1]))
        #print('b')
    elif a[0]<=b[0] and a[1]>b[1]:
        outlist = sorted(outlist, key=lambda x: (x[0], -x[1]))
    return outlist

