import pandas as pd
import re

# Charger le fichier XLSX
file_path = './data/Data.xlsx'
df = pd.read_excel(file_path)

# Afficher les premières lignes pour comprendre la structure
df.head()


# Fonction pour fusionner les lignes avec des retours à la ligne
def merge_lines(df):
    merged_data = []
    i = 0
    n = len(df)
    
    while i < n:
        # Initialiser la ligne courante
        current_row = df.iloc[i].copy()
        
        # Vérifier si la ligne suivante doit être fusionnée
        j = i + 1
        while j < n and pd.isna(df.iloc[j]['Title']):
            # Fusionner les contenus
            for col in df.columns:
                if pd.notna(df.iloc[j][col]):
                    current_row[col] = str(current_row[col]) + ' ' + str(df.iloc[j][col])
            j += 1
        
        # Ajouter la ligne fusionnée
        merged_data.append(current_row)
        
        # Passer à la ligne suivante
        i = j
    
    # Créer un nouveau DataFrame avec les lignes fusionnées
    merged_df = pd.DataFrame(merged_data)
    
    return merged_df
    

# Appliquer la fonction pour fusionner les lignes
merged_df = merge_lines(df)

# Afficher le résultat
merged_df.head()


# Vérifier s'il y a des cellules vides ou des retours à la ligne cachés dans les colonnes 'Title' et 'Content'
empty_or_newline_in_title = df['Title'].isna() | df['Title'].str.contains(r'\n', na=False)
empty_or_newline_in_content = df['Content'].isna() | df['Content'].str.contains(r'\n', na=False)

# Afficher les lignes où il y a des cellules vides ou des retours à la ligne
lines_with_empty_or_newline = df[empty_or_newline_in_title | empty_or_newline_in_content]
lines_with_empty_or_newline


# Fonction pour nettoyer les retours à la ligne dans les cellules
def clean_newlines(df):
    # Supprimer les retours à la ligne dans les cellules de 'Content'
    df['Content'] = df['Content'].str.replace(r'\n', ' ', regex=True)
    return df

# Appliquer la fonction pour nettoyer les retours à la ligne
df_cleaned = clean_newlines(df)

# Réappliquer la fonction pour fusionner les lignes si nécessaire
merged_df_cleaned = merge_lines(df_cleaned)

# Afficher un aperçu du résultat
merged_df_cleaned.head()


# Fonction pour nettoyer les balises HTML et les entités comme &nbsp;
def clean_html_and_entities(text):
    if pd.isna(text):
        return text
    # Supprimer les balises HTML
    clean_text = re.sub(r'<[^>]+>', '', text)
    # Remplacer les entités HTML comme &nbsp;
    clean_text = clean_text.replace('&nbsp;', ' ')
    # Nettoyer les espaces superflus
    clean_text = ' '.join(clean_text.split())
    return clean_text

# Appliquer la fonction de nettoyage aux colonnes 'Title' et 'Content'
merged_df_cleaned['Title'] = merged_df_cleaned['Title'].apply(clean_html_and_entities)
merged_df_cleaned['Content'] = merged_df_cleaned['Content'].apply(clean_html_and_entities)

# Afficher un aperçu du résultat
merged_df_cleaned.head()

#conserve que les colonnes title, content et thématique
merged_df_cleaned = merged_df_cleaned[['Title', 'Content', 'Thématiques']]

# supprimes les lignes où content ou title ou thématique est vide
merged_df_cleaned = merged_df_cleaned.dropna(subset=['Title', 'Content', 'Thématiques'])

# supprime les guillemets dans les colonnes title, content et thématique
merged_df_cleaned['Title'] = merged_df_cleaned['Title'].str.replace('"', '', regex=False)
merged_df_cleaned['Content'] = merged_df_cleaned['Content'].str.replace('"', '', regex=False)
merged_df_cleaned['Thématiques'] = merged_df_cleaned['Thématiques'].str.replace('"', '', regex=False)

# ajoute "question : " avant chaque question, "réponse : " avant chaque réponse dans la colonne content et "thématique : " avant chaque thématique dans la colonne thématique
merged_df_cleaned['Title'] = 'Question : ' + merged_df_cleaned['Title'] + ' '
merged_df_cleaned['Content'] = ' Réponse : ' + merged_df_cleaned['Content'] + ' '
merged_df_cleaned['Thématiques'] = ' Thématique : ' + merged_df_cleaned['Thématiques']


# Enregistrer le fichier transformé et nettoyé
cleaned_file_path = './data/data.txt'
#remove columns to have only the data , without header
merged_df_cleaned.to_csv(cleaned_file_path, index=False, sep='|', header=False)