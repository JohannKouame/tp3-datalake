import os

class Processor:
    def clean_text(self, text):
        """
        Nettoie le texte en supprimant les caractères non-alphabétiques.
        :param text: Texte à nettoyer.
        :return: Texte nettoyé.
        """
        cleaned_text = ''.join([c if c.isalnum() or c.isspace() else ' ' for c in text])
        return cleaned_text.strip()

    def clean_data(self, file_path):
        """
        Nettoie les données d'un fichier et les enregistre dans le dossier staging.
        :param file_path: Chemin du fichier à nettoyer.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Nettoyer chaque ligne du fichier
            cleaned_lines = [self.clean_text(line) for line in lines]

            # Modifier le chemin pour le dossier staging
            cleaned_file_path = file_path.replace('raw', 'staging')

            # Créer le répertoire de destination si nécessaire
            os.makedirs(os.path.dirname(cleaned_file_path), exist_ok=True)

            # Écrire les données nettoyées dans le fichier de destination
            with open(cleaned_file_path, 'w', encoding='utf-8') as file:
                file.writelines('\n'.join(cleaned_lines))

            print(f"Fichier traité et enregistré : {cleaned_file_path}")

        except Exception as e:
            print(f"Erreur lors du traitement du fichier {file_path}: {e}")

    def process_raw_data(self, raw_directory):
        """
        Parcourt tous les fichiers dans le dossier raw_directory et les nettoie.
        :param raw_directory: Chemin du dossier contenant les fichiers bruts.
        """
        for root, dirs, files in os.walk(raw_directory):
            for file in files:
                if file.endswith('.txt'):  # Traiter uniquement les fichiers texte
                    file_path = os.path.join(root, file)
                    self.clean_data(file_path)
                else:
                    print(f"Fichier ignoré (non texte) : {file}")
