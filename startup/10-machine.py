from ophyd import EpicsSignal,PVPositioner, EpicsSignalRO, EpicsMotor
from ophyd import Device, Component as Comp
from ophyd import Component as Cpt
from ophyd import DeviceStatus


MR_attrs = "'user_readback','user_setpoint','motor_is_moving','motor_done_move','motor_stop'"

# ---------------------------- Load Lock -----------------------------
# Load Lock
#
class LL_mtr(Device):
    Claw_Trans = Comp(EpicsMotor,'2-Claw:EA3_1-Ax:T}Mtr')
    Claw_Rotate = Comp(EpicsMotor,'2-Claw:EA3_1-Ax:R}Mtr')
    Claw_Grab = Comp(EpicsMotor,'2-Claw:EA3_1-Ax:C}Mtr')
    Dock_Trans = Comp(EpicsMotor,'1-Dock:EA4_1-Ax:F}Mtr')

LL = LL_mtr('XF:21IDD-ES{LL:', name='LL')
# define what is displayed from the LL during quieries using LL.hints.
LL.hints = {'fields': [LL.Claw_Trans.name,LL.Claw_Rotate.name,LL.Claw_Grab.name,LL.Dock_Trans.name]}


#
# ---------------------------- LOW_TEMP Chamber -----------------------------
# Low_temp chamber:
#
class LT_mtr(Device):
   X = Comp(EpicsMotor,"-Ax:X}Mtr")
   Y = Comp(EpicsMotor,"-Ax:Y}Mtr")
   Z = Comp(EpicsMotor,"-Ax:Z}Mtr")
   Ry =  Comp(EpicsMotor,"-Ax:Ry}Mtr")

LT = LT_mtr('XF:21IDD-ES{LT:1-Manip:EA5_1', name='LT')
# define what is displayed from LT during quieries using LT.hints.
LT.hints = {'fields': [LT.X.name,LT.Y.name,LT.Z.name,LT.Ry.name]}


# ---------------------------- SAMPLE_PREP Chamber -----------------------------
# Sample_prep chamber:
#
class SP_mtr(Device):
    X = Comp(EpicsMotor,"-Ax:X}Mtr")
    Y = Comp(EpicsMotor,"-Ax:Y}Mtr")
    Z = Comp(EpicsMotor,"-Ax:Z}Mtr")
    Rx = Comp(EpicsMotor,"-Ax:Rx}Mtr")

SP = SP_mtr('XF:21IDD-ES{SP:1-Manip:EA2_1', name='SP')
# define what is displayed from SP during quieries using SP.hints.
SP.hints = {'fields': [SP.X.name,SP.Y.name,SP.Z.name,SP.Rx.name]}

#
#
# ---------------------------- ANALYSIS Chamber -----------------------------
# Analysis chamber:
#

class An_mtr(Device):

    #Add micro-scanning stage motors here when done
    Claw_Trans = Comp(EpicsMotor,"{ST:1-Claw:EA1_1-Ax:T}Mtr")
    Claw_Grab = Comp(EpicsMotor,"{ST:1-Claw:EA1_1-Ax:C}Mtr")

An = An_mtr("XF:21IDD-ES", name='An')
# define what is displayed from An during quieries using An.hints.
An.hints = {'fields': [An.Claw_Trans.name,An.Claw_Grab.name]}

#
#
# ---------------------------- Scienta Analyzer -----------------------------
# Scienta Analyzer:
#

class Analyzer_mtr(Device):
    Rz = Comp(EpicsMotor,"{SA:1-DPRF:EA1_1-Ax:1}Mtr")

