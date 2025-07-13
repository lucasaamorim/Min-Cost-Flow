import collections
from itertools import product
from push_relabel import PushRelabel

class MinCostPushRelabel:
    """
    Implementação simples do algoritmo de cost-scaling para encontrar um Fluxo de Custo Mínimo.
    """
    def __init__(self, num_vertices):
        """
        Inicialização
        
        Args:
            num_vertices (int): O Número de vértices do grafo.
                                É assumido que os vértices estão numerados de 0 a num_vertices-1.
        """
        self.V = num_vertices
        self.graph = collections.defaultdict(list)
        
        # Propriedades dos arcos do grafo (capacidade, fluxo e custo)
        self.capacity = [[0] * self.V for _ in range(self.V)]
        self.flow = [[0] * self.V for _ in range(self.V)]
        self.cost = [[0] * self.V for _ in range(self.V)]
        
        #Índice dos nós de demanda (para checagem rápida da viabilidade do fluxo)
        self.demand = []
        self.supply = []
        
        # Excesso de Fluxo (Similar ao push-relabel)
        self.excess = [0] * self.V
        
        # Potencial (funcionamento um pouco diferente do potencial usado no push-relabel mas ainda é similar)
        self.potential = [0] * self.V

    def add_edge(self, u, v, cap, cost):
        """
        Adiciona um arco no grafo.
        
        Args:
            u (int): Nó de origem do arco.
            v (int): Nó de destino do arco.
            cap (int): Capacidade do arco.
            cost (int): Custo por unidade de fluxo enviada pelo arco.
        """
        self.graph[u].append(v)
        self.graph[v].append(u) # Arcos reversos
        self.capacity[u][v] = cap
        self.cost[u][v] = cost
        # O custo de "devolver" fluxo é negativo
        self.cost[v][u] = -cost

    def set_supply(self, u, supply):
        """
        Define oferta/demanda de um nó. Oferta positiva indica um nó de oferta,
        e oferta negativa indica um nó de demanda.
        
        Args:
            u (int): Nó que queremos definir uma oferta/demanda.
            supply (int): Valor de oferta/demanda.
        """
        if supply > 0:
            self.excess[u] = supply
            self.supply.append(u)
        elif supply < 0:
            self.excess[u] = supply
            self.demand.append(u)
        else:
            print("Valor de oferta deve ser diferente de zero")

    def _reduced_cost(self, u, v):
        """
        Calcula o custo reduzido de um arco, Que guia o algoritmo.
        Um arco é considerado "aceitável" se seu custo reduzido for negativo.
        """
        return self.cost[u][v] + self.potential[u] - self.potential[v]

    def push(self, u, v):
        """
        Envia fluxo de um nó com excesso u para um vizinho v.
        Só é realizado em arcos "aceitáveis" onde o custo reduzido é negativo.
        """
        residual_capacity = self.capacity[u][v] - self.flow[u][v]
        delta = min(self.excess[u], residual_capacity)
        
        self.flow[u][v] += delta
        self.flow[v][u] -= delta
        
        self.excess[u] -= delta
        self.excess[v] += delta

    def relabel(self, u, epsilon):
        """
        Diminui o potencial do nó u.
        Torna ao menos um arco "aceitável".
        
        Args:
            u (int): Nó que vai ser feito o relabel.
            epsilon (float): Tolerância de erro atual.
        """
        
        min_potential_diff = float('inf')
        #potential[u] = min_edge_weight
        # Encontra a menor diferença de potencial que tornaria um arco admissível
        for v in self.graph[u]:
            if self.capacity[u][v] - self.flow[u][v] > 0:
                # The new potential should be p[v] - c[u,v] - epsilon
                min_potential_diff = min(min_potential_diff, self.potential[v] - self.cost[u][v])

        if min_potential_diff != float('inf'):
            # Decrease the potential to make at least one arc admissible
            self.potential[u] = min_potential_diff - epsilon
    
    def refine(self, epsilon):
        """
        Parte principal do algoritmo: Encontra um fluxo epsilon-opitimal.
        Elimina todo fluxo em excesso através de pushs e relabels.
        """

        # 1. Saturar todos os arcos aceitáveis para criar um pré-fluxo
        for u in range(self.V):
            for v in self.graph[u]:
                if self._reduced_cost(u, v) < 0:
                    delta = self.capacity[u][v] - self.flow[u][v]
                    if delta > 0:
                        self.flow[u][v] += delta
                        self.flow[v][u] -= delta
                        self.excess[u] -= delta
                        self.excess[v] += delta

        # 2. Encontrar nós com excesso para fazer push ou relabel - repetindo o processo até nenhum nó ter excesso (com excessão da fonte e origem)
        active_nodes = [i for i, e in enumerate(self.excess) if e > 0]
        
        while active_nodes:
            u = active_nodes.pop(0)
            
            # Elimina todo o excesso do nó
            while self.excess[u] > 0:
                pushed = False
                for v in self.graph[u]:
                    # Confere se o arco é aceitável para realizarmos um PUSH
                    if self.capacity[u][v] - self.flow[u][v] > 0 and self._reduced_cost(u, v) < 0:
                        was_inactive = self.excess[v] <= 0
                        self.push(u, v)
                        # Caso o push tenha gerado um excesso em V, adicionamos ele na lista de nós com excesso
                        if self.excess[v] > 0 and was_inactive:
                            active_nodes.append(v)
                        pushed = True
                
                # Caso não tenha ocorrido nenhum push no nó, realizamos um relabel dele
                if not pushed:
                    self.relabel(u, epsilon)
                    continue

    def min_cost_flow(self, alpha=2):
        """
        Constrói um fluxo de custo mínimo no grafo 
        
        Args:
            alpha (int): Fator de redução do epsilon em cada fase do algoritmo.
            
        Returns:
            tuple: Uma tupla contendo o fluxo e o grafo final.
        """
        # --- Escalonamento ---
        
        # 1. Escala custos para valores inteiros e garante a otimalidade
        scaling_factor = self.V
        max_abs_cost = 0
        for u in range(self.V):
            for v in self.graph[u]:
                self.cost[u][v] *= scaling_factor
                if abs(self.cost[u][v]) > max_abs_cost:
                    max_abs_cost = abs(self.cost[u][v])

        # 2. Inicialização do epsilon
        epsilon = float(max_abs_cost)

        # 3. Obter uma circulação viável usando algum algoritmo de fluxo máximo
        
        # Criar um grafo com os vértices do nosso grafo original + fonte e sumidouro artificial
        # A fonte artificial será o nó n-2 e o sumidouro artificial será n-1 (considerando n = número de nós no grafo)
        g = PushRelabel(self.V+2);
        
        source = g.V-2
        sink = g.V-1
        # Exportar as arestas originais para o grafo g
        [g.add_edge(u,v,self.capacity[u][v]) for u,v in product(range(self.V),range(self.V)) if self.capacity[u][v] > 0] 
        # Conectar as arestaas de oferta com a fonte artificial (arestas com capacidade = |demanda no nó de oferta|)
        [g.add_edge(source,v,abs(self.excess[v])) for v in self.supply]
        # Conectar as arestas de demanda com o sumidouro artificial (arestas com capacidade = |demanda no nó de demanda|)
        [g.add_edge(u,sink,abs(self.excess[u])) for u in self.demand]

        # Encontrar um fluxo máximo (e consequentemente uma circulação viável, caso exista)
        g.max_flow();
        

        # Confere se a circulação é viável (toda a demanda é atendida)
        if sum([f[sink] for f in g.flow]) != sum(g.flow[source]):
            print("Circulação não viável. Não há como atender toda a demanda.")
            return None, None
        
        # Atualizar o nosso grafo para a circulação encontrada via push-relabel
        self.flow = [[g.flow[u][v] for v in range(self.V)] for u in range(self.V)]
        self.excess = [0] * self.V

        # 4. Loop de escalonamento
        while epsilon >= 1:
            print(f"--- Realizando refine com epsilon = {epsilon / scaling_factor:.4f} ---")
            self.refine(epsilon)
            epsilon /= alpha

        # 5. Calcula o custo final com os custos originais (não escalonados)
        total_cost = 0
        for u in range(self.V):
            for v in range(self.V):
                if self.flow[u][v] > 0:
                    original_cost = self.cost[u][v] / scaling_factor
                    total_cost += self.flow[u][v] * original_cost
                    
        return total_cost, self.flow

