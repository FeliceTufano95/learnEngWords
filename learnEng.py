from src import vocaboli, preposizioni

def main():
    while True:
        print("\n=== LEARN ENG ===")
        print("1. Gestione vocaboli")
        print("2. Gestione preposizioni")
        print("3. Esci")

        scelta = input("Scelta: ").strip()

        if scelta == "1":
            vocaboli.main()
        elif scelta == "2":
            preposizioni.main()
        elif scelta == "3":
            print("Uscita...")
            break
        else:
            print("Opzione non valida!")

if __name__ == "__main__":
    main()