SA = Analyzer_mtr("XF:21IDD-ES", name='SA')
# define what is displayed from SA during quieries using SA.hints.
SA.hints = {'fields': [SA.Rz.name]}
#
#
#---------------------------Mirrors------------------------------
class M1_mirror(Device):
    X = Comp(EpicsMotor,"Trans}Mtr")
    Mirror_Trans = Comp(EpicsMotor,"Trans}Mtr")
    Mirror_InOut = Comp(EpicsMotor,"Trans}Mtr")
    Ry = Comp(EpicsMotor,"Pitch}Mtr")
    Mirror_Pitch = Comp(EpicsMotor,"Pitch}Mtr")
    Rz = Comp(EpicsMotor,"Roll}Mtr")
    Mirror_Roll = Comp(EpicsMotor,"Roll}Mtr")

M1 = M1_mirror("XF:21IDA-OP{Mir:1-Ax:4_",name="M1")
# define what is displayed from M1 during quieries using M1.hints.
M1.hints = {'fields': [M1.X.name,M1.Ry.name,M1.Rz.name]}
    
class Hexapod_Mir(Device):
    X = Comp(EpicsMotor,"_X}Mtr")
    Mirror_Trans = Comp(EpicsMotor,"_X}Mtr")
    Mirror_InOut = Comp(EpicsMotor,"_X}Mtr")
    Y = Comp(EpicsMotor,"_Y}Mtr")
    Mirror_Stripe = Comp(EpicsMotor,"_Y}Mtr")
    Mirror_Exchange = Comp(EpicsMotor,"_Y}Mtr") 
    Z = Comp(EpicsMotor,"_Z}Mtr")
    Rx = Comp(EpicsMotor,"_Rx}Mtr")
    Mirror_Roll = Comp(EpicsMotor,"_Rz}Mtr")
    Ry = Comp(EpicsMotor,"_Ry}Mtr")
    Mirror_Pitch = Comp(EpicsMotor,"_Ry}Mtr")
    Rz = Comp(EpicsMotor,"_Rz}Mtr")
    Mirror_Yaw = Comp(EpicsMotor,"_Rx}Mtr")
    
M3 = Hexapod_Mir("XF:21IDB-OP{Mir:3-Ax:11",name="M3")
# define what is displayed from M3 during quieries using M3.hints.
M3.hints = {'fields': [M3.X.name,M3.Y.name,M3.Z.name,M3.Rx.name,M3.Ry.name,M3.Rz.name]}
M4B = Hexapod_Mir("XF:21IDC-OP{Mir:4B-Ax:B4",name="M4B")
# define what is displayed from M3 during quieries using M3.hints.
M4B.hints = {'fields': [M4B.X.name,M4B.Y.name,M4B.Z.name,M4B.Rx.name,M4B.Ry.name,M4B.Rz.name]}

class Monochromator(Device):
    Focus_Const = Comp(EpicsMotor,"-Ax:8_Cff}Mtr")
    Energy = Comp(EpicsMotor,"-Ax:8_Eng}Mtr")
    Grating_Trans = Comp(EpicsMotor,"-Ax:8_GT}Mtr")
    Mirror_Pitch = Comp(EpicsMotor,"-Ax:8_MP}Mtr")
    Mirror_Pitch_off = Comp(EpicsSignal,"-Ax:8_MP}Mtr.OFF")
    Mirror_Pitch_set = Comp(EpicsSignal,"-Ax:8_MP}Mtr.SET")
    Grating_Pitch = Comp(EpicsMotor,"-Ax:8_GP}Mtr")
    Grating_Pitch_off = Comp(EpicsSignal,"-Ax:8_GP}Mtr.OFF")
    Grating_Pitch_set = Comp(EpicsSignal,"-Ax:8_GP}Mtr.SET")
    Grating_lines = Comp(EpicsSignal,"}:LINES:RBV",write_pv="}:LINES:SET",put_complete=False)
    

PGM = Monochromator("XF:21IDB-OP{Mono:1",name="PGM")
# define what is displayed from the PGM during quieries using PGM.hints.
PGM.hints = {'fields': [PGM.Energy.name,PGM.Focus_Const.name,PGM.Grating_lines.name]}



