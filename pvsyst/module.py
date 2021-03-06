'''
@author: frederic rivollier
'''

import re, sys, os
import json, struct
import numpy as np

from .core import text_to_dict


import logging
logging.addLevelName(5,"VERBOSE")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pysyst.module')

from pprint import pprint, pformat


# read PAN file and return dict
def pan_to_dict(path):

    # group keys of PVSYST 6.7.6
    # key is the start value to identify
    # vaLue is the dict key to be used
    pan_sections ={'PVObject_': 'pvModule',
                'PVObject_Commercial': 'pvCommercial',
                'PVObject_IAM': 'pvIAM',
                'IAMProfile': 'TCubicProfile',
                'Remarks, Count': 'Remarks',
                'OperPoints, list of': 'tOperPoint'}

    #open file
    with open(path,'r') as file:
        raw = file.read()

    #parse text file to nested dict based on pan_keys
    data = text_to_dict(raw, pan_sections)
    logger.debug(pformat(data))

    '''
    List of PVSYST paramters and units:
    http://files.pvsyst.com/help/pvmodule_parametersummary.htm
    '''
    m = {}
    m['manufacturer'] = (data['pvModule']['pvCommercial']['Manufacturer'])
    m['Model'] = (data['pvModule']['pvCommercial']['Model'])
    m['Technol'] = (data['pvModule']['Technol'])

    m['NCelS'] = int(data['pvModule']['NCelS'])
    m['NCelP'] = int(data['pvModule']['NCelP'])
    m['GRef'] = float(data['pvModule']['GRef'])
    m['TRef'] = float(data['pvModule']['TRef'])
    m['PNom'] = float(data['pvModule']['PNom'])
    m['Isc'] = float(data['pvModule']['Isc'])
    m['Voc'] = float(data['pvModule']['Voc'])
    m['Imp'] = float(data['pvModule']['Imp'])
    m['Vmp'] = float(data['pvModule']['Vmp'])

    m['muISC'] = float(data['pvModule']['muISC'])
    m['muVocSpec'] = float(data['pvModule']['muVocSpec'])

    m['muISC'] = float(data['pvModule']['muISC'])
    m['muVocSpec'] = float(data['pvModule']['muVocSpec'])

    m['muPmpReq'] = float(data['pvModule']['muPmpReq'])
    m['RShunt'] = float(data['pvModule']['RShunt'])
    m['Rp_0'] = float(data['pvModule']['Rp_0'])
    m['Rp_Exp'] = float(data['pvModule']['Rp_Exp'])
    m['RSerie'] = float(data['pvModule']['RSerie'])
    m['Gamma'] = float(data['pvModule']['Gamma'])
    m['muGamma'] = float(data['pvModule']['muGamma'])

    # IAM profile to ndarray

    # Options:
    # FrontSurface=fsNormalGlass
    # FrontSurface=fsARCoating
    # if not defined FrontSurface key will not exist
    # FrontSurface=fsPlastic
    # FrontSurface=fsTextured

    '''
    # if Ashre  PVObject_IAM=pvIAM / IAMMode=Ashrae
      PVObject_IAM=pvIAM
        Flags=$00
        IAMMode=Ashrae
        B0_IAM=0.075
      End of PVObject pvIAM

     # if user define FrontSurface key will not exist but  PVObject_IAM=pvIAM
     PVObject_IAM=pvIAM
        Flags=$00
        IAMMode=UserProfile
        IAMProfile=TCubicProfile
          NPtsMax=9
          NPtsEff=9
          LastCompile=$B18D
          Mode=3
          Point_1=10.0,0.99900
          Point_2=20.0,0.99900
          Point_3=30.0,0.99500
          Point_4=40.0,0.99200
          Point_5=50.0,0.98600
          Point_6=60.0,0.97000
          Point_7=70.0,0.91700
          Point_8=80.0,0.76300
          Point_9=90.0,0.00000
        End of TCubicProfile
      End of PVObject pvIAM
  '''
    try:
        if data['pvModule']['pvIAM']['IAMMode'] == 'UserProfile':
            points = int(data['pvModule']['pvIAM']['TCubicProfile']['NPtsEff'])
            x = []
            y = []
            for n in range(points):
                v = data['pvModule']['pvIAM']['TCubicProfile']['Point_{}'.format(n+1)]
                v = v.split(',')
                x.append(float(v[0]))
                m['Point_{}_AOI'.format(n+1)] = float(v[0])

                y.append(float(v[1]))
                m['Point_{}_EFF'.format(n+1)] = float(v[1])

            # m['IAM'] = np.array([x,y])

    except Exception as e:
        logger.warning('IAM profile not found')
        logger.log(5, e)
        m['IAM'] = None



    '''
    low irradiance
    OperPoints, list of=6 tOperPoint
        Point_1=False,800,25.0,0.00,0.00,0.000,0.000,0.00
        Point_2=False,600,25.0,0.00,0.00,0.000,0.000,0.00
        Point_3=False,400,25.0,0.00,0.00,0.000,0.000,0.00
        Point_4=False,200,25.0,0.00,0.00,0.000,0.000,0.00
        Point_5=False,200,25.0,0.00,0.00,0.000,0.000,0.00
        Point_6=False,200,25.0,0.00,0.00,0.000,0.000,0.00
      End of List OperPoints

    '''

    return m


