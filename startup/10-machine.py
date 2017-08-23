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

LL = LL_mtr('XF:21IDD-ES{LL:',read_attrs = MR_attrs, name='LL')


#
# ---------------------------- LOW_TEMP Chamber -----------------------------
# Low_temp chamber:
#
class LT_mtr(Device):
   X = Comp(EpicsMotor,"-Ax:X}Mtr")
   Y = Comp(EpicsMotor,"-Ax:Y}Mtr")
   Z = Comp(EpicsMotor,"-Ax:Z}Mtr")
   Ry =  Comp(EpicsMotor,"-Ax:Ry}Mtr")

LT = LT_mtr('XF:21IDD-ES{LT:1-Manip:EA5_1',read_attrs = MR_attrs, name='LT')



# ---------------------------- SAMPLE_PREP Chamber -----------------------------
# Sample_prep chamber:
#
class SP_mtr(Device):
    X = Comp(EpicsMotor,"-Ax:X}Mtr")
    Y = Comp(EpicsMotor,"-Ax:Y}Mtr")
    Z = Comp(EpicsMotor,"-Ax:Z}Mtr")
    Rx = Comp(EpicsMotor,"-Ax:Rx}Mtr")

SP = SP_mtr('XF:21IDD-ES{SP:1-Manip:EA2_1',read_attrs = MR_attrs, name='SP')


#
#
# ---------------------------- ANALYSIS Chamber -----------------------------
# Analysis chamber:
#

class An_mtr(Device):

    #Add micro-scanning stage motors here when done
    Claw_Trans = Comp(EpicsMotor,"{ST:1-Claw:EA1_1-Ax:T}Mtr")
    Claw_Grab = Comp(EpicsMotor,"{ST:1-Claw:EA1_1-Ax:C}Mtr")

An = An_mtr("XF:21IDD-ES",read_attrs = MR_attrs, name='An')

#
#
# ---------------------------- Scienta Analyzer -----------------------------
# Scienta Analyzer:
#

class Analyzer_mtr(Device):
    Rz = Comp(EpicsMotor,"{SA:1-DPRF:EA1_1-Ax:1}Mtr")

SA = Analyzer_mtr("XF:21IDD-ES",read_attrs = MR_attrs, name='SA')

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
M4B = Hexapod_Mir("XF:21IDC-OP{Mir:4B-Ax:B4",name="M4B")

class Monochromator(Device):
    Focus_Const = Comp(EpicsMotor,"-Ax:8_Cff}Mtr")
    Energy = Comp(EpicsMotor,"-Ax:8_Eng}Mtr")
    Grating_Trans = Comp(EpicsMotor,"-Ax:8_GT}Mtr")
    Mirror_Pitch = Comp(EpicsMotor,"-Ax:8_MP}Mtr")
    Mirror_Pitch_off = Comp(EpicsSignal,"-Ax:8_MP}Mtr.OFF")
    Grating_Pitch = Comp(EpicsMotor,"-Ax:8_GP}Mtr")
    Grating_Pitch_off = Comp(EpicsSignal,"-Ax:8_GP}Mtr.OFF")
    Grating_lines = Comp(EpicsSignal,"}:LINES:SET")

PGM = Monochromator("XF:21IDB-OP{Mono:1",name="PGM")


class KB_pair(Device):
    VFM_Y = Comp(EpicsMotor,"VFMTy}Mtr")
    VFM_Mirror_InOut = Comp(EpicsMotor,"VFMTy}Mtr")
    VFM_Mirror_Trans = Comp(EpicsMotor,"VFMTy}Mtr")
    VFM_Z = Comp(EpicsMotor,"VFMTz}Mtr")
    VFM_Mirror_Astig = Comp(EpicsMotor,"VFMTz}Mtr")
    VFM_Mirror_Horizontal = Comp(EpicsMotor,"VFM_Astig}Mtr")
    VFM_Mirror_Incline = Comp(EpicsMotor,"VFM_IO}Mtr")

    HFM_Z = Comp(EpicsMotor,"HFM_Astig}Mtr")
    HFM_X = Comp(EpicsMotor,"HFM_IO}Mtr")
    HFM_Mirror_Astig = Comp(EpicsMotor,"HFM_Astig}Mtr")
    HFM_Mirror_InOut = Comp(EpicsMotor,"HFM_IO}Mtr")
    HFM_Mirror_Trans = Comp(EpicsMotor,"HFM_IO}Mtr")
    
    HFM_Au_Mesh = Comp(EpicsMotor,"HGM}Mtr")
    VFM_Au_Mesh = Comp(EpicsMotor,"VGM}Mtr")
    

