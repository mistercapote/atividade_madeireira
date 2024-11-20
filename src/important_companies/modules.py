"""Arquivos com funções necessárias"""
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from networkx.classes.function import path_weight
from tqdm import tqdm
from data_cleaner import convert_id_to_str


def get_concessions(list_nodes: list,emp_type: dict)-> int: 
  # As concessões são todas emps marcadas como MANEJO,1
  # (fonte legal e extratores de madeira)

  count = 0
  for node in list_nodes:
    if emp_type[node] == 'MANEJO':
      count+=1

  return count

def get_sink_nodes(graph: nx.graph, emp_type: dict)-> dict:
  # If node is marked as FINAL, he is a sink
  # It is the final destination of the timber chain

  nodes = {}
  for node in graph.nodes():
    if emp_type[node] == 'FINAL':
      nodes[node] = 1
      continue

    # we consider sink nodes as final nodes or nodes that only transports to other final nodes
    not_sink = False
    for edge in graph.edges(node):
      if emp_type[edge[1]] != 'FINAL':
        not_sink=True

    if not not_sink:
      nodes[node] = 1

  return nodes

def get_timberflow(graph: nx.graph,emp_type: dict) -> None:
  
  sink_nodes = get_sink_nodes(graph, emp_type)

  total_in = 0
  total_out = 0

  # For all edges in the graph
  # 1. sum the volume of input (from MANEJO types)
  # 2. sum the volume of output (from FINAL types)
  for edge in graph.edges():
    if emp_type[edge[0]] == 'MANEJO':
      total_in += path_weight(graph, [edge[0],edge[1]], weight='Volume')
    elif edge[1] in sink_nodes:
      total_out += path_weight(graph, [edge[0],edge[1]], weight='Volume')

  print(f'Inflow Vol(m3): {total_in} \nOut Vol(m3): {total_out} \nProportion: {total_out/total_in}')
  return total_in, total_out