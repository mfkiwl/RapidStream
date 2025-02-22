set anchor_regs [get_pins pfm_top_i/dynamic_region/gaussian_kernel/inst/*q_reg*/D]
set anchor_reg_D_pins [get_pins pfm_top_i/dynamic_region/gaussian_kernel/inst/*q_reg*/D]
set anchor_reg_D_nets [get_nets -segments -of_objects $anchor_reg_D_pins]
set placeholder_Q_pins [get_pins -of_objects $anchor_reg_D_nets -filter {name =~ *Q}]
set placeholder_regs [get_cells -of_objects ${placeholder_Q_pins} ]
disconnect_net -objects [get_pins -of_objects ${placeholder_regs} -filter {NAME =~ *D}]
route_design -nets [get_nets pfm_top_i/dynamic_region/gaussian_kernel/*]
