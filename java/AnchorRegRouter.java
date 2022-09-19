/*
 * Copyright (c) 2022 Xilinx, Inc.
 * All rights reserved.
 *
 * Author: Chris Lavin, Xilinx Research Labs.
 *
 * This file is part of RapidWright.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
/**
 *
 */
package com.xilinx.rapidwright.rwroute;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import com.xilinx.rapidwright.design.Cell;
import com.xilinx.rapidwright.design.ConstraintGroup;
import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.DesignTools;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.design.blocks.PBlock;
import com.xilinx.rapidwright.design.blocks.PBlockRange;
import com.xilinx.rapidwright.device.Device;
import com.xilinx.rapidwright.device.Node;
import com.xilinx.rapidwright.device.PIP;
import com.xilinx.rapidwright.device.SiteTypeEnum;
import com.xilinx.rapidwright.device.Tile;
import com.xilinx.rapidwright.edif.EDIFHierPortInst;
import com.xilinx.rapidwright.edif.EDIFPortInst;
import com.xilinx.rapidwright.edif.EDIFTools;


/**
 * Created on: Aug 22, 2022
 */
public class AnchorRegRouter {

    // get all the site pins of the anchor registers to be routed to
    // we can easily get all the cell pins to be routed to, but we need the site pins as well
    private static Map<SitePinInst, EDIFHierPortInst> anchorRegPinsToRoute(Design design) {
        Set<EDIFHierPortInst> gndPins = new HashSet<>(design.getNetlist().getPhysicalGndPins());
        Set<EDIFHierPortInst> vccPins = new HashSet<>(design.getNetlist().getPhysicalVccPins());

        // for each target pin, we need to know its SitePinInst
        // we also need to know the port instance on the island that the anchor connects to
        // we will add the partition pins onto the island port instances
        Map<SitePinInst, EDIFHierPortInst> mapAnchorPinToIslandPort = new HashMap<>();

        for(Cell c : design.getCells()) {
            if(c.getName().startsWith("pfm_top_i/dynamic_region/gaussian_kernel/inst/") && c.getName().contains("_q_reg")) {

                // the logical pin name
                for(String pin : c.getPinMappingsP2L().values()) {
                	// skip clock net
                	if (!pin.equals("D") && !pin.equals("Q")) {
                		continue;
                	}

                    EDIFHierPortInst portInst = design.getNetlist().getHierPortInstFromName(c.getName() + EDIFTools.EDIF_HIER_SEP + pin);

                    // get the net that connects to the pin
                    String netName = design.getNetlist().getParentNet(portInst.getHierarchicalNet()).toString();
                    Net net = design.getNet(netName);

                    // if the pin is connected to physical nets
                    if(net == null) {
                        if(gndPins.contains(portInst)) net = design.getGndNet();
                        else if(vccPins.contains(portInst)) net = design.getVccNet();
                    }

                    // Gets the site pin that is currently routed to the specified cell pin.
                    String sitePinName = DesignTools.getRoutedSitePin(c, net, pin);
                    SitePinInst pinInst = c.getSiteInst().getSitePinInst(sitePinName);
                    if(pinInst == null) {
                        pinInst = net.createPin(sitePinName, c.getSiteInst());
                    }

                    // get the PortInst on the island wrapper
                    // first get the wrapper pin name
                    Collection<EDIFPortInst> portList = portInst.getNet().getPortInsts();

                    for (EDIFPortInst port: portList) {
                    	// check if the port belongs to a hierarchical cell
                    	// in theory there should be only 3 ports on the anchor net
                    	// the anchor Q/D port; the sink/src D/Q port; the hier port on the island
                    	if (!port.getCellInst().getCellType().isLeafCellOrBlackBox()) {
                    		String hierName = "pfm_top_i/dynamic_region/gaussian_kernel/inst/" + port.toString();
                    		EDIFHierPortInst islandPortInst = design.getNetlist().getHierPortInstFromName(hierName);
                    		mapAnchorPinToIslandPort.put(pinInst, islandPortInst);
                    	}
                    }
                }
            }
        }
        return mapAnchorPinToIslandPort;
    }

