from ophyd import EpicsSignal, EpicsSignalRO, EpicsMotor
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# SR current
# CNT012 src  SRcur  SR:C03-BI{DCCT:1}I:Real-I
SRcur = EpicsSignalRO('SR:C03-BI{DCCT:1}I:Real-I', name='SRcur')

#epu1_gap = PVPositioner('XF:23ID-ID{EPU:1-Ax:Gap}Pos-SP',
#                        readback='XF:23ID-ID{EPU:1-Ax:Gap}Pos-I',
#                        stop='SR:C23-ID:G1A{EPU:1-Ax:Gap}-Mtr.STOP',
#                        stop_val=1,
#                        put_complete=True,
#                        name='epu1_gap')

# Loadlock Feeder pos and readback low_limit high_limit
#llf = EpicsMotor('XF:21IDC-ES{SH:proto-Ax:F}Mtr', read_attrs=['user_readback','user_setpoint','motor_is_moving','motor_done_move','motor_stop'],name='llf')
#print("\n\n\tAre PVs connected to IOCs?")
#if llf.connected == False:
#	print(bcolors.FAIL + "\t*** ---------------- ***" + bcolors.ENDC)
#	print(bcolors.FAIL + "\t*   Not connected!!!   *" + bcolors.ENDC)
#	print(bcolors.FAIL + "\t*** ---------------- ***" + bcolors.ENDC)
#else:
#	print(bcolors.OKGREEN + "Connected" + bcolors.ENDC);
#llf.user_setpoint.limits[1]
#llf_llm = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:F}Mtr.LLM', name='llf_llm')
#llf.user_setpoint.limits[0]
#llf_hlm = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:F}Mtr.HLM', name='llf_hlm')

#llfv = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:F}Mtr.VAL', name='llfv')
#llfr = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:F}Mtr.RBV', name='llfr')

# Loadlock Manip pos and readback low_limit high_limit
#llt = EpicsMotor('XF:21IDC-ES{SH:proto-Ax:T}Mtr', read_attrs=['user_readback','user_setpoint','motor_is_moving','motor_done_move','motor_stop'],name='llt')
#llt_llm = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:T}Mtr.LLM', name='llt_llm')
#llt_hlm = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:T}Mtr.HLM', name='llt_hlm')

#lltv = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:T}Mtr.VAL', name='lltv')
#lltr = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:T}Mtr.RBV', name='lltr')

# Loadlock Claw pos and readback low_limit high_limit
#llc = EpicsMotor('XF:21IDC-ES{SH:proto-Ax:C}Mtr', name='llc')
#llcv = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:C}Mtr.VAL', name='llcv')
#llcr = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:C}Mtr.RBV', name='llcr')
#llc_llm = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:C}Mtr.LLM', name='llc_llm')
#llc_hlm = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:C}Mtr.HLM', name='llc_hlm')

# Loadlock Rotate pos and readback low_limit high_limit
#llr = EpicsMotor('XF:21IDC-ES{SH:proto-Ax:R}Mtr', name='llr')
#llrv = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:R}Mtr.VAL', name='llrv')
#llrr = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:R}Mtr.RBV', name='llrr')
#llr_llm = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:R}Mtr.LLM', name='llc_rlm')
#llr_hlm = EpicsSignal('XF:21IDC-ES{SH:proto-Ax:R}Mtr.HLM', name='llc_rlm')

