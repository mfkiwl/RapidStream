# Assume:
# 1. Use half-SLR islands
# 2. Use <4 HBM channels, from 28 to 31
# 3. Platform xilinx_u280_xdma_201920_3
set kernel_name "gaussian_kernel"
delete_pblocks anchor_region
delete_pblocks CR*

# anchor region
create_pblock anchor_region
resize_pblock anchor_region -add { SLICE_X115Y0:SLICE_X119Y719 }
resize_pblock anchor_region -add { LAGUNA_X0Y0:LAGUNA_X25Y479}
# include the SLICE right next to the laguna columns
resize_pblock anchor_region -add {
  SLICE_X9Y180:SLICE_X9Y299 SLICE_X9Y420:SLICE_X9Y539
  SLICE_X20Y180:SLICE_X20Y299 SLICE_X20Y420:SLICE_X20Y539
  SLICE_X38Y180:SLICE_X38Y299 SLICE_X38Y420:SLICE_X38Y539
  SLICE_X51Y180:SLICE_X51Y299 SLICE_X51Y420:SLICE_X51Y539
  SLICE_X64Y180:SLICE_X64Y299 SLICE_X64Y420:SLICE_X64Y539
  SLICE_X86Y180:SLICE_X86Y299 SLICE_X86Y420:SLICE_X86Y539
  SLICE_X98Y180:SLICE_X98Y299 SLICE_X98Y420:SLICE_X98Y539
  SLICE_X112Y180:SLICE_X112Y299 SLICE_X112Y420:SLICE_X112Y539
  SLICE_X125Y180:SLICE_X125Y299 SLICE_X125Y420:SLICE_X125Y539
  SLICE_X140Y180:SLICE_X140Y299 SLICE_X140Y420:SLICE_X140Y539
  SLICE_X153Y180:SLICE_X153Y299 SLICE_X153Y420:SLICE_X153Y539
  SLICE_X165Y180:SLICE_X165Y299 SLICE_X165Y420:SLICE_X165Y539
  SLICE_X183Y180:SLICE_X183Y299 SLICE_X183Y420:SLICE_X183Y539
}
# some SLICE nearby the IO columns are not included in the dynamic region
resize_pblock anchor_region -remove {SLICE_X117Y600:SLICE_X117Y719 SLICE_X117Y480:SLICE_X117Y539 SLICE_X117Y180:SLICE_X117Y239}
set_property parent pblock_dynamic_region [get_pblocks anchor_region]
set_property EXCLUDE_PLACEMENT 1 [get_pblocks anchor_region]

# define the island pblocks
create_pblock CR_X0Y8_To_CR_X3Y11
resize_pblock CR_X0Y8_To_CR_X3Y11 -add {CLOCKREGION_X0Y8:CLOCKREGION_X3Y11}
set_property parent pblock_dynamic_region [get_pblocks CR_X0Y8_To_CR_X3Y11]

create_pblock CR_X0Y4_To_CR_X3Y7
resize_pblock CR_X0Y4_To_CR_X3Y7 -add {CLOCKREGION_X0Y4:CLOCKREGION_X3Y7}
set_property parent pblock_dynamic_region [get_pblocks CR_X0Y4_To_CR_X3Y7]

create_pblock CR_X0Y0_To_CR_X3Y3
resize_pblock CR_X0Y0_To_CR_X3Y3 -add {SLICE_X0Y15:SLICE_X114Y239 BUFG_GT_X0Y24:BUFG_GT_X0Y95 BUFG_GT_SYNC_X0Y15:BUFG_GT_SYNC_X0Y59 CMACE4_X0Y0:CMACE4_X0Y1 DSP48E2_X0Y0:DSP48E2_X15Y89 GTYE4_CHANNEL_X0Y4:GTYE4_CHANNEL_X0Y15 GTYE4_COMMON_X0Y1:GTYE4_COMMON_X0Y3 LAGUNA_X0Y0:LAGUNA_X15Y119 PCIE4CE4_X0Y0:PCIE4CE4_X0Y1 RAMB18_X0Y6:RAMB18_X7Y95 RAMB36_X0Y3:RAMB36_X7Y47 URAM288_X0Y4:URAM288_X1Y63 SLICE_X11Y0:SLICE_X12Y14}
set_property parent pblock_dynamic_region [get_pblocks CR_X0Y0_To_CR_X3Y3]