M4A = KB_pair("XF:21IDC-OP{Mir:4A-Ax:A4_",name="M4A")    

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
PGMUslit = ESMSlit_type1("XF:21IDB-OP{Mono:1-Slt:7_U_1", name='PGMUslit')
PGMDslit = ESMSlit_type1("XF:21IDB-OP{Mono:1-Slt:8_D_1", name='PGMDslit')
M4BUslit = ESMSlit_type1("XF:21IDC-OP{Mir:4B-Slt:B4_U_1", name='M4BUslit')

class ESMSlit_type2(Device):
    h_scan = Comp(EpicsMotor,"-Ax:HS}Mtr")
    h_apperture = Comp(EpicsMotor,"-Ax:HA}Mtr")
    v_scan = Comp(EpicsMotor,"-Ax:VS}Mtr")
    v_aperture = Comp(EpicsMotor,"-Ax:VA}Mtr")
    h_gap = Comp(EpicsMotor,"-Ax:HG}Mtr")
    h_center = Comp(EpicsMotor,"-Ax:HC}Mtr")
    v_gap = Comp(EpicsMotor,"-Ax:VG}Mtr")
    v_center = Comp(EpicsMotor,"-Ax:VC}Mtr")

M3Uslit = ESMSlit_type2("XF:21IDB-OP{Mir:3-Slt:10_U_1", name='M3Uslit')
M4AUslit = ESMSlit_type2("XF:21IDC-OP{Mir:4A-Slt:A4_U_1", name='M4AUslit')
M4BDslit = ESMSlit_type2("XF:21IDC-OP{Mir:4B-Slt:B5_D_1", name='M4BDslit')

class ExitSlit(Device):
    v_gap = Comp(EpicsMotor,"_VG}Mtr")
    h_gap = Comp(EpicsMotor,"_HG}Mtr")
    h_def = Comp(EpicsMotor,"_HDS}Mtr")
    v_def = Comp(EpicsMotor,"_VDS}Mtr")
    
ExitSlitA = ExitSlit('XF:21IDC-OP{Slt:1A-Ax:A1',name='ExitSlitA')
ExitSlitB = ExitSlit('XF:21IDC-OP{Slt:1B-Ax:B1',name='ExitSlitB')

#Diagnostics
class DIAG(Device):
    trans = Comp(EpicsMotor,"}Mtr")    


BTA2diag = DIAG("XF:21IDC-OP{BT:A2-Diag:A2_1-Ax:1", name= 'BTA2diag')
BTB2diag = DIAG("XF:21IDC-OP{BT:B2-Diag:B2_1-Ax:1", name= 'BTB2diag')
M3Udiag = DIAG("XF:21IDB-OP{Mir:3-Diag:10_U_1-Ax:1", name= 'M3Udiag')
M4AUdiag = DIAG("XF:21IDC-OP{Mir:4A-Diag:A3_U_1-Ax:1",name = 'M4AUdiag')
M4BDdiag1 = DIAG("XF:21IDC-OP{Mir:4B-Diag:B5_D_1-Ax:1",name = 'M4BDdiag1')
M4BDdiag2 = DIAG("XF:21IDC-OP{Mir:4B-Diag:B5_D_2-Ax:2",name = 'M4BDdiag2')

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

class TwoButtonShutter(Device:)
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
            count += 1
            if count > 5:
                cmd_sig.clear_sub(cmd_retry_cb)
                st._finished(success=False)
            if value == 'None':
                if not st.done:
                    time.sleep(.5)
                    cmd_sig.set(1)
                    ts = datetime.datetime.fromtimestamp(timestamp).strftime(_time_fmtstr)
                    print('** ({}) Had to reactuate shutter while {}ing'.format(ts, val))
                else:
                    cmd_sig.clear_sub(cmd_retry_cb)

        cmd_sig.subscribe(cmd_retry_cb, run=False)
        cmd_sig.set(1)
        self.status.subscribe(shutter_cb)


        return st

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_st = None
        self.read_attrs = ['status']

shutter = TwoButtonShutter('XF:21ID-PPS{Sh:FE}', name='shutter')
shutter_A = TwoButtonShutter('XF:21ID-PPS{Sh:1A}', name='shutterA')
gate1 = TwoButtonShutter('XF:21IDA-VA{Mir:1-GV:4_D_1}', name='gate1')
