
def ses_xps(date='', fl_nmbs=[], norm=False, sh=[], off=[], ml=[]):
    import os

    base_path = "/direct/XF21ID1/csv_files/XPS"
    f, ax = plt.subplots(figsize=(8,6))
    plt.xticks(fontsize=12, rotation=0)
    
    if sh  ==[]: sh  =[0.0]*len(fl_nmbs)
    if off ==[]: off =[0.0]*len(fl_nmbs)
    if ml  ==[]: ml  =[1.0]*len(fl_nmbs)
    
    for indx, fl_nb in enumerate(fl_nmbs):
        fl_str = str(fl_nb)
        for i in range(4-len(str(fl_nb))):
            fl_str = '0' + fl_str
        filename = date + '_' + fl_str + '.txt'
        path_to_file = os.path.join(base_path, filename)
        fd = open(path_to_file , 'r')
        lst = fd.readlines()      #python list: every element is a line
        lst = lst[lst.index("[Data 1]\n")+1:-1]
        x,y = [],[]
        for i in lst:
            x.append(i.split(' ')[1])
            y.append(i.split(' ')[3])
        x, y =np.array(x),np.array(y)
        x, y =np.asfarray(x,float),np.asfarray(y,float)
        if norm != False:
            y = (y-min(y))/(max(y)-min(y))*norm
            
        ax.plot(x+sh[indx],ml[indx]*y+off[indx], label= date+'_'+fl_str)
        ax.legend()
    return 



def read_in_2ddddd(filename):
    '''read-in ses 2D data
    If the data is 1D it quits and gives a message'''
    import os

    base_path = "/direct/XF21ID1/csv_files/XPS"          #directory containing the ses data  
    path_to_file = os.path.join(base_path, filename)
    fd = open(path_to_file , 'r')
    lst = fd.readlines()                                 #python list: every element is a line

    lst_dim1 = [c for c in lst if 'Dimension 1' in c]    # the lines of the file pertaining to Dimension 1 (energy)
    dim1_name = lst_dim1[0][17:-1]                       # the first line [0], contains the name from character 17 on
    d1_str = lst_dim1[2][18:-1].split(' ')               # the values of this axis are in the third element [2], 
                                                         # from char. 18 on
    d1 = [float(i) for i in d1_str]                      # the characters are transformed in numbers

    lst_dim2 = [c for c in lst if 'Dimension 2' in c]    # same for Dimention 2 (angle)
    if lst_dim2 != []:                                   
        dim2_name = lst_dim2[0][17:-1]
    else:
        print(filename + ' is not a 2D data')            # if there is no second dim. quit
        return None, None, None, None, None
    d2_str = lst_dim2[2][18:-1].split(' ')
    d2 = [float(i) for i in d2_str]

                    # Scienta txt files: 
                    # the data are stored in consecutive lines which starts just after a special line '[Data 1]\n'
                    # the first element of the line is the energy value, followed by a list of ordered intensities 
                    # (from min angles to max angle) for that energy
                    # need to eliminate the last character ([:-1]) which is a carriage return and the first 
                    # value ([1:]) which is the energy

    Idata = np.empty([len(d1), len(d2)])   
    for i in range(len(d1)):
        ln = lst[lst.index('[Data 1]\n')+1+i][:-1].split('  ')[1:]    
        Idata[i] = [float(i) for i in ln]
    Idata = np.transpose(Idata)
    return np.asarray(d1), dim1_name, np.asarray(d2), dim2_name, Idata