# leave a 1-CR column gap for hmss
create_pblock CR_X4Y0_To_CR_X7Y3
resize_pblock CR_X4Y0_To_CR_X7Y3 -add {
  URAM288_X4Y16:URAM288_X4Y63 URAM288_X2Y4:URAM288_X3Y63 RAMB36_X11Y12:RAMB36_X11Y47 RAMB36_X8Y3:RAMB36_X10Y47 RAMB18_X11Y24:RAMB18_X11Y95 RAMB18_X8Y6:RAMB18_X10Y95 DSP48E2_X25Y18:DSP48E2_X27Y89 DSP48E2_X16Y0:DSP48E2_X24Y89 SLICE_X183Y60:SLICE_X191Y239 SLICE_X182Y60:SLICE_X182Y179 SLICE_X176Y60:SLICE_X181Y239 SLICE_X165Y15:SLICE_X175Y239 SLICE_X164Y15:SLICE_X164Y179 SLICE_X153Y15:SLICE_X163Y239 SLICE_X152Y15:SLICE_X152Y179 SLICE_X140Y15:SLICE_X151Y239 SLICE_X139Y15:SLICE_X139Y179 SLICE_X125Y15:SLICE_X138Y239 SLICE_X124Y15:SLICE_X124Y179 SLICE_X117Y15:SLICE_X123Y239
}
set_property parent pblock_dynamic_region [get_pblocks CR_X4Y0_To_CR_X7Y3]

create_pblock CR_X4Y4_To_CR_X7Y7
resize_pblock CR_X4Y4_To_CR_X7Y7 -add {
  URAM288_X2Y64:URAM288_X4Y127 RAMB36_X8Y48:RAMB36_X11Y95 RAMB18_X8Y96:RAMB18_X11Y191 DSP48E2_X28Y114:DSP48E2_X28Y161 DSP48E2_X16Y90:DSP48E2_X27Y185 SLICE_X192Y300:SLICE_X198Y419 SLICE_X183Y240:SLICE_X191Y479 SLICE_X182Y300:SLICE_X182Y419 SLICE_X165Y240:SLICE_X181Y479 SLICE_X164Y300:SLICE_X164Y419 SLICE_X153Y240:SLICE_X163Y479 SLICE_X152Y300:SLICE_X152Y419 SLICE_X140Y240:SLICE_X151Y479 SLICE_X139Y300:SLICE_X139Y419 SLICE_X125Y240:SLICE_X138Y479 SLICE_X124Y300:SLICE_X124Y419 SLICE_X117Y240:SLICE_X123Y479
}
set_property parent pblock_dynamic_region [get_pblocks CR_X4Y4_To_CR_X7Y7]

create_pblock CR_X4Y8_To_CR_X7Y11
resize_pblock CR_X4Y8_To_CR_X7Y11 -add {
  URAM288_X2Y128:URAM288_X4Y191 RAMB36_X8Y96:RAMB36_X11Y143 RAMB18_X8Y192:RAMB18_X11Y287 DSP48E2_X28Y210:DSP48E2_X28Y281 DSP48E2_X16Y186:DSP48E2_X27Y281 SLICE_X195Y540:SLICE_X200Y719 SLICE_X194Y540:SLICE_X194Y659 SLICE_X192Y540:SLICE_X193Y719 SLICE_X183Y480:SLICE_X191Y719 SLICE_X182Y540:SLICE_X182Y659 SLICE_X165Y480:SLICE_X181Y719 SLICE_X164Y540:SLICE_X164Y659 SLICE_X153Y480:SLICE_X163Y719 SLICE_X152Y540:SLICE_X152Y659 SLICE_X140Y480:SLICE_X151Y719 SLICE_X139Y540:SLICE_X139Y659 SLICE_X125Y480:SLICE_X138Y719 SLICE_X124Y540:SLICE_X124Y659 SLICE_X117Y480:SLICE_X123Y719
}
set_property parent pblock_dynamic_region [get_pblocks CR_X4Y8_To_CR_X7Y11]

set island_pblocks {
  CR_X0Y8_To_CR_X3Y11
  CR_X0Y4_To_CR_X3Y7
  CR_X0Y0_To_CR_X3Y3
  CR_X4Y0_To_CR_X7Y3
  CR_X4Y4_To_CR_X7Y7
  CR_X4Y8_To_CR_X7Y11
}

foreach island $island_pblocks {
  # exclude the anchor regions from the island pblocks
  resize_pblock ${island} -remove [get_property DERIVED_RANGES [get_pblocks anchor_region]]
  resize_pblock ${island} -remove [get_property DERIVED_RANGES [get_pblocks base_region]]
}

# somehow these speical blocks will be left out of the island pblock
# as a result, the adjacent SLICE columns are also left out if we do not add them back
resize_pblock CR_X0Y0_To_CR_X3Y3 -add {CMACE4_X0Y0:CMACE4_X0Y1 PCIE4CE4_X0Y1:PCIE4CE4_X0Y1}
resize_pblock CR_X0Y4_To_CR_X3Y7 -add {CMACE4_X0Y2:CMACE4_X0Y4 ILKNE4_X0Y0:ILKNE4_X0Y0}
resize_pblock CR_X0Y8_To_CR_X3Y11 -add {CMACE4_X0Y5:CMACE4_X0Y7 ILKNE4_X0Y2:ILKNE4_X0Y2}

# assign island to pblocks
set base_addr pfm_top_i/dynamic_region/${kernel_name}/inst
add_cells_to_pblock anchor_region [get_cells ${base_addr}] -clear_locs
foreach island $island_pblocks {
  add_cells_to_pblock ${island}  [get_cells ${base_addr}/WRAPPER_VERTEX_${island}] -clear_locs
}
