from threading import Thread

from QuantumKat.quantum_kat import quantum_bot

if __name__ == "__main__":
    quantum_kat_thread = Thread(target=quantum_bot.run)
    quantum_kat_thread.start()
    quantum_kat_thread.join()
