import click
import json
import os
import shutil
from collections import defaultdict
from typing import Dict, List

from .util import ParallelManager, get_local_anchor_list, RAPIDSTREAM_BASE_PATH
from .floorplan_const import get_neighbor_slice_site_of_laguna_site


def setup_island_placement_opt_inner(
    config: Dict,
    init_place_dir: str,
    anchor_place_dir: str,
    place_opt_dir: str,
    top_name: str,
    rerun_placement: bool,
):
  """"""

  anchor_place_dir = os.path.abspath(anchor_place_dir)
  init_place_dir = os.path.abspath(init_place_dir)
  place_opt_dir = os.path.abspath(place_opt_dir)

  if os.path.exists(place_opt_dir):
    shutil.rmtree(place_opt_dir)

  os.mkdir(place_opt_dir)

  # collect all anchor locations
  anchor_to_loc = collect_all_anchor_locs(anchor_place_dir)

  mng = ParallelManager()
  for slot_name in config['vertices'].keys():
    os.mkdir(f'{place_opt_dir}/{slot_name}')
    script = get_island_opt_script(
      config, top_name, slot_name, anchor_to_loc, init_place_dir, place_opt_dir, rerun_placement,
    )
    open(f'{place_opt_dir}/{slot_name}/island_phys_opt.tcl', 'w').write('\n'.join(script))
    mng.add_task(f'{place_opt_dir}/{slot_name}/', 'island_phys_opt.tcl')

  open(f'{place_opt_dir}/parallel.txt', 'w').write('\n'.join(mng.get_parallel_script()))


def collect_all_anchor_locs(anchor_place_dir: str) -> Dict[str, str]:
  anchor_to_loc = {}
  for root, dirs, files in os.walk(anchor_place_dir):
    for file in files:
      if file.endswith('json'):
        local_anchor_to_loc = json.loads(open(f'{root}/{file}', 'r').read())
        anchor_to_loc.update(local_anchor_to_loc)
  return anchor_to_loc


def get_local_anchor_to_loc(
    config: Dict,
    slot_name: str,
    anchor_to_loc: Dict[str, str],
) -> Dict[str, str]:
  local_anchor_to_loc = {}
  for orientation in config['vertices'][slot_name]['orientation_to_wire'].keys():
    _local_anchor_list = get_local_anchor_list(config, slot_name, orientation)
    local_anchor_to_loc.update(
      {anchor: anchor_to_loc[anchor] for anchor in _local_anchor_list}
    )
  return local_anchor_to_loc


def map_laguna_anchors_to_slice(anchor_to_loc: Dict[str, str]) -> Dict[str, str]:
  """A laguna site can hold up to 24 sll connections, but the nearby SLICE that
    share the same INT can only hold up to 16 FFs. Thus if the right side SLICE is full,
    we map to the SLICE on the left side
  """
  anchor_to_slice_loc = {}
  slice_counter = defaultdict(int)
  for anchor, loc in anchor_to_loc.items():
    if loc.startswith('LAGUNA'):
      loc_right, loc_left = get_neighbor_slice_site_of_laguna_site(loc)
      if slice_counter[loc_right] < 16:
        loc = loc_right
      else:
        loc = loc_left
      slice_counter[loc] += 1
    anchor_to_slice_loc[anchor] = loc
  return anchor_to_slice_loc


def get_island_opt_script(
  config: Dict,
  top_name: str,
  slot_name: str,
  anchor_to_loc: Dict[str, str],
  init_place_dir: str,
  place_opt_dir: str,
  rerun_placement: bool,
) -> List[str]:
  script = []

  local_anchor_to_loc = get_local_anchor_to_loc(config, slot_name, anchor_to_loc)

  kernel_cell_addr = f'pfm_top_i/dynamic_region/{top_name}/inst/{slot_name}/'
  local_anchor_to_loc = {kernel_cell_addr + anchor : loc for anchor, loc in local_anchor_to_loc.items()}

  script.append(f'open_checkpoint {init_place_dir}/{slot_name}/{slot_name}_place.dcp')

  if rerun_placement:
    # map laguna anchors to nearby slice sites
    # avoid connectitivy DRC in place_design
    local_anchor_to_loc = map_laguna_anchors_to_slice(local_anchor_to_loc)
    script.append('place_design -unplace')
  else:
    # remove the location of anchors from last iteration
    script.append('unplace_cell { \\')
    for anchor in local_anchor_to_loc.keys():
      script.append(f'  {anchor} \\')
    script.append('}')

  # dictate the location for each anchor
  script.append('place_cell { \\')
  for anchor, loc in local_anchor_to_loc.items():
    script.append(f'  {anchor} {loc} \\')
  script.append('}')

  if rerun_placement:
    script.append('place_design')
  else:
    script.append('phys_opt_design')

  # extract locations of src and dst of each anchor
  script.append(f'set kernel_cell_addr "{kernel_cell_addr}"')
  script.append(f'source {RAPIDSTREAM_BASE_PATH}/tcl/extractSrcAndDstOfAnchors.tcl')

  script.append(f'write_checkpoint {place_opt_dir}/{slot_name}/{slot_name}_island_and_anchor_place.dcp')

  kernel_cell = kernel_cell_addr.strip('/')
  script.append('delete_pblocks *') # remove the pblock on the island
  script.append(f'write_checkpoint -cell {kernel_cell}/{slot_name} {place_opt_dir}/{slot_name}/{slot_name}_island_place.dcp')

  return script
