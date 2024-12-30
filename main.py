import subprocess
import ipaddress
import argparse

def traceroute(target, print_realtime=False, output_file=None):
    process = subprocess.Popen(["tracert", target], stdout=subprocess.PIPE, text=True)

    hops = []  # Stocker les différents sauts
    while True:
        line = process.stdout.readline()
        if not line:
            break
        else:
            line = line.strip()
            hops.append(line)

            if print_realtime:  # Affiche les sauts en temps réel si l'option -p est activée
                print(line)

            # Identifier les adresses IP dans la ligne
            elements = line.split()
            for element in elements:
                try:
                    ip = ipaddress.IPv4Address(element)
                    if print_realtime:  # Affiche les adresses IP en temps réel si -p
                        print(f"Adresse IP du saut : {ip}")
                    break
                except ipaddress.AddressValueError:
                    pass

    process.wait()

    if output_file:  # Stocke les résultats dans un fichier texte si l'option -o est activée
        with open(output_file, "w") as file:
            file.write("\n".join(hops))
        print(f"Les résultats ont été enregistrés dans le fichier : {output_file}")

    if not print_realtime:  # Si -p n'est pas activé, affiche les résultats une fois terminé
        print("Traçage terminé. Résultats :")
        print("\n".join(hops))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traceroute avec options")
    parser.add_argument("target", help="Adresse du site à tracer (ex : google.com)")
    parser.add_argument("-p", action="store_true", help="Affiche les sauts en temps réel")
    parser.add_argument("-o", metavar="fichier", help="Enregistre les résultats dans un fichier texte")

    args = parser.parse_args()

    # Appeler la fonction traceroute avec les options fournies
    traceroute(target=args.target, print_realtime=args.p, output_file=args.o)