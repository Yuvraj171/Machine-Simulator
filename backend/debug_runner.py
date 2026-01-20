import sys
import os
import time
import random

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.simulation.machine import MachineState

def run_debug_session():
    print("🛠️ DEBUG SESSION STARTED (Extended for Quench Verification)")
    machine = MachineState()
    
    print("1️⃣ STARTING CYCLE...")
    machine.start_cycle()
    
    print(f"   Initial State: {machine.state}")
    
    # Simulate 50 ticks (approx 10s at 0.2s/tick, but here we sleep 0.1s so it's faster)
    max_ticks = 100 
    quench_seen = False

    for i in range(max_ticks):
        machine.update()
        
        # Check Quench integrity
        if machine.state == "QUENCH":
            quench_seen = True
            if machine.current_flow == 120.0 and machine.current_pressure == 3.5:
                print(f"   ✅ QUENCH OK: Flow={machine.current_flow} | Press={machine.current_pressure}")
            else:
                print(f"   ❌ QUENCH FAILURE: Flow={machine.current_flow} | Press={machine.current_pressure}")
        
        # Check Heating integrity
        if machine.state == "HEATING":
             if machine.current_power < 50.0:
                 print(f"   ❌ HEATING FAILURE: Power={machine.current_power}")
        
        # Faster simulation for debug
        time.sleep(0.05) 
        
        if machine.state == "UNLOADING":
            print("🏁 CYCLE COMPLETED")
            break

    if not quench_seen:
        print("⚠️ NEVER REACHED QUENCH STATE!")

if __name__ == "__main__":
    run_debug_session()