def read_in_2d(filename):
    '''read-in ses 2D data
    If the data is 1D it quits and gives a message'''
    import os

    base_path = "/direct/XF21ID1/csv_files/XPS"          #directory containing the ses data  
    path_to_file = os.path.join(base_path, filename)
    fd = open(path_to_file , 'r')
    lst = fd.readlines()                                 #python list: every element is a line


    PE = float([c for c in lst if 'Pass Energy' in c][0].split('=')[1])
    Lens_Mode = str([c for c in lst if 'Lens Mode' in c][0].split('=')[1])
    n_swps = int([c for c in lst if 'Number of Sweeps' in c][0].split('=')[1])
    hv = float([c for c in lst if 'Excitation Energy' in c][0].split('=')[1])
    en_stp= float([c for c in lst if 'Energy Step' in c][0].split('=')[1])
    Date = str([c for c in lst if 'Date' in c][0].split('=')[1])
    Time = [c for c in lst if 'Time' in c][1].split('=')[1]
    Cmts = [c for c in lst if 'Comments' in c][0]
    info = {'PE': PE,
            'Lens_Mode': Lens_Mode,
            'n_swps': n_swps,
            'hv': hv,
            'en_stp': en_stp,
            'Date': Date,
            'Time': Time,
            'Cmts': Cmts
    }
    
    lst_dim1 = [c for c in lst if 'Dimension 1' in c]    # the lines of the file pertaining to Dimension 1 (energy)
    dim1_name = lst_dim1[0][17:-1]                       # the first line [0], contains the name from character 17 on
    d1_str = lst_dim1[2][18:-1].split(' ')               # the values of this axis are in the third element [2], 
                                                         # from char. 18 on
    d1 = [float(i) for i in d1_str]                      # the characters are transformed in numbers

    lst_dim2 = [c for c in lst if 'Dimension 2' in c]    # same for Dimention 2 (angle)
    if lst_dim2 != []:                                   
        dim2_name = lst_dim2[0][17:-1]
    else:
        print(filename + ' is not a 2D data')            # if there is no second dim. quit
        return None, None, None, None, None
    d2_str = lst_dim2[2][18:-1].split(' ')
    d2 = [float(i) for i in d2_str]

                    # Scienta txt files: 
                    # the data are stored in consecutive lines which starts just after a special line '[Data 1]\n'
                    # the first element of the line is the energy value, followed by a list of ordered intensities 
                    # (from min angles to max angle) for that energy
                    # need to eliminate the last character ([:-1]) which is a carriage return and the first 
                    # value ([1:]) which is the energy

    Idata = np.empty([len(d1), len(d2)])   
    for i in range(len(d1)):
        ln = lst[lst.index('[Data 1]\n')+1+i][:-1].split('  ')[1:]    
        Idata[i] = [float(i) for i in ln]
    Idata = np.transpose(Idata)
    return np.asarray(d1), dim1_name, np.asarray(d2), dim2_name, Idata, info




def ses_2D(ymd ='', nmb=None, sum_=False):
    '''routine to plot ses_2D data.
    If sum_=True plot also the sum over all angles'''

    import ipywidgets as widgets               # prepare a slider to manipulate the contranst   
    from ipywidgets import HBox, VBox
    from IPython.display import display

    
    
    fl_str = str(nmb)
    for i in range(4-len(str(nmb))):
        fl_str = '0' + fl_str
    filename = ymd + '_' + fl_str + '.txt'

    en, en_name, ang, ang_name, I, info = read_in_2d(filename) # read_in the data and the name of the axis
    
    if (en_name or ang_name)== None: return 

    print(info['hv'])
    im_extent=[en[0], en[-1], ang[0], ang[-1]]
    im_aspect=abs((en[-1]-en[0])/(ang[-1]-ang[0]))

    I_T = I.transpose()
    I_sum_en = np.empty([I.shape[1]])
    I_sum_en = np.sum(I, axis=0, out = I_sum_en)

    I_sum_an = np.empty([I_T.shape[1]])
    I_sum_an = np.sum(I_T, axis=0, out = I_sum_an)

    
    ang_stp, ang_range, ang_cols= abs(ang[0]-ang[1]),\
                                      abs(ang[0]-ang[-1]),\
                                      abs((ang[0]-ang[-1])/(ang[0]-ang[1]))
    en_stp, en_range, en_cols= abs(en[0]-en[1]),\
                                      abs(en[0]-en[-1]),\
                                      abs((en[0]-en[-1])/(en[0]-en[1]))
                
    ln_flag = None
    
    cmap = widgets.Dropdown(
                            options=['viridis', 'plasma', 'inferno', 'magma', 'gray'],
                            value='viridis',
                            description='cmap:',
                            disabled=False,
                            )
#    display(cmap)


    sldr_Cntr = widgets.FloatSlider(
        value=1,
#        value=(I.max()-I.min())/2,        
        min=.1,
#        max=I.max()-I.min(),
        max=2,
        step=0.01,
#        step=0.01*(I.max()-I.min()),
        description='Contrast:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.1f',
    ) 
