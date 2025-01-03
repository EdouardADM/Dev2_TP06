import subprocess  # Pour exécuter la commande tracert
import argparse   # Pour gérer les arguments en ligne de commande (-p, -o)
import re         # Pour les expressions régulières (analyse du texte)
import sys        # Pour la configuration du buffer de sortie
import socket    # Pour résoudre les noms de domaine en adresses IP

def get_target_ipv6(target):
    try:
        # getaddrinfo retourne toutes les infos d'adressage pour un nom d'hôte
        addrinfo = socket.getaddrinfo(target, None)
        # On filtre pour ne garder que les IPv6 (AF_INET6)
        ipv6_addresses = [addr[4][0] for addr in addrinfo if addr[0] == socket.AF_INET6]
        # On retourne la première IPv6 trouvée
        return ipv6_addresses[0] if ipv6_addresses else None
    except (socket.gaierror, IndexError):
        return None

def parse_tracert_line(line):
    # Regex pour trouver le numéro de saut (ex: "  1  ")
    hop_pattern = re.compile(r'^\s*(\d+)\s+')
    # Regex pour trouver l'IP (soit entre crochets [1.2.3.4], soit après les "ms")
    ip_pattern = re.compile(r'\[([\d.]+)\]|(?:\d+\s+ms\s+)+(\S+)$')
    
    # Vérifie si la ligne commence par un numéro de saut
    hop_match = hop_pattern.match(line)
    if not hop_match:
        return None

    # Cherche l'IP dans la ligne
    ip_match = ip_pattern.search(line)
    if ip_match:
        # Prend soit l'IP entre crochets, soit celle après les "ms"
        ip = ip_match.group(1) or ip_match.group(2)
        if ip == '*':
            return f"Hop {hop_match.group(1)}: *"
        return f"Hop {hop_match.group(1)}: {ip}"
    elif '*' in line:
        return f"Hop {hop_match.group(1)}: *"
    return None

def traceroute(target, print_realtime=False, output_file=None):
    # Récupère l'IPv6 de la cible
    target_ipv6 = get_target_ipv6(target)
    if target_ipv6:
        message = f"Détermination du chemin vers {target} [{target_ipv6}]\n"
        print(message)
    else:
        print(f"Impossible de résoudre l'IPv6 de {target}")
        return

    # Configure la sortie en temps réel si demandé
    if print_realtime:
        sys.stdout.reconfigure(line_buffering=True)
    
    # Lance la commande tracert
    process = subprocess.Popen(
        ["tracert", "-d", target],  # -d évite la résolution DNS
        stdout=subprocess.PIPE,      # Capture la sortie
        stderr=subprocess.PIPE,      # Capture les erreurs
        text=True,                  # Mode texte
        encoding="cp850",           # Encodage Windows
        bufsize=1                   # Buffer ligne par ligne
    )
    
    # Liste pour stocker tous les sauts
    hops = []
    # Lit la sortie ligne par ligne
    for line in process.stdout:
        line = line.strip()
        hop_info = parse_tracert_line(line)
        
        if hop_info:
            hops.append(hop_info)
            if print_realtime:
                print(hop_info, flush=True)
    
    # Attend la fin de la commande
    process.wait()
    
    # Sauvegarde dans un fichier si demandé
    if output_file:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(message)
            file.write("\n".join(hops))
    
    # Affiche tout à la fin si pas en temps réel
    if not print_realtime:
        print("\n".join(hops))
    
    return hops

if __name__ == "__main__":
    # Crée le parseur d'arguments
    parser = argparse.ArgumentParser(description="Traceroute avec options")
    # Ajoute les arguments possibles
    parser.add_argument("target", help="Adresse du site à tracer (ex : google.com)")
    parser.add_argument("-p", action="store_true", help="Affiche les sauts en temps réel")
    parser.add_argument("-o", metavar="fichier", help="Enregistre les résultats dans un fichier texte")

    # Parse les arguments
    args = parser.parse_args()
    # Lance le traceroute avec les options fournies
    traceroute(target=args.target, print_realtime=args.p, output_file=args.o)