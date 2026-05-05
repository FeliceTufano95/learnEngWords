import random
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
DATA_DIR.mkdir(exist_ok=True)

FILE_PREPOSIZIONI = DATA_DIR / "preposizioni.json"

def carica_json(file_path):
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Attenzione: il file {file_path.name} non è un JSON valido. Verrà inizializzato vuoto.")
    return []

prepositionsInFile = carica_json(FILE_PREPOSIZIONI)

def salva_preposizioni():
    with open(FILE_PREPOSIZIONI, "w", encoding="utf-8") as f:
        json.dump(prepositionsInFile, f, indent=4, ensure_ascii=False)

def trova_voce(word):
    for p in prepositionsInFile:
        if p["word"].lower() == word.lower():
            return p
    return None

def aggiungi_voce():
    print("\nAggiungi nuove parole con preposizioni (INVIO vuoto per terminare)")
    while True:
        word = input("Parola: ").strip()
        if not word:
            break

        esistente = trova_voce(word)
        if esistente:
            print(f"'{word}' è già presente. Usa l'opzione per aggiungere una nuova preposizione.")
            continue

        raw_preps = input("Inserisci una o più preposizioni separate da virgola: ").strip().lower()
        if not raw_preps:
            print("Devi inserire almeno una preposizione.")
            continue

        preps = [x.strip() for x in raw_preps.split(",") if x.strip()]
        preps = list(dict.fromkeys(preps))

        prepositionsInFile.append({
            "word": word,
            "prepositions": preps,
            "errors": 0
        })

        print(f"Aggiunta: {word} -> {', '.join(preps)}\n")

    salva_preposizioni()

def aggiungi_preposizione_a_voce():
    if not prepositionsInFile:
        print("\nNessuna voce salvata!")
        return

    word = input("Inserisci la parola a cui vuoi aggiungere una preposizione: ").strip()
    voce = trova_voce(word)

    if not voce:
        print(f"La parola '{word}' non è presente.")
        return

    print(f"Preposizioni attuali per '{voce['word']}': {', '.join(voce['prepositions'])}")

    nuova_prep = input("Nuova preposizione da aggiungere: ").strip().lower()
    if not nuova_prep:
        print("Nessuna preposizione inserita.")
        return

    if nuova_prep in [p.lower() for p in voce["prepositions"]]:
        print(f"La preposizione '{nuova_prep}' è già presente per '{voce['word']}'.")
        return

    voce["prepositions"].append(nuova_prep)
    salva_preposizioni()
    print(f"Aggiunta preposizione '{nuova_prep}' a '{voce['word']}'.")

def rimuovi_preposizione_da_voce():
    if not prepositionsInFile:
        print("\nNessuna voce salvata!")
        return

    word = input("Inserisci la parola da cui rimuovere una preposizione: ").strip()
    voce = trova_voce(word)

    if not voce:
        print(f"La parola '{word}' non è presente.")
        return

    if not voce["prepositions"]:
        print("Questa voce non ha preposizioni salvate.")
        return

    print(f"\nPreposizioni per '{voce['word']}':")
    for i, prep in enumerate(voce["prepositions"], 1):
        print(f"{i}. {prep}")

    scelta = input("Numero della preposizione da rimuovere: ").strip()

    if not scelta.isdigit():
        print("Scelta non valida.")
        return

    idx = int(scelta) - 1
    if idx < 0 or idx >= len(voce["prepositions"]):
        print("Scelta non valida.")
        return

    rimossa = voce["prepositions"].pop(idx)

    if not voce["prepositions"]:
        conferma = input("Non ci sono più preposizioni per questa parola. Vuoi eliminare l'intera voce? (s/N): ").strip().lower()
        if conferma == "s":
            prepositionsInFile.remove(voce)
            print(f"Voce '{voce['word']}' eliminata completamente.")
        else:
            print("Attenzione: la voce è rimasta senza preposizioni.")

    salva_preposizioni()
    print(f"Preposizione '{rimossa}' rimossa con successo.")

