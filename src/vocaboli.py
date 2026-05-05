import random
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
DATA_DIR.mkdir(exist_ok=True)

FILE_NAME = DATA_DIR / "parole.json"
FILE_IMPARATE = DATA_DIR / "parole_imparate.json"

def carica_json(file_path):
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Attenzione: il file {file_path.name} non è un JSON valido. Verrà inizializzato vuoto.")
    return []

wordsInFile = carica_json(FILE_NAME)
wordsLearned = carica_json(FILE_IMPARATE)

def salva_parole():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(wordsInFile, f, indent=4, ensure_ascii=False)

def salva_parole_imparate():
    with open(FILE_IMPARATE, "w", encoding="utf-8") as f:
        json.dump(wordsLearned, f, indent=4, ensure_ascii=False)

def aggiungi_parola():
    print("\nAggiungi nuove parole (lascia vuoto per terminare):")
    while True:
        eng = input("Parola in inglese: ").strip()
        if not eng:
            break
        ita = input(f"Significato in italiano di '{eng}': ").strip()

        if any(p["english"].lower() == eng.lower() for p in wordsInFile):
            print(f"'{eng}' è già nella lista.")
        else:
            wordsInFile.append({"english": eng, "italian": ita, "errors": 0})
            print(f"Aggiunta: {eng} -> {ita}\n")
    salva_parole()

def rimuovi_parola():
    if not wordsInFile:
        print("\nNessuna parola salvata!")
        return

    parola = input("Inserisci la parola in inglese da rimuovere: ").strip().lower()
    for p in wordsInFile:
        if p["english"].lower() == parola:
            wordsInFile.remove(p)
            salva_parole()
            print(f"Parola '{p['english']}' rimossa con successo.")
            return
    print(f"La parola '{parola}' non è stata trovata.")

def sposta_parole_imparate():
    if not wordsInFile:
        print("\nNessuna parola salvata!")
        return

    parole_da_spostare = []

    print("\nPremi 's' per segnare la parola come MEMORIZZATA.\n")

    for p in wordsInFile:
        scelta = input(f"'{p['english']}' → vuoi spostarla tra le parole imparate? (s/N): ").strip().lower()
        if scelta == "s":
            parole_da_spostare.append(p)

    if not parole_da_spostare:
        print("\nNessuna parola selezionata.")
        return

    print("\nParole selezionate:")
    for i, p in enumerate(parole_da_spostare, 1):
        print(f"{i}. {p['english']}")

    while True:
        conferma = input("\nConfermi lo spostamento? (s/n): ").strip().lower()
        if conferma in ("s", "n"):
            break
        print("Devi digitare 's' o 'n'")

    if conferma == "n":
        print("\nOperazione annullata.")
        return

    for p in parole_da_spostare:
        wordsInFile.remove(p)
        nuova_parola = {
            "english": p["english"],
            "italian": p["italian"]
        }
        wordsLearned.append(nuova_parola)

    salva_parole()
    salva_parole_imparate()

    print(f"\nSpostate {len(parole_da_spostare)} parole tra quelle memorizzate.")

def modifica_parola():
    if not wordsInFile:
        print("\nNessuna parola salvata!")
        return

    search = input("Inserisci parte della parola in inglese da modificare: ").strip().lower()
    matching = [p for p in wordsInFile if search in p["english"].lower()]

    if not matching:
        print(f"Nessuna parola trovata che contenga '{search}'.")
        return

    print("\nParole trovate:")
    for i, p in enumerate(matching, 1):
        print(f"{i}. {p['english']} -> {p['italian']} (errors: {p['errors']})")

    scelta = input("Seleziona il numero della parola da modificare: ").strip()
    if not scelta.isdigit() or int(scelta) < 1 or int(scelta) > len(matching):
        print("Scelta non valida.")
        return

    p = matching[int(scelta) - 1]

    print(f"\nModifica parola: {p['english']} -> {p['italian']}")
    nuova_eng = input(f"Nuova parola inglese (INVIO per lasciare '{p['english']}'): ").strip()
    nuovo_ita = input(f"Nuovo significato (INVIO per lasciare '{p['italian']}'): ").strip()

    if nuova_eng:
        p["english"] = nuova_eng
    if nuovo_ita:
        p["italian"] = nuovo_ita

    salva_parole()
    print(f"Parola modificata: {p['english']} -> {p['italian']}\n")

