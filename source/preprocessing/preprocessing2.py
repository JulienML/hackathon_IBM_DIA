import pandas as pd
import re

def nettoyer_texte(texte):
    """Nettoie le texte en supprimant les retours à la ligne, les balises HTML et les &nbsp;."""
    if isinstance(texte, str):
        # Supprimer les retours à la ligne
        texte = texte.replace('\n', ' ').replace('\r', ' ')
        # Supprimer les balises HTML
        texte = re.sub(r'<[^>]+>', '', texte)
        # Supprimer les &nbsp;
        texte = texte.replace('&nbsp;', ' ')
        # Supprimer les espaces multiples
        texte = ' '.join(texte.split())
    return texte

def traiter_fichier_excel(chemin_entree, chemin_sortie):
    """Lit un fichier Excel, nettoie les données et exporte en CSV."""
    # Lire le fichier Excel
    df = pd.read_excel(chemin_entree, engine='openpyxl')

    # Appliquer la fonction de nettoyage à toutes les colonnes
    df = df.applymap(nettoyer_texte)

    # Exporter en CSV
    df.to_csv(chemin_sortie, index=False, encoding='utf-8-sig')
    print(f"Le fichier a été exporté avec succès vers {chemin_sortie}")

# Exemple d'utilisation
if __name__ == "__main__":
    chemin_entree = 'donnees.xlsx'
    chemin_sortie = 'donnees_clean.csv'
    traiter_fichier_excel(chemin_entree, chemin_sortie)