    private static Map<String, PBlock> getPBlocksFromXDC(Design design){
        Device device = design.getDevice();
        Map<String,PBlock> pblockMap = new HashMap<>();
        for(ConstraintGroup cg : ConstraintGroup.values()) {
            for(String line : design.getXDCConstraints(cg)) {
                if(line.trim().startsWith("resize_pblock")) {
                    String[] parts = line.split("\\s+");
                    String pblockName = null;
                    String pblockRange = null;
                    boolean nextIsName = false;
                    boolean nextIsRange = false;
                    for(String part : parts) {
                        if(part.contains("get_pblocks")) {
                            nextIsName = true;
                        }else if(nextIsName) {
                            nextIsName = false;
                            pblockName = part.replace("]", "").replace("}", "");
                        }else if(part.contains("-add")) {
                            nextIsRange = true;
                        }else if(nextIsRange) {
                            pblockRange = part.replace("{", "").replace("}", "").replace("]", "");
                            PBlock pblock = pblockMap.computeIfAbsent(pblockName, name -> new PBlock(name));
                            pblock.add(new PBlockRange(device, pblockRange));
                        }
                    }
                }

            }
        }
        return pblockMap;
    }


    private static String getPblockNameOfTile(HashMap<String, Set<Tile> > pblockNameToTiles, Tile t) {
        for (Map.Entry<String, Set<Tile> > e : pblockNameToTiles.entrySet()) {
            if (e.getValue().contains(t)) {
                return e.getKey();
            }
        }
        return null;

    }

    private static boolean isDirectionNode(Node n) {
    	switch (n.getIntentCode()) {
    	case NODE_SINGLE:
    	case NODE_DOUBLE:
    	case NODE_HQUAD:
    	case NODE_VQUAD:
    	case NODE_HLONG:
    	case NODE_VLONG:
    		String name = n.toString();
    		if (name.contains("/EE") || name.contains("/SS") || name.contains("/WW") || name.contains("/NN")) {
    			return true;
    		}
    		else {
    			return false;
    		}
    	default:
    		return false;
    	}
    }

    private static boolean isValidNodeForPartPin(
    		Node n,
    		String targetPblock,
    		HashMap<String, Set<Tile> > pblockNameToTiles,
    		Map<Node, Node> connections
    ) {
    	// we should select a node as a part pin if it satisfies the following rules:
    	// 1 it is a EE/WW/SS/NN node
    	// 2 it should be in the target pblock
    	// 3 its next node should be in the target pblock

    	// case 1: the node is a mux node, should not choose it as the part pin
    	if (!isDirectionNode(n)) {
    		return false;
    	}
    	// case 2: the node is not a mux node
    	else {
    		// case 2.1: the node is in the target pblock
    		if (targetPblock == getPblockNameOfTile(pblockNameToTiles, n.getTile())) {
    			Node nextNode = connections.get(n);
    			// case 2.1.1: the node is the last node
    			if (nextNode == null) {
    				return true;
    			}
    			// case 2.1.2: the node is not the last node
    			else {
    				// case 2.1.2.1: the next node is still in the target pblock
    				if (targetPblock == getPblockNameOfTile(pblockNameToTiles, nextNode.getTile())) {
    					return true;
    				}
    				// case 2.1.2.2: the next node is not in the target pblock
    				// this means some detour happens and the net routes outside the pblock in the middle
    				// we should not choose the current node as the part pin
    				else {
    					return false;
    				}
    			}
    		}
    		// case 2.2: the node is not in the target pblock
    		else {
    			return false;
    		}
    	}
    }