class BEST_Xaxis(Device):
    readback = Comp(EpicsSignal,"FM}:BPM0:PosX")  # Make these EpicsSignal, 'PV:...'
    setpoint = Comp(EpicsSignal,"FM}:PID:SetpointX")
    tolerance = 0.1

    def read_val(self):
        return self.get()[-1]
    
    position='yes'
    

    
    def set(self, value):
        desired_value = value
        status = DeviceStatus(self)

        def are_we_there_yet(value, *args, **kwargs):
            if abs(value[-1] - desired_value) < self.tolerance:
                # This alerts the RunEngine that it can move on.
                status._finished()
        
        # Start us moving.
        self.setpoint.put(desired_value)
        # The function are_we_there_yet will receive
        # updates from pyepics as the readback changes.
        self.readback.subscribe(are_we_there_yet)
        # Hand this back the RunEngine immediately.
        return status

class BEST_Yaxis(Device):

    readback = Comp(EpicsSignal,"FM}:BPM0:PosY")  # Make these EpicsSignal, 'PV:...'
    setpoint = Comp(EpicsSignal,"FM}:PID:SetpointY")
    tolerance = 0.1

    def read_val(self):
        return self.get()[-1]
    
    position='yes'   
        
    def set(self, value):
        desired_value = value
        status = DeviceStatus(self)
        
        def are_we_there_yet(value, *args, **kwargs):
            if abs(value[-1] - desired_value) < self.tolerance:
                # This alerts the RunEngine that it can move on.
                status._finished()
        
        # Start us moving.
        self.setpoint.put(desired_value)
        # The function are_we_there_yet will receive
        # updates from pyepics as the readback changes.
        self.readback.subscribe(are_we_there_yet)
        # Hand this back the RunEngine immediately.
        return status


class KB_pair(Device):
    VFM_Y = Comp(EpicsMotor,"Ax:A4_VFMTy}Mtr")
    VFM_Mirror_InOut = Comp(EpicsMotor,"Ax:A4_VFMTy}Mtr")
    VFM_Mirror_Trans = Comp(EpicsMotor,"Ax:A4_VFMTy}Mtr")
    VFM_Z = Comp(EpicsMotor,"Ax:A4_VFMTz}Mtr")
    VFM_Mirror_Astig = Comp(EpicsMotor,"Ax:A4_VFMTz}Mtr")
    VFM_Mirror_Horizontal = Comp(EpicsMotor,"Ax:A4_VFM_Astig}Mtr")
    VFM_Mirror_Incline = Comp(EpicsMotor,"Ax:A4_VFM_IO}Mtr")

    HFM_Z = Comp(EpicsMotor,"Ax:A4_HFM_Astig}Mtr")
    HFM_X = Comp(EpicsMotor,"Ax:A4_HFM_IO}Mtr")
    HFM_Mirror_Astig = Comp(EpicsMotor,"Ax:A4_HFM_Astig}Mtr")
    HFM_Mirror_InOut = Comp(EpicsMotor,"Ax:A4_HFM_IO}Mtr")
    HFM_Mirror_Trans = Comp(EpicsMotor,"Ax:A4_HFM_IO}Mtr")
    
    HFM_Au_Mesh = Comp(EpicsMotor,"Ax:A4_HGM}Mtr")
    VFM_Au_Mesh = Comp(EpicsMotor,"Ax:A4_VGM}Mtr")

    VFM_Rx = Comp(BEST_Xaxis,"") 
    VFM_Pitch = Comp(BEST_Xaxis,"")
    HFM_Ry = Comp(BEST_Yaxis,"")
    HFM_Pitch = Comp(BEST_Yaxis,"") 


M4A = KB_pair("XF:21IDC-OP{Mir:4A-",name="M4A")
# define what is displayed from M4A during quieries using M4A.hints.
M4A.hints = {'fields': [M4A.VFM_Y.name,M4A.VFM_Z.name,M4A.VFM_Rx.name,
                        M4A.HFM_Z.name,M4A.HFM_X.name,M4A.HFM_Ry.name]}






