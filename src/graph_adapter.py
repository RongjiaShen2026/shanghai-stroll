"""
Graph adapter: converts NetworkX MultiDiGraph (from OSMnx) into our 
internal WeightedDigraph representation used by the Dijkstra's solver.
"""

from __future__ import annotations

import logging

import time 

from typing import Tuple, Dict, Any, Hashable

import networkx as nx

from src.Dijkstra import WeightedDigraph, WeightedEdge, Node

# logging is a way to track events that happen when some software runs.
logger = logging.getLogger(__name__)

class GraphConversionError(Exception):
    """Raised when a NetworkX graph cannot be converted to a WeightedDigraph."""


def nx_to_weighted_digraph(
        G: nx.MultiDiGraph,
        *,
        weight_attr: str = 'length',
        strict: bool = True,
) -> Tuple[WeightedDigraph, Dict[Hashable, Node]]:
    """
    Convert a NetworkX MultiDiGraph (from OSMnx) into a WeightedDigraph.
    
    Each OSM node becomes a Node in the output graph. 
    
    For each parallel edge between two OSM nodes, only the edge with the smallest `weight_attr` is
    kept (since the shortest-path solver only cares about the minimum).
    
    Args:
        G: A NetworkX MultiDiGraph, typically produced by `osmnx.graph_from_*`.
            Nodes are expected to be OSM IDs (int). Edges must carry a numeric
            `weight_attr` (default: "length" in meters).
        weight_attr: Name of the edge attribute to use as edge weight.
        strict: If True, raise on missing/invalid weights. If False, skip
            offending edges and log a warning.

    Returns:
        A tuple ``(wg, osmid_to_node)`` where:
            - ``wg`` is the converted WeightedDigraph.
            - ``osmid_to_node`` maps original OSM IDs to the new Node objects,
              so callers can translate paths back to OSM IDs afterward.

    Raises:
        GraphConversionError: If the input graph is empty, or if `strict=True`
            and any edge is missing/has invalid `weight_attr`.

    """

    #---- 1. Validate input ----

    if G is None:
        raise GraphConversionError("Input graph is None.")
    
    if G.number_of_nodes()== 0:
        raise GraphConversionError("Input graph has no nodes.")
    
    logger.info(
        "Converting graph: %d nodes, %d edges (weight_attr=%r, strict=%s)",
        G.number_of_nodes(), G.number_of_edges(), weight_attr, strict,
    )
    
    t0 = time.perf_counter()

    wg = WeightedDigraph()
    osmid_to_node: Dict[Hashable, Node]={}

    
    # ---- 2. Convert nodes ----
    for osmid in G.nodes:
        node = Node(str(osmid)) # Convert OSM ID to string for internal use
        wg.addNode(node)
        osmid_to_node[osmid] = node
    


    # ---- 3. Convert edges (collapse parallel edges)----

    skipped = 0

    for u, v, key, data in G.edges(keys=True, data=True):
        weight = data.get(weight_attr)

        if weight is None or not isinstance(weight, (int, float)) or weight < 0:
            msg = (f"Edge ({u},{v}, key={key}) has invalid {weight_attr}={weight!r}"
                   )
            
            if strict:
                raise GraphConversionError(msg)
            
            logger.warning("%s - skipping", msg)
            skipped += 1
            continue

        src = osmid_to_node[u]
        dst = osmid_to_node[v]

        # If multiple parallel edges exist, keep only the shortest.
        existing_weight = None
        if dst in wg.childrenOf(src):
            existing_weight = wg.getWeight(src, dst)
        
        if existing_weight is None:
            edge = WeightedEdge(src, dst, float(weight))
            wg.addEdge(edge)
        
        elif weight < existing_weight:
            wg.weights[(src, dst)] = float(weight) # Update weight of existing edge
    
    elapsed = time.perf_counter() - t0
    logger.info(
        "Conversion complete: in %.3fs (%d edges skipped).", elapsed, skipped,
    )

    return wg, osmid_to_node


    












