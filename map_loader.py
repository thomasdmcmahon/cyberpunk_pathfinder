import osmnx as ox
import networkx as nx

def load_city(city_name="Manhattan, New York, USA", dist=400):
    """
    Downloads a city street network around a place name.
    city_name: string (e.g., "Chicago, USA")
    dist: distance (meters) around city center
    """
    print(f"Downloading map for {city_name}...")
    G = ox.graph_from_place(city_name, network_type="drive")
    G = nx.Graph(G)
    G = nx.convert_node_labels_to_integers(G)

    # Extract node positions
    pos = {n: (float(data["x"]), float(data["y"])) for n, data in G.nodes(data=True)}

    print(f"✅ Map loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")
    return G, pos