#
#
# ---------------------------- SLITS AND DIAGNOSTICS -----------------------------
# Slits

#
class ESM_Diagon(Device):
    H_mirror = Comp(EpicsMotor,"-Ax:3_HLPM}Mtr")
    H_Yag = Comp(EpicsMotor,"-Ax:3_HLPF}Mtr")
    V_mirror = Comp(EpicsMotor,"-Ax:3_VLPM}Mtr")
    V_Yag = Comp(EpicsMotor,"-Ax:3_VLPF}Mtr")
#

Diagon = ESM_Diagon("XF:21IDA-OP{Diag:1",name='Diagon')
# define what is displayed from Diagon during quieries using Diagon.hints.
Diagon.hints = {'fields': [Diagon.H_mirror.name,Diagon.H_Yag.name,Diagon.V_mirror.name,Diagon.V_Yag.name]}

class ESMSlit_type1(Device):
    inboard = Comp(EpicsMotor,"-Ax:I}Mtr")
    outboard = Comp(EpicsMotor,"-Ax:O}Mtr")
    bottom = Comp(EpicsMotor,"-Ax:B}Mtr")
    top = Comp(EpicsMotor,"-Ax:T}Mtr")
    h_gap = Comp(EpicsMotor,"-Ax:HG}Mtr")
    h_center = Comp(EpicsMotor,"-Ax:HC}Mtr")
    v_gap = Comp(EpicsMotor,"-Ax:VG}Mtr")
    v_center = Comp(EpicsMotor,"-Ax:VC}Mtr")
#
M1Dslit = ESMSlit_type1("XF:21IDA-OP{Mir:1-Slt:4_D_1", name='M1Dslit')
# define what is displayed from M1Dslit during quieries using M1Dslit.hints.
M1Dslit.hints = {'fields': [M1Dslit.h_gap.name,M1Dslit.h_center.name,M1Dslit.v_gap.name,M1Dslit.v_center.name]}
PGMUslit = ESMSlit_type1("XF:21IDB-OP{Mono:1-Slt:7_U_1", name='PGMUslit')
# define what is displayed from PGMUslit during quieries using PGMUslit.hints.
PGMUslit.hints = {'fields': [PGMUslit.h_gap.name,PGMUslit.h_center.name,PGMUslit.v_gap.name,PGMUslit.v_center.name]}
PGMDslit = ESMSlit_type1("XF:21IDB-OP{Mono:1-Slt:8_D_1", name='PGMDslit')
# define what is displayed from PGMDslit during quieries using PGMDslit.hints.
PGMDslit.hints = {'fields': [PGMDslit.h_gap.name,PGMDslit.h_center.name,PGMDslit.v_gap.name,PGMDslit.v_center.name]}
M4BUslit = ESMSlit_type1("XF:21IDC-OP{Mir:4B-Slt:B4_U_1", name='M4BUslit')
# define what is displayed from PGMUslit during quieries using PGMUslit.hints.
M4BUslit.hints = {'fields': [M4BUslit.h_gap.name,M4BUslit.h_center.name,M4BUslit.v_gap.name,M4BUslit.v_center.name]}

class ESMSlit_type2(Device):
    h_scan = Comp(EpicsMotor,"-Ax:HS}Mtr")
    h_apperture = Comp(EpicsMotor,"-Ax:HA}Mtr")
    v_scan = Comp(EpicsMotor,"-Ax:VS}Mtr")
    v_apperture = Comp(EpicsMotor,"-Ax:VA}Mtr")
    h_gap = Comp(EpicsMotor,"-Ax:HG}Mtr")
    h_center = Comp(EpicsMotor,"-Ax:HC}Mtr")
    v_gap = Comp(EpicsMotor,"-Ax:VG}Mtr")
    v_center = Comp(EpicsMotor,"-Ax:VC}Mtr")

