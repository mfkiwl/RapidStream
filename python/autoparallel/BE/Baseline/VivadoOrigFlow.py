import argparse
import json
import logging
import os
import re

from autoparallel.BE.Utilities import loggingSetup

loggingSetup()


def getVivadoFlowWithOrigRTL(
  fpga_part_name,
  orig_rtl_path,
  top_name
):
  script = []

  script.append(f'set_param general.maxThreads 8')

  # to differentiate with the original top
  script.append(f'set_part {fpga_part_name}')

  # read in the original RTLs by HLS
  script.append(f'set ORIG_RTL_PATH "{orig_rtl_path}"') 
  script.append(r'set orig_rtl_files [glob ${ORIG_RTL_PATH}/*.v]') 
  script.append(r'read_verilog ${orig_rtl_files}') 

  # read in the generated wrappers
  script.append(f'set wrapper_files [glob {wrapper_path}/*.v]') 
  script.append(r'read_verilog ${wrapper_files}') 

  # instantiate IPs used in the RTL. Use "-nocomplain" in case no IP is used
  script.append(r'set orig_ip_files [glob -nocomplain ${ORIG_RTL_PATH}/*.tcl]') 
  script.append(r'foreach ip_tcl ${orig_ip_files} { source ${ip_tcl} }') 

  # clock xdc
  script.append(f'read_xdc "{baseline_dir}/clock.xdc"')

  script.append(f'synth_design -top "{top_name}" -mode out_of_context')
  script.append(f'write_checkpoint synth.dcp')

  script.append(f'opt_design')
  script.append(f'write_checkpoint synth-opt.dcp')

  script.append(f'place_design -directive Explore')
  script.append(f'write_checkpoint place.dcp')

  script.append(f'phys_opt_design')
  script.append(f'write_checkpoint place-opt.dcp')

  script.append(f'route_design -directive Explore')
  script.append(f'write_checkpoint route.dcp')

  script.append(f'phys_opt_design')
  script.append(f'write_checkpoint route-opt.dcp')

  return script


def createClockFromBUFGXDC(target_period=2.50):
  xdc = []
  xdc.append(f'create_clock -name ap_clk -period {target_period} [get_pins test_bufg/O]')
  return xdc


def createSlotWrappers():
  slot_name_to_rtl = hub['SlotWrapperRTL']
  for slot_name, rtl in slot_name_to_rtl.items():
    # remove all annotations because those are for the split compile flow
    rtl = [re.sub(r"\(\*.+\*\)", "", line) for line in rtl]

    open(f'{wrapper_path}/{slot_name}.v', 'w').write('\n'.join(rtl))

  top_rtl = hub['NewTopRTL']
  open(f'{wrapper_path}/new_top.v', 'w').write(top_rtl)


def getNonPipelinedTopWithBUFG():
  """
  run the original HLS design. However we need to add the BUFG into the top for fair comparison
  """
  orig_rtl_path = hub['ORIG_RTL_PATH']
  orig_rtl_top = open(f'{orig_rtl_path}/{orig_top_name}.v').read()

  orig_rtl_top = re.sub(f'module {orig_top_name}', f'module {orig_top_name_with_bufg}', orig_rtl_top)
  orig_rtl_top = orig_rtl_top.replace('ap_clk,', 'ap_clk_port,')

  bufg_connect = 'input   ap_clk_port; wire ap_clk;  '
  bufg_annotation = '(* DONT_TOUCH = "yes", LOC = "BUFGCE_X0Y194" *)'
  bufg_def = 'BUFGCE test_bufg (.I(ap_clk_port), .CE(1\'b1),.O(ap_clk) );'
  orig_rtl_top = re.sub(r'input[ ]+ap_clk;', f'{bufg_connect} {bufg_annotation} {bufg_def}', orig_rtl_top)

  open(f'{wrapper_path}/orig_top_with_bufg.v', 'w').write(orig_rtl_top)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--hub_path", type=str, required=True)
  parser.add_argument("--base_dir", type=str, required=True)
  parser.add_argument("--vivado_version", type=str, required=True)
  args = parser.parse_args()

  hub_path = args.hub_path
  base_dir = args.base_dir

  hub = json.loads(open(hub_path, 'r').read())

  NEW_TOP_MODULE_SUFFIX = '_hw_test'
  top_rtl = hub['NewTopRTL']
  pipeline_top_name = re.search(rf'[^ ]+{NEW_TOP_MODULE_SUFFIX}', top_rtl).group(0)
  orig_top_name = pipeline_top_name.replace(NEW_TOP_MODULE_SUFFIX, '')
  orig_top_name_with_bufg = f'{orig_top_name}_non_pipeline_with_bufg'

  baseline_dir = f'{base_dir}/baseline_orig_vivado'
  os.mkdir(baseline_dir)
  
  wrapper_path = f'{baseline_dir}/wrappers'
  os.mkdir(wrapper_path)

  xdc = createClockFromBUFGXDC()
  open(f'{baseline_dir}/clock.xdc', 'w').write('\n'.join(xdc))

  os.mkdir(f'{baseline_dir}/pipelined_baseline')
  script = getVivadoFlowWithOrigRTL(hub['FPGA_PART_NAME'], hub['ORIG_RTL_PATH'], pipeline_top_name)
  open(f'{baseline_dir}/pipelined_baseline/baseline_pipelined.tcl', 'w').write('\n'.join(script))

  os.mkdir(f'{baseline_dir}/non_pipelined_baseline')
  script = getVivadoFlowWithOrigRTL(hub['FPGA_PART_NAME'], hub['ORIG_RTL_PATH'], orig_top_name_with_bufg)
  open(f'{baseline_dir}/non_pipelined_baseline/baseline_non_pipelined.tcl', 'w').write('\n'.join(script))

  createSlotWrappers()
  getNonPipelinedTopWithBUFG()