def modifica_voce():
    if not prepositionsInFile:
        print("\nNessuna voce salvata!")
        return

    search = input("Inserisci parte della parola da modificare: ").strip().lower()
    matching = [p for p in prepositionsInFile if search in p["word"].lower()]

    if not matching:
        print(f"Nessuna parola trovata che contenga '{search}'.")
        return

    print("\nVoci trovate:")
    for i, p in enumerate(matching, 1):
        print(f"{i}. {p['word']} -> {', '.join(p['prepositions'])} (errors: {p['errors']})")

    scelta = input("Seleziona il numero della voce da modificare: ").strip()
    if not scelta.isdigit() or int(scelta) < 1 or int(scelta) > len(matching):
        print("Scelta non valida.")
        return

    voce = matching[int(scelta) - 1]

    nuova_parola = input(f"Nuova parola (INVIO per lasciare '{voce['word']}'): ").strip()
    if nuova_parola:
        voce["word"] = nuova_parola

    salva_preposizioni()
    print(f"Voce aggiornata: {voce['word']} -> {', '.join(voce['prepositions'])}")

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

def quiz_preposizioni():
    if not prepositionsInFile:
        print("\nNessuna voce disponibile per il quiz.")
        return

    num = input(f"Quante parole vuoi nel quiz? (max {len(prepositionsInFile)}): ").strip()
    num = int(num) if num.isdigit() else 5

    selezionate = weighted_sample_no_replacement(prepositionsInFile, num)

    print(f"\nQuiz preposizioni: {len(selezionate)} parole")
    print("Rispondi 's' se ricordi la/le preposizione/i, 'n' se non la/le ricordi.\n")

    for i, p in enumerate(selezionate, 1):
        risposta = input(f"{i}. '{p['word']}' -> ti ricordi la preposizione? (s/n): ").strip().lower()

        if risposta == "s":
            print("Perfetto, passiamo alla prossima.")
            if p["errors"] > 0:
                p["errors"] -= 1
        else:
            print(f"Preposizione/i corretta/e: {', '.join(p['prepositions'])}")
            p["errors"] += 1

    salva_preposizioni()

def elenca_difficili():
    if not prepositionsInFile:
        print("\nNessuna voce presente!")
        return

    max_errors = max(p["errors"] for p in prepositionsInFile)
    if max_errors == 0:
        print("\nNon hai ancora voci difficili!")
        return

    difficili = [p for p in prepositionsInFile if p["errors"] == max_errors]

    print(f"\nVoci più difficili (errori = {max_errors}):")
    for i, p in enumerate(difficili, 1):
        print(f"{i}. {p['word']} -> {', '.join(p['prepositions'])}")

def elenca_tutte():
    if not prepositionsInFile:
        print("\nNessuna voce salvata!")
        return

    print("\nElenco completo:")
    for i, p in enumerate(prepositionsInFile, 1):
        print(f"{i}. {p['word']} -> {', '.join(p['prepositions'])} (errors: {p['errors']})")

def reset_errori():
    if not prepositionsInFile:
        print("\nNessuna voce presente!")
        return

    conferma = input("Sei sicuro di voler resettare tutti gli errori a 0? (s/N): ").strip().lower()
    if conferma == "s":
        for p in prepositionsInFile:
            p["errors"] = 0
        salva_preposizioni()
        print("Tutti gli errori sono stati resettati.")
    else:
        print("Operazione annullata.")

def main():
    while True:
        print("\n--- MENU PREPOSIZIONI ---")
        print("1. Aggiungi nuova parola con preposizioni")
        print("2. Aggiungi una preposizione a una parola esistente")
        print("3. Rimuovi una preposizione da una parola")
        print("4. Modifica una parola")
        print("5. Fai un quiz")
        print("6. Elenca le voci difficili")
        print("7. Elenca tutte le voci")
        print("8. Resetta tutti gli errori a 0")
        print("9. Esci")

        scelta = input("Scelta: ").strip()

        if scelta == "1":
            aggiungi_voce()
        elif scelta == "2":
            aggiungi_preposizione_a_voce()
        elif scelta == "3":
            rimuovi_preposizione_da_voce()
        elif scelta == "4":
            modifica_voce()
        elif scelta == "5":
            quiz_preposizioni()
        elif scelta == "6":
            elenca_difficili()
        elif scelta == "7":
            elenca_tutte()
        elif scelta == "8":
            reset_errori()
        elif scelta == "9":
            print("Ritorno al menu principale...")
            break
        else:
            print("Opzione non valida!")

if __name__ == "__main__":
    main()