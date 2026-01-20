import sqlite3
import os

# Define DB Path directly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "simulation_v2.db")

def verify_sync():
    print(f"📂 Checking Database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("❌ ERROR: Database file not found!")
        return

    with open("backend/db_report.txt", "w", encoding='utf-8') as f:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10) # 10s timeout for locks
            cursor = conn.cursor()
            
            # 1. Check SimRun
            f.write("--- SIM RUNS ---\n")
            cursor.execute("SELECT id, status, total_rows FROM sim_runs WHERE id=1")
            run = cursor.fetchone()
            if run:
                f.write(f"✅ Found SimRun(id=1): Status={run[1]}, TotalRows={run[2]}\n")
            else:
                f.write("❌ SimRun(id=1) NOT FOUND. (Startup initialization failed?)\n")
            f.flush()

            # 2. Check Telemetry Count
            f.write("\n--- TELEMETRY ---\n")
            try:
                cursor.execute("SELECT COUNT(*) FROM telemetry")
                count = cursor.fetchone()[0]
                f.write(f"📊 Total Rows: {count}\n")
            except Exception as e:
                 f.write(f"❌ Could not count telemetry: {e}\n")
                 count = 0
            f.flush()

            # 3. Last 3 Rows
            if count > 0:
                f.write("\n📝 LAST 3 RECORDS:\n")
                cursor.execute("SELECT id, timestamp_sim, state, part_id, ok_count, ng_count FROM telemetry ORDER BY id DESC LIMIT 3")
                rows = cursor.fetchall()
                for row in rows:
                    f.write(f"ID: {row[0]} | Time: {row[1]} | State: {row[2]}\n")
                    f.write(f"   Part: {row[3]} | OK: {row[4]} | NG: {row[5]}\n")
                    f.write("-" * 40 + "\n")
            else:
                f.write("⚠️ No telemetry data found. (Machine has not produced any parts yet?)\n")
            f.flush()

            conn.close()

        except Exception as e:
            f.write(f"❌ DATABASE ERROR: {e}\n")
            f.flush()

if __name__ == "__main__":
    verify_sync()
