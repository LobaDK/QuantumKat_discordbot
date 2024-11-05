from threading import Thread, Event

from QuantumKat.quantum_kat import quantum_bot

threads: list[Thread] = []
restart_quantum_kat_event = Event()


if __name__ == "__main__":
    threads.append(Thread(target=quantum_bot.run, name="QuantumKat"))

    for thread in threads:
        thread.start()

    while True:
        # Wait for the event to be set, then reset it
        restart_quantum_kat_event.wait()
        restart_quantum_kat_event.clear()

        for thread in [t for t in threads if t.name == "QuantumKat"]:
            thread.join()  # Wait for the thread to finish
            threads.remove(thread)

        # Create a new thread and start it
        new_thread = Thread(target=quantum_bot.run, name="QuantumKat")
        new_thread.start()
        threads.append(new_thread)
