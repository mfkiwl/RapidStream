from typing import List, Tuple, Dict
from graphviz import Digraph

class Node:
  def __init__(self, route: str):
    """
    given a list of tokens, use the first one as the name of the current node
    find the children nodes of the current node
    """
    self.name: str = None
    self.children: List[Node] = None
    self.attributes = {} # for dot visualization

    self._parseTokens(route)

  def _preprocess(self, route: str) -> List[str]:
    route = route.replace('{', ' { ').replace('}', ' } ')
    return [t for t in route.split() if t]

  def _parseTokens(self, route: str):
    tokens = self._preprocess(route)

    # get rid of the brackets if exist
    if tokens[0] == '{':
      assert tokens[-1] =='}'
      tokens = tokens[1:-1]

    # the first node must be a valid one  
    assert tokens[0] != '{'

    # the first token is used for the current node
    self.name = tokens[0]
    self.children = []
    remaining_tokens = tokens[1:]

    # find children from the rest of the nodes
    while remaining_tokens:
      closure, remaining_tokens = self._getClosure(remaining_tokens)
      self.children.append(Node(' '.join(closure)))


  def _getClosure(self, tokens: List) -> Tuple[List, List]:
    """
    if the first token is '{', return tokens until associated '}'
    else, return the first token
    """
    if not tokens:
      assert False

    # if the first node is not '{', the entire list belongs to one child node
    elif tokens[0] != '{':
      closure = tokens

    # if the first node is '{', the nodes bewteen it and the associated '}' belongs to one child node
    else:
      closure = []
      stack = 0
      for t in tokens:
        closure.append(t)

        if t == '{':
          stack += 1
        elif t == '}':
          stack -= 1
        
        if stack == 0:
          break
      
    remaining_tokens = tokens[len(closure) : ]
    return closure, remaining_tokens

  def dumpRouteString(self):
    if not self.children:
      return self.name
    else:
      route = self.name + ' '
      for i in range(len(self.children)-1):
        route += '{ ' + self.children[i].dumpRouteString() + ' } '
      route += self.children[-1].dumpRouteString()
      
      return route

  def getDot(self, vertices: List, edges: List):
    """
    get the dot file for the tree.
    """
    vertices.append( [str(id(self)), self.name, self.attributes ] ) # name, label, attrs
    edges += [(str(id(self)), str(id(child))) for child in self.children]

    for child in self.children:
      child.getDot(vertices, edges)

  def addAttr(self, attrs: Dict[str, str]):
    self.attributes.update(attrs)
  

def compareRouteString(str1, str2):
  token_list_1 = [t for t in str1.split() if t]
  token_list_2 = [t for t in str2.split() if t]
  len1 = len(token_list_1)
  len2 = len(token_list_2)
  for i in range(min(len1, len2)):
    print(token_list_1[i] == token_list_2[i], token_list_1[i], token_list_2[i])


def compareAndMarkTwoTrees(tree1: Node, tree2: Node) -> None:
  """
  Use tree1 as the base, mark any node in tree2 that is an expansion from tree1
  """
  def mark(node): 
    node.addAttr({'color' : 'red'})

  if tree1 and tree2:
    num_children_1 = len(tree1.children)
    num_children_2 = len(tree2.children)

    if num_children_1 > num_children_2:
      tree1, tree2 = tree2, tree1

    if tree1.name != tree2.name:
      mark(tree1)
      mark(tree2)

    for i in range(num_children_1):
      compareAndMarkTwoTrees(tree1.children[i], tree2.children[i])
    
    for i in range(num_children_1, num_children_2):
      compareAndMarkTwoTrees(None, tree2.children[i])
  
  elif not tree1 and tree2:
    mark(tree2)
    for child in tree2.children:
      compareAndMarkTwoTrees(None, child)
  elif tree1 and not tree2:
    mark(tree1)
    for child in tree1.children:
      compareAndMarkTwoTrees(child, None)
  else:
    return
    

def getDotFile(tree: Node, filename = 'clock.dot'):
  """
  use https://dreampuf.github.io/GraphvizOnline/ to visualize dot files
  """
  vertices = []
  edges = []
  tree.getDot(vertices, edges)

  dot = Digraph(comment='Clock Route')
  for v_id, v_name, v_attr in vertices:
    dot.node(v_id, v_name, v_attr)
  for src, sink in edges:
    dot.edge(src, sink)

  open(filename, 'w').write(dot.source)


def testCompareAndMarkTwoTrees():
  route1 = '{ CLK_BUFGCE_9_CLK_OUT CLK_CMT_MUX_16_ENC_2_CLK_OUT CLK_CMT_MUX_2TO1_19_CLK_OUT CLK_HROUTE_0_2 CLK_HROUTE_L2 CLK_HROUTE_L2 CLK_CMT_MUX_3TO1_2_CLK_OUT CLK_VROUTE_BOT CLK_CMT_DRVR_TRI_ESD_3_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_2_CLK_OUT CLK_VROUTE_BOT CLK_CMT_DRVR_TRI_ESD_2_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP { CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B { CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN } CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN } CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN }'
  route2 = '{ CLK_BUFGCE_9_CLK_OUT CLK_CMT_MUX_16_ENC_2_CLK_OUT CLK_CMT_MUX_2TO1_19_CLK_OUT CLK_HROUTE_0_2 CLK_HROUTE_L2 CLK_HROUTE_L2 CLK_CMT_MUX_3TO1_2_CLK_OUT CLK_VROUTE_BOT CLK_CMT_DRVR_TRI_ESD_3_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_2_CLK_OUT CLK_VROUTE_BOT CLK_CMT_DRVR_TRI_ESD_2_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP { CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B { CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN } CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN } CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN dummy_tail { dummy_node_1 dummy_node_2 } }'
  tree1 = Node(route1)
  tree2 = Node(route2)
  compareAndMarkTwoTrees(tree1, tree2)
  getDotFile(tree2, 'mark_diff.dot')


def testTreeBasics():
  test_input = '{ CLK_BUFGCE_9_CLK_OUT CLK_CMT_MUX_16_ENC_2_CLK_OUT CLK_CMT_MUX_2TO1_19_CLK_OUT CLK_HROUTE_0_2 CLK_HROUTE_L2 CLK_HROUTE_L2 CLK_CMT_MUX_3TO1_2_CLK_OUT CLK_VROUTE_BOT CLK_CMT_DRVR_TRI_ESD_3_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_2_CLK_OUT CLK_VROUTE_BOT CLK_CMT_DRVR_TRI_ESD_2_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP { CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B { CLK_CMT_MUX_3TO1_1_CLK_OUT CLK_VDISTR_TOP CLK_CMT_DRVR_TRI_ESD_0_CLK_OUT_SCHMITT_B CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN } CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN } CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_CMT_MUX_3TO1_0_CLK_OUT CLK_VDISTR_BOT CLK_CMT_DRVR_TRI_ESD_1_CLK_OUT_SCHMITT_B CLK_BUFCE_ROW_FSR_0_CLK_IN CLK_BUFCE_ROW_FSR_0_CLK_OUT CLK_TEST_BUF_SITE_1_CLK_IN }'

  # construct a tree from the ROUTE string
  tree = Node(test_input)

  # convert back to the ROUTE string
  rebuild_tree = '{ ' + tree.dumpRouteString() + ' }'
  assert test_input == rebuild_tree

  # visualize the tree
  getDotFile(tree)

if __name__ == '__main__':
  testCompareAndMarkTwoTrees()
  testTreeBasics()