M3Uslit = ESMSlit_type2("XF:21IDB-OP{Mir:3-Slt:10_U_1", name='M3Uslit')
M3Uslit.hints = {'fields': [M3Uslit.h_gap.name,M3Uslit.h_center.name,M3Uslit.v_gap.name,M3Uslit.v_center.name]}
M4AUslit = ESMSlit_type2("XF:21IDC-OP{Mir:4A-Slt:A4_U_1", name='M4AUslit')
M4AUslit.hints = {'fields': [M4AUslit.h_gap.name,M4AUslit.h_center.name,M4AUslit.v_gap.name,M4AUslit.v_center.name]}
M4BDslit = ESMSlit_type2("XF:21IDC-OP{Mir:4B-Slt:B5_D_1", name='M4BDslit')
M4BDslit.hints = {'fields': [M4BDslit.h_gap.name,M4BDslit.h_center.name,M4BDslit.v_gap.name,M4BDslit.v_center.name]}

class ExitSlit(Device):
    v_gap = Comp(EpicsMotor,"_VG}Mtr")
    h_gap = Comp(EpicsMotor,"_HG}Mtr")
    h_def = Comp(EpicsMotor,"_HDS}Mtr")
    v_def = Comp(EpicsMotor,"_VDS}Mtr")
    
ExitSlitA = ExitSlit('XF:21IDC-OP{Slt:1A-Ax:A1',name='ExitSlitA')
ExitSlitA.hints = {'fields': [ExitSlitA.h_gap.name,ExitSlitA.v_gap.name]}
ExitSlitB = ExitSlit('XF:21IDC-OP{Slt:1B-Ax:B1',name='ExitSlitB')
ExitSlitB.hints = {'fields': [ExitSlitB.h_gap.name,ExitSlitB.v_gap.name]}

#Diagnostics
class DIAG(Device):
    trans = Comp(EpicsMotor,"}Mtr")    


BTA2diag = DIAG("XF:21IDC-OP{BT:A2-Diag:A2_1-Ax:1", name= 'BTA2diag')
BTA2diag.hints = {'fields': [BTA2diag.trans.name]}
BTB2diag = DIAG("XF:21IDC-OP{BT:B2-Diag:B2_1-Ax:1", name= 'BTB2diag')
BTB2diag.hints = {'fields': [BTB2diag.trans.name]}
M3Udiag = DIAG("XF:21IDB-OP{Mir:3-Diag:10_U_1-Ax:1", name= 'M3Udiag')
M3Udiag.hints = {'fields': [M3Udiag.trans.name]}
M4AUdiag = DIAG("XF:21IDC-OP{Mir:4A-Diag:A3_U_1-Ax:1",name = 'M4AUdiag')
M4AUdiag.hints = {'fields': [M4AUdiag.trans.name]}
M4BDdiag1 = DIAG("XF:21IDC-OP{Mir:4B-Diag:B5_D_1-Ax:1",name = 'M4BDdiag1')
M4BDdiag1.hints = {'fields': [M4BDdiag1.trans.name]}
M4BDdiag2 = DIAG("XF:21IDC-OP{Mir:4B-Diag:B5_D_2-Ax:2",name = 'M4BDdiag2')
M4BDdiag2.hints = {'fields': [M4BDdiag2.trans.name]}

# --------------------------FRONT END COMPONENTS -----------------------------
# Slits

class Virtual_Size(PVPositioner):
#This is used to connect to the front end gap size PV's.
    readback = Comp(EpicsSignalRO, 't2.C')
    setpoint = Comp(EpicsSignal,'size')
    done = Comp(EpicsSignalRO,'DMOV')
    done_value = 1

class Virtual_Center(PVPositioner):
#This is used to connect to the front end gap centre PV's.
    readback = Comp(EpicsSignalRO, 't2.D')
    setpoint = Comp(EpicsSignal,'center')
    done = Comp(EpicsSignalRO,'DMOV')
    done_value = 1

