import sys
import os

# Add root directory to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.simulation.machine import MachineState

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_status(machine):
    status = machine.get_status()
    t = status['telemetry']
    print("-" * 50)
    print(f" TIME: {t['timer']}s  |  STATE: {status['state']}")
    print("-" * 50)
    print(f" 🌡️  TEMP:   {t['temp']} °C")
    print(f" ⚡ POWER:  {t['power']} kW")
    print(f" 💧 FLOW:   {t['flow']} LPM")
    print("-" * 50)

def main():
    machine = MachineState()
    print("🤖 Interactive Machine Simulator v1.0")
    print("Type 'help' for commands.")
    
    while True:
        try:
            cmd = input("\nSim > ").strip().lower()
            
            if cmd == "help":
                print("\nCommands:")
                print("  step    -> Move forward 1 second")
                print("  start   -> Start a new cycle (IDLE -> LOADING)")
                print("  status  -> Show current telemetry")
                print("  heat    -> Cheat: Force state to HEATING")
                print("  quench  -> Cheat: Force state to QUENCH")
                print("  exit    -> Quit")
                
            elif cmd == "step":
                machine.update()
                print_status(machine)
                
            elif cmd == "start":
                machine.start_cycle()
                print("🚀 Cycle Started!")
                print_status(machine)
            
            elif cmd == "status":
                print_status(machine)
                
            elif cmd == "heat":
                machine.transition_to(MachineState.HEATING)
                print("🔥 Forced HEATING Mode")
                
            elif cmd == "quench":
                machine.transition_to(MachineState.QUENCH)
                print("💦 Forced QUENCH Mode")

            elif cmd == "fault":
                machine.inject_fault()
                
            elif cmd == "exit":
                print("Bye!")
                break
                
            else:
                print("Unknown command. Type 'help'.")
                
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