# read PAN file and return dict of module paramters for PVLIB
def pan_to_module_param(path):

    # group keys of PVSYST 6.7.6
    # key is the start value to identify
    # vaLue is the dict key to be used
    pan_sections ={'PVObject_': 'pvModule',
                'PVObject_Commercial': 'pvCommercial',
                'PVObject_IAM': 'pvIAM',
                'IAMProfile': 'TCubicProfile',
                'Remarks, Count': 'Remarks',
                'OperPoints, list of': 'tOperPoint'}

    #open file
    with open(path,'r') as file:
        raw = file.read()

    #parse text file to nested dict based on pan_keys
    data = text_to_dict(raw, pan_sections)
    logger.debug(pformat(data))

    '''
    List of PVSYST paramters and units:
    http://files.pvsyst.com/help/pvmodule_parametersummary.htm
    '''
    m = {}
    m['manufacturer'] = (data['pvModule']['pvCommercial']['Manufacturer'])
    m['module_name'] = (data['pvModule']['pvCommercial']['Model'])
    m['Technol'] = (data['pvModule']['Technol'])

    m['CellsInS'] = int(data['pvModule']['NCelS'])
    m['CellsInP'] = int(data['pvModule']['NCelP'])
    m['GRef'] = float(data['pvModule']['GRef'])
    m['TRef'] = float(data['pvModule']['TRef'])
    m['Pmpp'] = float(data['pvModule']['PNom'])
    m['Isc'] = float(data['pvModule']['Isc'])
    m['Voc'] = float(data['pvModule']['Voc'])
    m['Impp'] = float(data['pvModule']['Imp'])
    m['Vmpp'] = float(data['pvModule']['Vmp'])

    m['mIsc_percent'] = (float(data['pvModule']['muISC'])/1000/m['Isc'])*100 #PAN stored in mA/C,convert to %/C
    m['mVoc_percent'] = (float(data['pvModule']['muVocSpec'])/1000/m['Voc'])*100 # PAN stored in mV/C, convert to %/C

    m['mIsc'] = float(data['pvModule']['muISC'])/1000  # convert to A/C
    m['mVocSpec'] = float(data['pvModule']['muVocSpec'])/1000  # convert to V/C

    m['mPmpp'] = float(data['pvModule']['muPmpReq'])
    m['Rshunt'] = float(data['pvModule']['RShunt'])
    m['Rsh 0'] = float(data['pvModule']['Rp_0'])
    m['Rshexp'] = float(data['pvModule']['Rp_Exp'])
    m['Rserie'] = float(data['pvModule']['RSerie'])
    m['Gamma'] = float(data['pvModule']['Gamma'])
    m['muGamma'] = float(data['pvModule']['muGamma'])

    # IAM profile to ndarray

    # Options:
    # FrontSurface=fsNormalGlass
    # FrontSurface=fsARCoating
    # if not defined FrontSurface key will not exist
    # FrontSurface=fsPlastic
    # FrontSurface=fsTextured

    '''
    # if Ashre  PVObject_IAM=pvIAM / IAMMode=Ashrae
      PVObject_IAM=pvIAM
        Flags=$00
        IAMMode=Ashrae
        B0_IAM=0.075
      End of PVObject pvIAM

     # if user define FrontSurface key will not exist but  PVObject_IAM=pvIAM
     PVObject_IAM=pvIAM
        Flags=$00
        IAMMode=UserProfile
        IAMProfile=TCubicProfile
          NPtsMax=9
          NPtsEff=9
          LastCompile=$B18D
          Mode=3
          Point_1=10.0,0.99900
          Point_2=20.0,0.99900
          Point_3=30.0,0.99500
          Point_4=40.0,0.99200
          Point_5=50.0,0.98600
          Point_6=60.0,0.97000
          Point_7=70.0,0.91700
          Point_8=80.0,0.76300
          Point_9=90.0,0.00000
        End of TCubicProfile
      End of PVObject pvIAM
  '''
    try:
        if data['pvModule']['pvIAM']['IAMMode'] == 'UserProfile':
            points = int(data['pvModule']['pvIAM']['TCubicProfile']['NPtsEff'])
            x = []
            y = []
            for n in range(points):
                v = data['pvModule']['pvIAM']['TCubicProfile']['Point_{}'.format(n+1)]
                v = v.split(',')
                x.append(float(v[0]))
                y.append(float(v[1]))
            m['IAM'] = np.array([x,y])
    except Exception as e:
        logger.warning('IAM profile not found')
        logger.log(5, e)
        m['IAM'] = None

    '''
    low irradiance
    OperPoints, list of=6 tOperPoint
        Point_1=False,800,25.0,0.00,0.00,0.000,0.000,0.00
        Point_2=False,600,25.0,0.00,0.00,0.000,0.000,0.00
        Point_3=False,400,25.0,0.00,0.00,0.000,0.000,0.00
        Point_4=False,200,25.0,0.00,0.00,0.000,0.000,0.00
        Point_5=False,200,25.0,0.00,0.00,0.000,0.000,0.00
        Point_6=False,200,25.0,0.00,0.00,0.000,0.000,0.00
      End of List OperPoints

    '''


    #constants
    k = 1.38064852e-23 #Boltzmann’s constant (J/K)
    kelvin0 = 273.15
    q = 1.60217662e-19 # charge of an electron (coulombs)
    GRef = 1000
    Tc = 25 + kelvin0 #Deg Kelvin

    '''
    solve IoRef for Pmp
    Using Voc to solve reverse saturation current IoRef based on
    reference: Mermoud, Lejeune (2010): Performance Assessment of a Simulation Model for PV Modules of Any Available Technology.
    Proc 25th European Photovoltaic Solar Energy Conference –Valencia, Spain, 6-10 September 2010

    #PVSYST one diode equation
    http://files.pvsyst.com/help/index.html?pvcell_reversechar.htm

    I  =  Iph  -   Io  [ exp  (q · (V+I·Rs) / ( Ncs·Gamma·k·Tc) ) - 1 ]    -    (V + I·Rs) / Rsh

    with :
    I        =        Current supplied by the module  [A].
    V        =        Voltage at the terminals of the module  [V].
    Iph   [Isc]     =        Photocurrent [A], proportional to the irradiance G,  with a correction as function of  Tc  (see below).
    ID        =        Diode current, is the product   Io  ·  [exp(     ) -1].
    Io  [I_0_ref]      =        inverse saturation current, depending on the temperature [A]  (see expression below).
    Rs        =        Series resistance [ohm].
    Rsh        =        Shunt resistance [ohm].
    q        =        Charge of the electron  =  1.602·E-19 Coulomb
    k        =        Bolzmann's constant =  1.381 E-23  J/K.
    Gamma=          Diode quality factor, normally between 1 and 2
    Ncs        =        Number of cells in series.
    Tc        =        Effective temperature of the cells [Kelvin]
    '''

    # solving IoRef for Pmax
    # PVSYST manual is not clear on method used by PVSYST i.e. Voc or Pmpp
    # Checked empiricaly agains PVSYST and is the method used by CASSYS
    I = m['Impp']  # solve IoRef for Pmax
    V = m['Vmpp']  # solve IoRef for Pmax

    Io = -((I+(V + I*m['Rserie'])/\
                m['Rshunt'])-m['Isc'])/\
                (np.exp(q*(V+I*m['Rserie'])/\
                (m['CellsInS']*m['Gamma']*k*Tc))-1)


    # mapping pvlib mpodule paramters names
    m['gamma_ref'] = m['Gamma']
    m['mu_gamma'] = m['muGamma']
    m['I_L_ref'] = m['Isc']
    m['I_o_ref'] = Io
    m['EgRef'] = 1.121  # The energy bandgap at reference temperature in units of eV
    m['R_sh_ref'] = m['Rshunt']
    m['R_sh_0'] = m['Rsh 0']
    m['R_s'] = m['Rserie']
    m['R_sh_exp'] = m['Rshexp']
    m['cells_in_series'] = m['CellsInS']
    m['alpha_sc'] = m['mIsc']  # A/C

    return m