class Virtual_Motor_Center_And_Gap(Device):
#This is used to combine the gap centre and size classes from above into a single class object
    h_gap = Comp(Virtual_Size,'12-Ax:X}')
    h_center = Comp(Virtual_Center,'12-Ax:X}')
    v_gap = Comp(Virtual_Size,'12-Ax:Y}')
    v_center = Comp(Virtual_Center,'12-Ax:Y}')

class Blades(Device):
#This creates a class for the independent motion of each of the front end slit "blades"
    outboard = Comp(EpicsMotor, "1-Ax:O}Mtr")
    inboard = Comp(EpicsMotor, "2-Ax:I}Mtr")
    top = Comp(EpicsMotor, "1-Ax:T}Mtr")
    bottom = Comp(EpicsMotor, "2-Ax:B}Mtr")

class Virtual_Motor_Slits(Blades, Virtual_Motor_Center_And_Gap):
#This combines the Blades and VirtualMotorCenterAndGap classes from above to create a single class for the front end slits.
    pass

    
FEslit = Virtual_Motor_Slits("FE:C21A-OP{Slt:",name='FEslit')
# define what is displayed from M1Dslit during quieries using M1Dslit.hints.
FEslit.hints = {'fields': [FEslit.h_gap.name,FEslit.h_center.name,FEslit.v_gap.name,FEslit.v_center.name]}

class TwoButtonShutter(Device):
    # TODO this needs to be fixed in EPICS as these names make no sense
    # the vlaue comingout of the PV do not match what is shown in CSS
    open_cmd = Cpt(EpicsSignal, 'Cmd:Opn-Cmd', string=True)
    # expected readback on status when open
    open_val = 'Open'

    close_cmd = Cpt(EpicsSignal, 'Cmd:Cls-Cmd', string=True)
    # expected readback on status when closed
    close_val = 'Not Open'

    permit_enabled = Cpt(EpicsSignal, 'Permit:Enbl-Sts', string=True)
    enabled = Cpt(EpicsSignal, 'Enbl-Sts', string=True)

    status = Cpt(EpicsSignalRO, 'Pos-Sts', string=True)
    fail_to_close = Cpt(EpicsSignalRO, 'Sts:FailCls-Sts', string=True)
    fail_to_open = Cpt(EpicsSignalRO, 'Sts:FailOpn-Sts', string=True)

    
    # user facing commands
    open_str = 'Open'
    close_str = 'Close'
    def set(self, val):
        if self._set_st is not None:
            raise RuntimeError('trying to set while a set is in progress')

        cmd_map = {self.open_str: self.open_cmd,
                   self.close_str: self.close_cmd}
        target_map = {self.open_str: self.open_val,
                      self.close_str: self.close_val}

        cmd_sig = cmd_map[val]
        target_val = target_map[val]

        st = self._set_st = DeviceStatus(self)
        enums = self.status.enum_strs

        def shutter_cb(value, timestamp, **kwargs):
            value = enums[int(value)]
            if value == target_val:
                self._set_st._finished()
                self._set_st = None
                self.status.clear_sub(shutter_cb)

        cmd_enums = cmd_sig.enum_strs
        count = 0
        def cmd_retry_cb(value, timestamp, **kwargs):
            nonlocal count
            

            value = cmd_enums[int(value)]
            # ts = datetime.datetime.fromtimestamp(timestamp).strftime(_time_fmtstr)
            # print('sh', ts, val, st)
            if value == 'None':
                if not st.done:
                    shutter_cb(self.status.get(as_string=False), timestamp)
                    if not st.done:
                        time.sleep(.1)

                        cmd_sig.set(1)

                        count += 1
                        if count > 1:
                            cmd_sig.clear_sub(cmd_retry_cb)
                            st._finished(success=False)
                    else:
                        cmd_sig.clear_sub(cmd_retry_cb)                            
                    
                else:
                    cmd_sig.clear_sub(cmd_retry_cb)

                    
        cmd_sig.put(1)
        cmd_sig.subscribe(cmd_retry_cb, run=False)

        self.status.subscribe(shutter_cb)


        return st

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_st = None
        self.read_attrs = ['status']

