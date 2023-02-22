
# Wafer socket protocol

# Once the socket room was created
# System reads 8192 bytes from the client
# If it starts with "WFRS" (WaFer Regular Sockets)
# Then it means that the client is not WSS
# OTHERWISE it's automatically assumed that client IS WSS








import multiprocessing, threading, os, sys
from pathlib import Path
import p_mods.wafer_sys
thisdir = Path(__file__).parent.absolute()
sys.path.append(str(thisdir.parent / 'web' / 'htbin'))
# from server_config import data as srv_cfg



wafer_config_ctrl = wafer_sys.wfcfg_ctrl(thisdir / 'sysc', thisdir.parent)

wafer_sys_util = wafer_sys.wf_sys_util(wafer_config_ctrl)














