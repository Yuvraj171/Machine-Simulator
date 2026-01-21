from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.simulation.generator import SimulationGenerator
from backend.simulation.machine import MachineState

router = APIRouter(
    prefix="/simulation",
    tags=["simulation"]
)

from backend.simulation.persistence import SimulationPersistence

# Global Machine Instance (Singleton for "Live" View)
active_machine = MachineState()
persistence_layer = SimulationPersistence()

# Link them (Dependency Injection via Property or Init would be cleaner, but simple setter works here)
active_machine.persistence = persistence_layer 

import asyncio
import threading
import time

@router.post("/start")
async def start_simulation(db: AsyncSession = Depends(get_db)): # Removed BackgroundTasks arg
    """
    Starts a LIVE simulation cycle (Real-time).
    """
    if active_machine.state != "IDLE":
        # Force restart behavior might be safer or just return running
        pass
    
    # 1. Start the DB Worker (if not running)
    if not persistence_layer.is_running:
        asyncio.create_task(persistence_layer.start_worker())
    
    # 2. Start Cycle
    active_machine.start_cycle()
    
    # 3. Launch Simulation Loop (Robust)
    sim_thread = threading.Thread(target=run_live_simulation_thread, daemon=True)
    sim_thread.start()
    
    return {"message": "Live Simulation Started", "mode": "REAL_TIME"}

def run_live_simulation_thread():
    """
    Ticks the machine every 0.2 seconds (5Hz).
    Running in a THREAD allows it to survive past the HTTP request.
    """
    print("🚀 LIVE SIMULATION THREAD STARTED", flush=True)
    try:
        while active_machine.state != "IDLE" and active_machine.state != "DOWN":
            active_machine.update()
            time.sleep(0.2) # Sync sleep in thread
        
        print(f"🏁 LIVE SIMULATION ENDED. State: {active_machine.state}", flush=True)
        
    except Exception as e:
        import traceback
        print(f"❌ CRITICAL SIMULATION CRASH: {e}", flush=True)
        traceback.print_exc()
        active_machine.transition_to("DOWN") # Safe Fallback
    
    finally:
        # This part needs to be async, but we are in a sync thread.
        # We need to run it in the event loop.
        # A common pattern is to get the event loop and run the async function.
        # However, for a simple stop_worker, if it's just setting a flag, it might be okay.
        # If it involves actual async I/O, it needs to be awaited in an async context.
        # For now, assuming persistence_layer.stop_worker() can be called from a thread
        # or that it internally handles its async nature (e.g., by scheduling on the event loop).
        # A more robust solution would involve a queue or a dedicated async thread executor.
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.call_soon_threadsafe(lambda: asyncio.create_task(persistence_layer.stop_worker()))
            else:
                # If the event loop is not running (e.g., app shutdown),
                # we might not be able to stop it cleanly.
                # For simplicity, we'll just call it directly if no loop is running,
                # assuming it's safe or will be handled by app shutdown.
                asyncio.run(persistence_layer.stop_worker())
        except RuntimeError:
            # No running event loop, try to run it directly if possible
            asyncio.run(persistence_layer.stop_worker())


@router.post("/reset")
async def reset_simulation(db: AsyncSession = Depends(get_db)):
    """
    Resets the machine to IDLE state and updates session tracking.
    """
    from datetime import datetime
    from backend.models import SimRun
    from sqlalchemy import select
    
    active_machine.reset()
    
    # Update session_start_time for "Current Session" export filter
    result = await db.execute(select(SimRun).where(SimRun.id == 1))
    sim_run = result.scalars().first()
    if sim_run:
        sim_run.session_start_time = datetime.now() # Use Local System Time (matches UI)
        await db.commit()
        print(f"📅 Session start time updated for run_id=1 to {sim_run.session_start_time}")
    
    return {"message": "Machine reset to IDLE", "new_state": active_machine.state}

@router.post("/stop")
async def stop_simulation():
    """
    Safely halts the machine (IDLE) but preserves counters/coil life.
    """
    active_machine.stop()
    return {"message": "Machine Stopped", "new_state": active_machine.state}

@router.post("/manual-control")
async def manual_control(enabled: bool, temp_limit: float = 1000.0, flow_target: float = 120.0):
    """
    Sets Manual Process Limits.
    enabled: True to override physics limits.
    temp_limit: Max Temp (Ceiling).
    flow_target: Target Flow (Center).
    """
    active_machine.manual_mode = enabled
    active_machine.manual_limits = {
        "temp_limit": temp_limit,
        "flow_target": flow_target
    }
    mode = "MANUAL" if enabled else "AUTO"
    print(f"🎛️ MANUAL CONTROL: {mode} | Temp<={temp_limit} | Flow~={flow_target}")
    return {"message": f"Manual Mode set to {mode}", "limits": active_machine.manual_limits}

@router.post("/inject-fault")
async def inject_fault(type: str = None):
    """
    Manually triggers a breakdown in the active machine.
    type: Optional specific fault (hose_burst, power_surge, etc)
    """
    active_machine.inject_fault(fault_type=type)
    return {"message": f"Fault injected: {type or 'Random'}", "new_state": active_machine.state}

@router.post("/repair")
async def repair_simulation():
    """
    Fixes the machine (clears drift/faults) without resetting counters.
    """
    active_machine.repair()
    return {"message": "Machine Repaired", "new_state": active_machine.state}




@router.get("/status")
async def get_status():
    """
    Returns the current live status of the machine.
    """
    return active_machine.get_status()