#Define the shutters from the above class.
shutter_FE = TwoButtonShutter('XF:21ID-PPS{Sh:FE}', name='shutter_FE')
shutter_FOE = TwoButtonShutter('XF:21IDA-PPS{PSh}', name='shutter_FOE')
shutter_A = TwoButtonShutter('XF:21IDC-PPS{PSh:1A}', name='shutter_A')
shutter_B = TwoButtonShutter('XF:21IDC-PPS{PSh:1B}', name='shutter_B')

#Define the beamline gatevalves from the above class.
#Section A (Inside FOE) 
BC1_GV2 = TwoButtonShutter('XF:21IDA-VA{BC:1-GV:2_D_1}', name='BC1_GV2')
Diag1_GV3 = TwoButtonShutter('XF:21IDA-VA{Diag:1-GV:3_D_1}', name='Diag1_GV3')
Mir1_GV4 = TwoButtonShutter('XF:21IDA-VA{Mir:1-GV:4_D_1}', name='Mir1_GV4')

#Section B (Between FOE and Mirror 3) 
BT6_GV6 = TwoButtonShutter('XF:21IDB-VA{BT:6-GV:6_D_1}', name='BT6_GV6')
BT7_GV7 = TwoButtonShutter('XF:21IDB-VA{BT:7-GV:7_D_1}', name='BT7_GV7')
Mono1_GV8 = TwoButtonShutter('XF:21IDB-VA{Mono:1-GV:8_D_1}', name='Mono1_GV8')
BT9_GV9 = TwoButtonShutter('XF:21IDB-VA{BT:9-GV:9_D_1}', name='BT9_GV9')
BT10_GV10 = TwoButtonShutter('XF:21IDB-VA{BT:10-GV:10_D_1}', name='BT10_GV10')

#Section C, A Branch (A Branch after Mirror 3)
Mir3_GV11A = TwoButtonShutter('XF:21IDC-VA{Mir:3-GV:11_D_A}', name='Mir:3_GV11A')
Slt1A_GVA1 = TwoButtonShutter('XF:21IDC-VA{Slt:1A-GV:A1_D_1}', name='Slt1A_GVA1')
BTA2_GVA2 = TwoButtonShutter('XF:21IDC-VA{BT:A2-GV:A2_D_1}', name='BTA2_GVA2')
BTA3_GVA3 = TwoButtonShutter('XF:21IDC-VA{BT:A3-GV:A3_D_1}', name='BTA3_GVA3')

#Section C, B Branch (B Branch after Mirror 3)
Mir3_GV11B = TwoButtonShutter('XF:21IDC-VA{Mir:3-GV:11_D_B}', name='Mir:3_GV11B')
Slt1B_GVB1 = TwoButtonShutter('XF:21IDC-VA{Slt:1B-GV:B1_D_1}', name='Slt1B_GVB1')
BTB2_GVB2 = TwoButtonShutter('XF:21IDC-VA{BT:B2-GV:B2_D_1}', name='BTB2_GVB2')
BTB3_GVB3 = TwoButtonShutter('XF:21IDC-VA{BT:B3-GV:B3_D_1}', name='BTB3_GVB3')
Mir4B_GVB4 = TwoButtonShutter('XF:21IDC-VA{Mir:4B-GV:B4_D_1}', name='Mir4B_GVB4')
BTB5_GVB5 = TwoButtonShutter('XF:21IDC-VA{BT:B5-GV:B5_D_1}', name='BTB5_GVB5')

#Section D, (A Branch endstation)
Anal1A_GVEA1 = TwoButtonShutter('XF:21IDD-VA{ANAL:1A-GV:EA1_1}', name='Anal1A_GVEA1')