    private static void createPartitionPins(Design design, HashMap<String, Set<Tile> > pblockNameToTiles,
            Map<SitePinInst, EDIFHierPortInst> anchorRegPins) {    	
        for(Entry<SitePinInst, EDIFHierPortInst> e : anchorRegPins.entrySet()) {
            // skip adding partition pins to laguna anchors
//            if (e.getKey().getSite().getSiteTypeEnum() == SiteTypeEnum.LAGUNA) {
//              continue;
//            }

            // get the pblock name of the src/sink of the anchor
            SitePinInst anchorPin = e.getKey();
            String anchorSrcOrSinkPblock;
            if (anchorPin.isOutPin()) {
              Tile sinkTile = anchorPin.getNet().getSinkPins().get(0).getTile();
              anchorSrcOrSinkPblock = getPblockNameOfTile(pblockNameToTiles, sinkTile);
            }
            else {
              Tile srcTile = anchorPin.getNet().getSourceTile();
              anchorSrcOrSinkPblock = getPblockNameOfTile(pblockNameToTiles, srcTile);
            }

            // get a linked list of nodes from the anchor to src/sink
            Net net = e.getKey().getNet();
            if(net.isStaticNet() || net.isClockNet()) continue;
            Node currNode = e.getKey().getConnectedNode();
            
            // need to consider bi-directional PIPs
            Map<Node, Node> connections = new HashMap<>();
            if(e.getKey().isOutPin()) {
                for(PIP pip : net.getPIPs()) {
                    if (pip.isBidirectional() && pip.isReversed()) {
                    	connections.put(pip.getEndNode(), pip.getStartNode());    	
                    }
                    else {
                        connections.put(pip.getStartNode(), pip.getEndNode());                    	
                    }
                }
            }else {
                for(PIP pip : net.getPIPs()) {
                    if (pip.isBidirectional() && pip.isReversed()) {
                        connections.put(pip.getStartNode(), pip.getEndNode());                    	
                    }
                    else {
                        connections.put(pip.getEndNode(), pip.getStartNode());                    	
                    }
                }
            }

            // locate the first node that is in the same pblock as the src/sink of the anchor
            while(!isValidNodeForPartPin(currNode, anchorSrcOrSinkPblock, pblockNameToTiles, connections)) {
                currNode = connections.get(currNode);

                // we fail to filed a preferred NN/SS/EE/WW node, use the last node as the part pin
                if (currNode == null) {
                	System.out.println("WARNING: skip adding part pin to " + e.getValue().toString());
                	break;
                }
            }

            // add the partition pin to the island ports instead of anchor pins
            if (currNode != null) {
                design.createPartitionPin(e.getValue(), currNode);
            }   
        }
    }

    public static void main(String[] args) {
        if(args.length != 2) {
            System.out.println("USAGE: <overlay_placed.dcp> <overlay_routed.dcp>");
            return;
        }

        Design design = Design.readCheckpoint(args[0]);

        Map<String, PBlock> pblocks = getPBlocksFromXDC(design);
        HashMap<String, Set<Tile> > pblockNameToTiles = new HashMap<String, Set<Tile> >();
        for(Entry<String, PBlock> e : pblocks.entrySet()) {
        	String pblock_name = e.getKey();
            if(pblock_name.contains("WRAPPER_VERTEX_CR_X")) {
            	if (pblockNameToTiles.get(pblock_name) == null) {
            		pblockNameToTiles.put(pblock_name, new HashSet<Tile>());
            	}
            	pblockNameToTiles.get(pblock_name).addAll(e.getValue().getAllTiles());
            }
        }

        Map<SitePinInst, EDIFHierPortInst> anchorRegPins = anchorRegPinsToRoute(design);

        RWRoute.routeDesignPartialNonTimingDriven(design);

        createPartitionPins(design, pblockNameToTiles, anchorRegPins);

//        // create black boxes
//        String island_cell_name = "pfm_top_i/dynamic_region/gaussian_kernel/inst/CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3";
//        DesignTools.makeBlackBox(design, island_cell_name);
//
//        // load in placed islands
//        Design island = Design.readCheckpoint("/share/einsx7/expr/island_dcp/CTRL_WRAPPER_VERTEX_CR_X4Y0_To_CR_X7Y3_island_place.dcp");
//        DesignTools.populateBlackBox(design, island_cell_name, island);
//        design.getNetlist().consolidateAllToWorkLibrary();

        //write checkpoint
        design.writeCheckpoint(args[1]);
    }

}