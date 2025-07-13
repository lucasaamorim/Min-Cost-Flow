import collections

class PushRelabel:
    def __init__(self, num_vertices):
        """
        Initializes the data structures for the algorithm.
        
        Args:
            num_vertices (int): The total number of vertices in the graph, including source and sink.
                                Vertices are assumed to be numbered 0 to num_vertices-1.
        """
        # Número de vértices no grafo
        self.V = num_vertices
        
        # Fluxo recebido que não foi enviado
        self.excess = [0] * self.V
        
        # Pontencial do nó (fluxo é enviado do maior para o menor potencial)
        self.height = [0] * self.V
        
        # Fluxo nos arcos (matriz de adjacência)
        self.flow = [[0] * self.V for _ in range(self.V)]
        
        # Capacidade dos arcos (matriz de adjacência)
        self.capacity = [[0] * self.V for _ in range(self.V)]
        
        # Representação do grafo em forma de uma lista de adjacência
        self.graph = collections.defaultdict(list)

    def add_edge(self, u, v, cap):
        """
        Inclui um novo arco no grafo
        
        Args:
            u (int): Nó de origem do arco.
            v (int): Nó de destino do arco.
            cap (int): Capacidade do arco.
        """
        self.graph[u].append(v)
        
        self.capacity[u][v] = cap

    def initialize_preflow(self, s):
        """
        Vai definindo o pré-fluxo do grafo
        
        Args:
            s (int): Nó fonte do grafo.
        """
        self.height[s] = self.V
        
        for v in self.graph[s]:
            # Enviar o máximo de fluxo possível.
            self.flow[s][v] = self.capacity[s][v]
            
            # Fluxo reverso
            self.flow[v][s] = -self.capacity[s][v]
            
            # Atualizar o excesso do nó que recebeu o fluxo.
            self.excess[v] = self.capacity[s][v]
            
            # Atualizar o excesso do nó fonte.
            self.excess[s] -= self.capacity[s][v]

    def push(self, u, v):
        """
        Envia fluxo em excesso de um nó u para um v adjacente com pontencial menor.
        
        Args:
            u (int): Nó de origem (deve ter excesso >= 0).
            v (int): Nó de destino (deve ter potencial menor que o do nó u).
        """
        
        residual_capacity = self.capacity[u][v] - self.flow[u][v]
        
        
        # Fluxo máximo que podemos enviar pelo arco
        delta = min(self.excess[u], residual_capacity)
        
        # Atualizar o fluxo nos arcos diretos e reversos.
        self.flow[u][v] += delta
        self.flow[v][u] -= delta
        
        # Atualiza o excesso em ambos os nós.
        self.excess[u] -= delta
        self.excess[v] += delta

    def relabel(self, u):
        """
        Atualiza o potencial do nó u para ({potencial do vizinho mais baixo} + 1)
        
        Args:
            u (int): Nó que sofrerá relabel.
        """
        min_height = float('inf')
        
        # considera o vizinho somente se o arco não estiver saturado
        for v in range(self.V):
            if self.capacity[u][v] - self.flow[u][v] > 0:
                min_height = min(min_height, self.height[v])
        
        # Atualiza o potencial para permitir push para o vizinho válido de menor potencial
        if min_height != float('inf'):
            self.height[u] = min_height + 1

    def max_flow(self, s, t):
        """
        Calcula o valor do fluxo máximo entre uma fonte e um sumidouro.
        
        Args:
            s (int): Nó fonte.
            t (int): Sumidouro.
            
        Returns:
            int: Valor do fluxo máximo.
        """
        # Passo 1: Criar um pré-fluxo partindo da fonte.
        self.initialize_preflow(s)
        
        it = 1
        # Loop Principal: Continuar enquanto houverem nós com excesso (exceto s e t).
        active_node_found = True
        while active_node_found:
            active_node_found = False
            # Encontra um nó com excesso 'u'.
            for u in range(self.V):
                if u == s or u == t:
                    continue
                    
                if self.excess[u] > 0:
                    active_node_found = True
                    
                    # Procura por um nó em que possamos fazer um PUSH.
                    pushed = False
                    for v in range(self.V):
                        if self.capacity[u][v] - self.flow[u][v] > 0 and self.height[u] == self.height[v] + 1:
                            print("push done")
                            self.push(u, v)
                            pushed = True
                            break # Após realizar um push, vai para o próximo vértice com excesso
                    
                    # Se não houve PUSH, então precisamos fazer um RELABEL em u.
                    if not pushed:
                        print("relabel done")
                        self.relabel(u)
            print(f"iteração {it} feita")
            it += 1
        # O fluxo máximo é o excesso no sumidouro.
        return self.excess[t]

# --- Examplo ---
if __name__ == "__main__":
    print("Teste - Godldberg-Tarjan Max Flow (push-relabel)")
    # Nós de 0 a 5
    num_nodes = 6
    g = PushRelabel(num_nodes)
    
    # Define os arcos e suas capacidades
    # (origem, destino, capacidade)
    edges = [
        (0, 1, 16), (0, 2, 13),
        (1, 2, 10), (1, 3, 12),
        (2, 1, 4),  (2, 4, 14),
        (3, 2, 9),  (3, 5, 20),
        (4, 3, 7),  (4, 5, 4)
    ]
    
    for u, v, cap in edges:
        g.add_edge(u, v, cap)

    # Escolha de um nó fonte e de um sumidouro
    source = 0
    sink = 5

    print(f"Grafo com {num_nodes} nós")
    print(f"Fonte: {source}, Sumidouro: {sink}")
    
    max_flow_value = g.max_flow(source, sink)
    print(f"O Fluxo máximo é: {max_flow_value}") # Saída esperada para esse caso: 23
