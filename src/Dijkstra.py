# We will firstly define the graph data structure, 
# and then implement Dijkstra's algorithm to find the shortest path in a weighted graph.

class Node(object):
    def __init__(self, name):
        """Assumes name is a string"""
        self.name = name
    def getName(self):
        return self.name
    def __str__(self):
        return self.name

class Edge(object):
    def __init__(self, src, dest):
        """Assumes src and dest are nodes"""
        self.src = src
        self.dest = dest
    def getSource(self):
        return self.src
    def getDestination(self):
        return self.dest
    def __str__(self):
        return self.src.getName() + '->' + self.dest.getName()
               
class Digraph(object):
    """edges is a dict mapping each node to a list of
    its children"""
    def __init__(self):
        self.edges = {}
    def addNode(self, node):
        if node in self.edges:
            raise ValueError('Duplicate node')
        else:
            self.edges[node] = []
    def addEdge(self, edge):
        src = edge.getSource()
        dest = edge.getDestination()
        if not (src in self.edges and dest in self.edges):
            raise ValueError('Node not in graph')
        self.edges[src].append(dest)
    def childrenOf(self, node):
        return self.edges[node]
    def hasNode(self, node):
        return node in self.edges
    def getNode(self, name):
        for n in self.edges:
            if n.getName() == name:
                return n
        raise NameError(name)
    def __str__(self):
        result = ''
        for src in self.edges:
            for dest in self.edges[src]:
                result = result + src.getName() + '->'\
                         + dest.getName() + '\n'
        return result[:-1] #omit final newline

class Graph(Digraph):
    def addEdge(self, edge):
        Digraph.addEdge(self, edge)
        rev = Edge(edge.getDestination(), edge.getSource())
        Digraph.addEdge(self, rev)


# for weighted shorest path, we can use Dijkstra's algorithm, 
# which is a generalization of BFS.

# first step: expand Edge class to include weights   
class WeightedEdge(Edge):
     def __init__(self, src, dest, weight = 1.0):
         """Assume src and dest are nodes, and weight a number"""  
         Edge.__init__(self, src, dest)

         self.weight = weight    
    
     def getWeight(self):
         return self.weight
     
     def __str__(self):
         return self.src.getName() + '->' + self.dest.getName() + ':' + str(self.weight)    
    

# second step: modify Graph to handle weighted edges
class WeightedDigraph(Digraph):
    def __init__(self):
        Digraph.__init__(self)
        self.weights = {}

    def addEdge(self, edge): 
        Digraph.addEdge(self, edge)

        self.weights[(edge.getSource(), edge.getDestination())] = edge.getWeight()
    
    def getWeight(self, src, dest):
        return self.weights[(src, dest)]


# third step: implement Dijkstra's algorithm
import heapq

def Dijkstra(graph, start, end, toPrint = False):
    '''Using Dijkstra's algorithm to find the shortest path from start to end in graph
    Assumes: graph is a WeightedDigraph; start and end are nodes
    returns: (shortest distance, shortest path), 
    if there is a path from start to end; None otherwise'''
    
    distance ={start: 0}
    previous ={start: None}

    pq = [(0, id(start), start)]

    visited = set()

    while pq:
        current_dist, _, current_node = heapq.heappop(pq)

        if current_node in visited:
            continue

        visited.add(current_node)

        if toPrint:
            print('visiting' + str(current_node) + 'with distance' + str(current_dist))

        if current_node == end:
            path = []
            node = end
            while node is not None:
                path.append(node)
                node=previous[node]
            
            path.reverse()
            
            return (current_dist, path)
        
        for neighbor in graph.childrenOf(current_node):
            if neighbor in visited:
                continue

            weight = graph.getWeight(current_node, neighbor)
            new_dist = current_dist + weight

            if neighbor not in distance or new_dist < distance[neighbor]:
                distance[neighbor] = new_dist
                previous[neighbor] = current_node
                heapq.heappush(pq, (new_dist, id(neighbor), neighbor))
    
    return (None, None)



# forth step: build a weighted graph and test Dijkstra's algorithm
if __name__ == '__main__':
    def buildWeightedGraph():
        g = WeightedDigraph()
    
        # add nodes
        cities = ['A','B','C','D','E']
    
        for name in cities:
            g.addNode(Node(name))
        
        # add edges with weights
        g.addEdge(WeightedEdge(g.getNode('A'), g.getNode('B'), 1))
        g.addEdge(WeightedEdge(g.getNode('A'), g.getNode('C'), 3))
        g.addEdge(WeightedEdge(g.getNode('B'), g.getNode('E'), 6))
        g.addEdge(WeightedEdge(g.getNode('C'), g.getNode('E'), 2))
        g.addEdge(WeightedEdge(g.getNode('B'), g.getNode('D'), 4))
        g.addEdge(WeightedEdge(g.getNode('D'), g.getNode('E'), 1))
    
        return g

    # running the test
    g = buildWeightedGraph()
    distance, path = Dijkstra(g, g.getNode('A'), g.getNode('E'), toPrint=True)

    print('\n')
    print('shortest distance: ' + str(distance))
    print(f'shortest path: {[str(node) for node in path]}')