# --- Exemplo ---
if __name__ == "__main__":
    print("Teste - Goldberg-Tarjan Min-Cost Flow (Cost-Scaling Push-Relabel)")
    
    # 6 nós: 0=Fábrica 1, 1=Fábrica 2, 2,3=Armazens, 4=Cidade A, 5=Cidade B
    num_nodes = 6
    g = MinCostPushRelabel(num_nodes)
    
    # (origem, destino, capacidade, custo)
    edges = [
        (0, 2, 15, 4), (0, 3, 10, 3),
        (1, 2, 20, 6), (1, 3, 5, 8),
        (2, 4, 25, 2), (3, 4, 10, 5),
        (3, 5, 15, 4), (4, 5, 20, 1)
    ]
    
    for u, v, cap, cost in edges:
        g.add_edge(u, v, cap, cost)

    # Definindo ofertas e demandas
    # Nós de oferta (Fábricas 1 e 2)
    g.set_supply(0, 20)
    g.set_supply(1, 15)
    
    # Nós de demanda (Cidades A e B)
    g.set_supply(4, -10)
    g.set_supply(5, -25)
    
    # Os nós 2 e 3 são nós intermediários
    
    min_cost, final_flow = g.min_cost_flow()
    
    print(f"\nO custo mínimo do fluxo é: {min_cost}")
    print("\nFluxo final nas arestas:")
    for r in range(num_nodes):
        for c in range(num_nodes):
            if final_flow[r][c] > 0:
                print(f"  Fluxo de {r} -> {c}: {final_flow[r][c]}")