#    display(sldr_Cntr)

    
    def on_value_change_Cntr(change):
        if sum_:
            im = ax2[0].imshow(I,extent=im_extent, aspect = im_aspect,\
                       cmap=cmap.value, interpolation='none', origin='lower',\
                               vmin=I.min()*change['new'], vmax=I.max()*change['new'])
            plt.tight_layout()
        else:
            im = ax2.imshow(I,extent=im_extent, aspect = im_aspect,\
                       cmap=cmap.value, interpolation='none', origin='lower',\
                               vmin=I.min()*change['new'], vmax=I.max()*change['new'])


    sldr_Cntr.observe(on_value_change_Cntr, names='value')
    

    

    if sum_:
        fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=2, figsize=(8,6), dpi=80, facecolor='w', edgecolor='k')
        ax2[0].get_shared_x_axes().join(ax2[0], ax1[0])
        ax2[0].get_shared_y_axes().join(ax2[0], ax2[1])

        
        im = ax2[0].imshow(I,extent=im_extent, aspect = im_aspect,\
                        cmap=cmap.value, interpolation='none', origin='lower',vmin=I.min(), vmax=I.max())

        ax2[0].set_xlabel(en_name)
        ax2[0].set_ylabel(ang_name)
        
        
        #***************************************#
        # ENERGY Slyder

        sldr_En = widgets.IntSlider(
            value=1,
            min=1,
            max=ang_cols-10,
            step=1,
            description='En_center',
            disabled=False,
            continuous_update=True,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        ) 
#        display(sldr_En)
        
        def on_value_change_En(change):
            n_loc = int(change['new'])
#            print('slider_En value %d' %sldr_En.value)
#            print('slider_En_dlt value %d' %sldr_En_dlt.value)
            ax1[0].clear()
            ax1[0].plot(en, sum(I[n_loc:n_loc+sldr_En_dlt.value]), label=filename)