def weighted_sample_no_replacement(items, k):
    items = items.copy()
    weights = [(p["errors"] + 1) * (1.5 if p["errors"] == 0 else 1) for p in items]
    selezionate = []

    for _ in range(min(k, len(items))):
        totale = sum(weights)
        scelta = random.uniform(0, totale)
        cumulativo = 0
        for i, w in enumerate(weights):
            cumulativo += w
            if cumulativo >= scelta:
                selezionate.append(items.pop(i))
                weights.pop(i)
                break
    return selezionate

def quiz(parole_quiz):
    if not parole_quiz:
        print("Nessuna parola disponibile per il quiz.")
        return

    print(f"\nQuiz: {len(parole_quiz)} parole casuali")
    for i, p in enumerate(parole_quiz, 1):
        conosci = input(f"\n{i}. '{p['english']}' → (s/n): ").strip().lower()
        if conosci == "n":
            print(f"Significato: {p['italian']}")
            p["errors"] += 1
        else:
            print("Ottimo!")
            if p["errors"] > 0:
                p["errors"] -= 1
    salva_parole()

def quiz_normale():
    if not wordsInFile:
        print("\nNessuna parola disponibile per il quiz.")
        return

    num = input(f"Quante parole vuoi nel quiz? (nel file ci sono {len(wordsInFile)} parole): ")
    num = int(num) if num.isdigit() else 5
    selezionate = weighted_sample_no_replacement(wordsInFile, num)
    quiz(selezionate)

def quiz_imparate():
    if not wordsLearned:
        print("\nNessuna parola memorizzata!")
        return

    num = input(f"Quante parole vuoi nel quiz? (max {len(wordsLearned)}): ")
    num = int(num) if num.isdigit() else 5

    selezionate = random.sample(wordsLearned, min(num, len(wordsLearned)))

    print(f"\nQuiz parole memorizzate: {len(selezionate)} parole")

    for i, p in enumerate(selezionate, 1):
        conosci = input(f"\n{i}. '{p['english']}' → ricordi il significato? (s/n): ").strip().lower()
        if conosci == "n":
            print(f"Significato: {p['italian']}")
        else:
            print("Perfetto!")

def elencaParoleDifficili():
    if not wordsInFile:
        print("\nNessuna parola presente!")
        return

    max_errors = max(p["errors"] for p in wordsInFile)
    if max_errors == 0:
        print("\nNon hai parole difficili!")
        return

    difficili = [p for p in wordsInFile if p["errors"] == max_errors]
    print(f"\nElenco parole più difficili (numero di errori -> {max_errors}):")
    for i, p in enumerate(difficili, 1):
        print(f"{i}. {p['english']} -> {p['italian']}")

def reset_errori():
    if not wordsInFile:
        print("\nNessuna parola presente!")
        return

    conferma = input("\nSei sicuro di voler portare a 0 gli errori di TUTTE le parole? (s/N): ").strip().lower()
    if conferma == "s":
        for p in wordsInFile:
            p["errors"] = 0
        salva_parole()
        print("\nTutti i pesi sono stati resettati a 0 con successo.")
    else:
        print("\nOperazione annullata")

def main():
    while True:
        print("\n--- MENU VOCABOLI ---")
        print("1. Aggiungi parole")
        print("2. Fai un quiz normale")
        print("3. Elenca le parole difficili")
        print("4. Rimuovi una parola")
        print("5. Modifica una parola")
        print("6. Sposta parole tra quelle memorizzate")
        print("7. Quiz parole memorizzate")
        print("8. Resetta tutti gli errori a 0")
        print("9. Esci")

        scelta = input("Scelta: ").strip()

        if scelta == "1":
            aggiungi_parola()
        elif scelta == "2":
            quiz_normale()
        elif scelta == "3":
            elencaParoleDifficili()
        elif scelta == "4":
            rimuovi_parola()
        elif scelta == "5":
            modifica_parola()
        elif scelta == "6":
            sposta_parole_imparate()
        elif scelta == "7":
            quiz_imparate()
        elif scelta == "8":
            reset_errori()
        elif scelta == "9":
            print("Ritorno al menu principale...")
            break
        else:
            print("Opzione non valida!")

if __name__ == "__main__":
    main()