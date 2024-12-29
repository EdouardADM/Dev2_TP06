import socket

# Vous importez les classes et fonctions nécessaires de Scapy pour créer et envoyer des paquets réseau.
from scapy.all import IP, ICMP, sr1

# Cette fonction implémente un traceroute vers une destination donnée avec un nombre maximum de sauts spécifié.
def traceroute(destination, max_hops=30):
    print(f"Traceroute vers {destination} (max {max_hops} sauts):")

    try:
        # Résolution du nom de domaine en adresse IP
        destination_ip = socket.gethostbyname(destination)
        print(f"Adresse IP du site : {destination_ip}\n")
    except socket.gaierror:
        # Gestion de l'erreur si le domaine ne peut pas être résolu
        print("Erreur : impossible de résoudre l'adresse.")
        return

    for ttl in range(1, max_hops + 1):
        # Créer le paquet ICMP avec un TTL spécifique
        packet = IP(dst=destination_ip, ttl=ttl) / ICMP()

        # Envoyer le paquet et recevoir la réponse
        reply = sr1(packet, verbose=0, timeout=2)

        if reply is None:
            # Si aucune réponse n'est reçue pour ce saut
            print(f"{ttl}\t*\tPas de réponse")
        else:
            # Afficher l'adresse IP du saut courant
            print(f"{ttl}\t{reply.src}")
            # Arrêter si on atteint la destination
            if reply.src == destination_ip:
                print("\nDestination atteinte.")
                break

if __name__ == "__main__":
    # Entrée de l'utilisateur pour le domaine ou l'adresse IP
    site = input("Entrez le nom de domaine ou l'adresse IP : ").strip()
    traceroute(site)