#            print(en[0], en[-1], ang[n_loc])
            ax2[0].clear()
            ax2[0].imshow(I,extent=im_extent, aspect = im_aspect,\
                        cmap=cmap.value, interpolation='none', origin='lower',vmin=I.min(), vmax=I.max())
            ax2[0].plot([en[0],en[-1]], [ang[n_loc], ang[n_loc]], 'r--', linewidth = 1)
            ax2[0].set_title('Angle = %.3f' %ang[n_loc])
            ax2[0].set_xlabel(en_name)
            ax2[0].set_ylabel(ang_name)

                
            plt.tight_layout()       
        
        
        sldr_En_dlt = widgets.IntSlider(
            value=10,
            min=1,
            max=I.shape[1]//2,
            step=0.01*(I.shape[1]//2),
            description='En_delta',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        ) 
#        display(sldr_En_dlt)
        
        def on_value_change_En_dlt(change):
            change['new']
 
        sldr_En_dlt.observe(on_value_change_En_dlt, names='value')
        sldr_En.observe(on_value_change_En, names='value')


        #***************************************#
        # ANGLE Slyder

        sldr_An = widgets.IntSlider(
            value=1,
            min=1,
            max=en_cols-10,
            step=1,
            description='An_center',
            disabled=False,
            continuous_update=True,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        ) 
#        display(sldr_An)
        
        def on_value_change_An(change):
            n_loc = int(change['new'])
#            print('slider_ang value %d' %sldr_An.value)
#            print('slider_ang_dlt value %d' %sldr_An_dlt.value)
            ax2[1].clear()
            ax2[1].plot(sum(I_T[n_loc:n_loc+sldr_An_dlt.value]),ang, label=filename)
            ax2[0].clear()
            ax2[0].imshow(I,extent=im_extent, aspect = im_aspect,\
                        cmap=cmap.value, interpolation='none', origin='lower',vmin=I.min(), vmax=I.max())
            ax2[0].plot([en[n_loc], en[n_loc]], [ang[0],ang[-1]], 'r--', linewidth = 1)
            ax2[0].set_title('En = %.3f' %en[n_loc])
            ax2[0].set_xlabel(en_name)
            ax2[0].set_ylabel(ang_name)

            plt.tight_layout()       
        
        
        sldr_An_dlt = widgets.IntSlider(
            value=10,
            min=1,
            max=I.shape[0]//2,
            step=0.01*(I.shape[0]//2),
            description='An_delta',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d',
        ) 
#        display(sldr_An_dlt)
        
        def on_value_change_An_dlt(change):
            change['new']
        
        tab_contents = ['E', 'A', 'E-dlt', 'A-dlt', 'cmap', 'ctr']
        children = [sldr_En, sldr_An, sldr_En_dlt, sldr_An_dlt, cmap, sldr_Cntr]
        tab = widgets.Tab()
        tab.children = children
        for i in range(len(children)):
            tab.set_title(i, tab_contents[i])
        display(tab)
                
        
        sldr_An_dlt.observe(on_value_change_An_dlt, names='value')
        sldr_An.observe(on_value_change_An, names='value')
        
        
        
        ax1[0].plot(en, I_sum_en, label=filename)
        ax2[1].plot(I_sum_an, ang,  label=filename)
        ax1[1].text(.2,.8, filename)

        plt.tight_layout()       

    else: # no summed spectra
        fig, ax2 = plt.subplots(nrows=1, ncols=1, figsize=(10, 8),  dpi=80, facecolor='w', edgecolor='k')      
        im = ax2.imshow(I,extent=im_extent, aspect = im_aspect,\
                        cmap=cmap.value, interpolation='none', origin='lower',vmin=I.min(), vmax=I.max())
        ax2.set_title(filename)
        ax2.set_xlabel(en_name)
        ax2.set_ylabel(ang_name)
        cb = ax2.figure.colorbar(im, orientation='horizontal', shrink=.5, pad=.1)    
        
        tab_contents = ['cmap', 'ctr']
        children = [cmap, sldr_Cntr]
        tab = widgets.Tab()
        tab.children = children
        for i in range(len(children)):
            tab.set_title(i, tab_contents[i])
        display(tab)    
        
        plt.tight_layout()       
                





def ses_plot(y_m_d ='', nm=None,  norm=False, sh=[], off=[], ml=[], sum_=False):
    '''ses_plot plot Scienta data. 
    Data names are entered assigning 
    1) ymd: a string with the date year_month_day format
    followed by
    2) nm: either a list of integers or a single integer
    If it is a list, it is assumed to be a graph of multiple 1D-xy curves 
    If it is a single number, it is assumed to be a 2D-plot
    '''
    if type(nm) == list:
        ax = ses_xps(date=y_m_d, fl_nmbs=nm, norm=norm, sh=sh, off=off, ml=ml)
        return ax
    else:
        ses_2D(ymd =y_m_d, nmb=nm, sum_=sum_)



def PES_CS(el, ke, level='nl'):
    elm_dict = np.load('/direct/XF21ID1/csv_files/dictionaries/ph_'+ el + '.npy').item()

    x, y = elm_dict[level]
    x, y =np.array(x),np.array(y)
    x, y =np.asfarray(x,float),np.asfarray(y,float)
    
    if (ke < min(x) or ke > max(x)): #out of interpolation range
        print('Warning: %s%s is out of interpolation range' %(el,level))
        print('Warning: %s%s assigned null cross section' %(el,level))
        cs = 0
    else:
        from scipy import interpolate
        f = interpolate.interp1d(x, y)
        cs = f(ke)      
    return cs





def Core_levels(elm, hv = None, graph = False, h=1, cs_pes = False):
    '''graph can be: False, True or 'overlay'
    '''
    
    # Load the dictionary
    El_BE = np.load('/direct/XF21ID1/csv_files/dictionaries/El_BE.npy').item()
    Z_BE = np.load('/direct/XF21ID1/csv_files/dictionaries/Z_BE.npy').item()

#    col = {'1s':'r',\
#              '2s':'b','2p':'b',\
#              '3s':'g','3p':'g','3d':'g',\
#              '4s':'c','4p':'c','4d':'c','4f':'c',\
#              '5s':'m','5p':'m','5d':'m','5f':'m',\
#              '6s':'y','6p':'y','6d':'y','6f':'y'}

    
    col = {0:'r',\
           1:'b',\
           2:'g',\
           3:'c',\
           4:'m',\
           5:'y',\
           6: 'Orange',\
           7: 'royalblue'}
    
    if graph == False:
        for el in elm:
            if hv == None:
                print(el+': '+'Binding Energies')
                for cl in El_BE[el]:
                    print(cl[0]+ ' = '+str(round(cl[1],2))+ ' eV')
            else:
                print(el+': '+'Kinetic Energies (assuming WF = 5 eV)')
                for cl in El_BE[el]:
                    if hv-cl[1]-5 > 0:
                        print(cl[0]+ ' = '+str(round(hv-cl[1]-5,2))+ ' eV')
    elif graph == True:
        f, ax = plt.subplots(figsize=(12,6))
        plt.xticks(fontsize=12, rotation=0)
        for el in elm:
            if hv == None:
                for cl in El_BE[el]:
                    cl_en = cl[1]   # energy location in eV
                    cl_orbit = cl[0] # nl quantum numbers, as in '2s', '3p1/2' ...
                    ax.plot([cl_en, cl_en], [0,h],color=col[elm.index(el)] , linewidth = 2, \
                            label=el+'-'+cl_en+'='+str(round(cl[1],2)))
                    ax.text(cl[1], 1.25*h,el+'-'+cl[0],color=col[elm.index(el)],\
                            horizontalalignment='center',verticalalignment='center', rotation='vertical')
                ax.set_xlabel('Binding Energy (eV)', fontsize = 12, fontweight = 'bold')
            else:
                for cl in El_BE[el]:
                    cl_en = cl[1]   # energy location in eV
                    cl_orbit = cl[0][0:2] # nl quantum numbers, as in '2s', '3p1/2' ...
                    if hv-cl[1]-5 > 0:
                        cs = 1    # default value if cs_pes is False
                        if cs_pes == True:
                            print('el = %s\t level=%s\t KE = %f' %(el, cl_orbit, hv-5-cl_en))
                            cs = PES_CS(el, hv, level= cl_orbit)
                            print('%s cross section is %f' %(el+cl_orbit, cs))
                        
                            
                        ax.plot([hv-cl[1]-5, hv-cl[1]-5], [0,h*cs], color=col[elm.index(el)] ,linewidth = 2,\
                                label=el+'-'+cl[0]+'='+str(round(hv-cl[1]-5,2))) 
                        ax.text(hv-cl[1]-5, 1.25*h*cs,el+'-'+cl[0], color=col[elm.index(el)] ,\
                            horizontalalignment='center',verticalalignment='center', rotation='vertical')
                ax.set_xlim([0,hv-5])
                ax.set_xlabel('Kinetic Energy (eV)', fontsize = 12, fontweight = 'bold')

                # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        return ax
    elif graph == 'overlay':
        for el in elm:
            if hv == None:
                for cl in El_BE[el]:
                    plt.plot([cl[1], cl[1]], [0,h],color=col[elm.index(el)] , linewidth = 2, \
                            label=el+'-'+cl[0]+'='+str(round(cl[1],2)))
                    plt.text(cl[1], 1.25*h,el+'-'+cl[0],color=col[elm.index(el)],\
                            horizontalalignment='center',verticalalignment='center', rotation='vertical')

                plt.xlabel('Binding Energy (eV)', fontsize = 12, fontweight = 'bold')
            else:
                for cl in El_BE[el]:
                    cl_en = cl[1]   # energy location in eV
                    cl_orbit = cl[0][0:2] # nl quantum numbers, as in '2s', '3p1/2' ...
                    
                    if hv-cl[1]-5 > 0:
                        cs = 1    # default value if cs_pes is False
                        if cs_pes == True:
                            cs = PES_CS(el, hv, level= cl_orbit)
                        plt.plot([hv-cl[1]-5, hv-cl[1]-5], [0,h*cs], '--', color=col[elm.index(el)] ,linewidth = 1,\
                                label=el+'-'+cl[0]+'='+str(round(hv-cl[1]-5,2))) 
                        plt.text(hv-cl[1]-5, 1.25*h*cs, el+'-'+cl[0], color=col[elm.index(el)] ,\
                            horizontalalignment='center',verticalalignment='center', rotation='vertical')
#                plt.xlim([0,hv-5])
                plt.xlabel('Kinetic Energy (eV)', fontsize = 12, fontweight = 'bold')
#                ax.set_title(elm+': '+ 'Core Level Kinetic Energies (hv = ' + str(hv) + ' eV; ' +'WF = ' + str(5) +' eV'+')',\
#                             fontsize = 12, fontweight = 'bold')
                # Shrink current axis by 20%
#        box = plt.get_position()
#        plt.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
