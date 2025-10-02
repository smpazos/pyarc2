import numpy as np
import os, io, time
from datetime import datetime
import matplotlib.pyplot as plt
# from openpyxl import Workbook
# from openpyxl.drawing.image import Image as XLImage
from pyarc2 import Instrument, find_ids, ControlMode, ReadAt, ReadAfter, \
    IdleMode, DataMode, AuxDACFn, BiasOrder

now = datetime.now()
onlydate = now.strftime("%Y-%m-%d")
onlytime = now.strftime("%H%M%S")
save_dir = 'C:\\measurements\\'+onlydate+'\\'+onlytime+'\\arC_outputs\\'
os.makedirs(save_dir, exist_ok=True)

# ========= Device init =========

if 'arc' in globals():
    print("Arc2 is already connected.")
else:
    device_ids = find_ids()
    if len(device_ids) == 0:
        print("No devices found")
        raise SystemExit
    # fw_path = r"D:\QXY\PhD\2- Arctwo\Arctwo\efm03_20240918.bin"
    fw_path = "efm03_20240918.bin"
    arc = Instrument(device_ids[0], fw_path)
# arc.set_control_mode(ControlMode.Header)
arc.connect_to_gnd(np.array([], dtype=np.uint64))
print("🔍 Begin Open-loop Endurance Test")

# ========= Params =========
V_READ   = 0.1
V_SET    = 1       # fixed SET
V_RESET  = -1      # fixed RESET 
PW_CONST = 1000    # 1 µs
N_PULSE  = 1        # number of pulse

CHECK_INTERVAL   = 100
R_HRS_MIN        = 8000     #initial reset
WINDOW_THRESHOLD = 0.8        #HRS/LRS--let the window collapse
MAX_CYCLES       = int(1e9)
SAVE_INTERVAL    = 500      # in case the program crashes
LOW_CH, HIGH_CH = 4, 59

# Selector configuration
SEL_LOW = 0;
SEL_HI  = 1.1;
SEL_MAX = 2.5;

# ========= Output =========
# save_dir = r"D:\QXY\PhD\2- Arctwo\Arctwo\IV-results"
os.makedirs(save_dir, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
save_path = os.path.join(save_dir, f"{stamp}_OpenLoop_Endurance_{V_SET}_{V_RESET}_pw{PW_CONST/1000}μs.xlsx")

# wb = Workbook()
# wb.remove(wb.active)
# ws = wb.create_sheet("Summary")
# ws.append(["Cycle", "LRS(Ω)", "HRS(Ω)", "Window(HRS/LRS)"])

# ========= Read =========
def read_resistance(vread=0.05):
    I = arc.read_one(LOW_CH, HIGH_CH, vread)
    arc.execute(); arc.finalise_operation(); arc.wait()
    if abs(I) < 1e-10:
        return np.inf
    return abs(vread / I)

# ========= pulse generate =========
def apply_pulse(voltage, n_pulse=N_PULSE):
    for _ in range(n_pulse):
        arc.pulse_one(LOW_CH, HIGH_CH, voltage, PW_CONST)
        arc.execute(); arc.finalise_operation(); arc.wait()

# ========= Step 1: Recover to HRS =========
arc.config_aux_channels([(AuxDACFn.SELL, SEL_LOW), (AuxDACFn.SELH, SEL_HI)]).execute()

MAX_RECOVER_PULSES = 1
count = 0
while count < MAX_RECOVER_PULSES:
    apply_pulse(V_RESET)
    r0 = read_resistance(vread=-V_READ)
    count += N_PULSE
    time.sleep(0.01)
    if r0 >= R_HRS_MIN:
        print(f"✅ Recovered: R = {r0:.1f} Ω after {count} pulses")
        break
else:
    print("⚠️ Recover failed: did not reach HRS target")

# ========= Step 2: Endurance Loop =========
hrs_list, lrs_list, window_list = [], [], []
start_time = time.time()
stop_reason = "Reached MAX_CYCLES"

try:
    
    arc.execute()
    for cycle in range(1, MAX_CYCLES + 1):
        # --- SET ---
        # apply_pulse(V_SET)
        # lrs = read_resistance(vread=V_READ)
        lrs = -V_READ / arc.pulseread_one(LOW_CH, HIGH_CH, V_SET, PW_CONST, V_READ)
        lrs_list.append(lrs)
        
        # --- RESET ---
        # apply_pulse(V_RESET)
        # hrs = read_resistance(vread=V_READ)
        hrs = -V_READ / arc.pulseread_one(LOW_CH, HIGH_CH, V_RESET, PW_CONST, V_READ)
        hrs_list.append(hrs)

        # --- Window ---
        window = hrs / lrs if lrs > 0 else np.inf
        window_list.append(window)

        # ws.append([cycle, lrs, hrs, window])
        print(f"Cycle {cycle}: LRS={lrs:.1f} Ω, HRS={hrs:.1f} Ω, Window={window:.2f}")

        # time.sleep(0.05)

        # Save periodically
        if cycle % SAVE_INTERVAL == 0:
            # wb.save(save_path)
            print("save")

        # --- Check window every CHECK_INTERVAL ---
        if cycle % CHECK_INTERVAL == 0:
            recent = window_list[-CHECK_INTERVAL:]
            if all(w < WINDOW_THRESHOLD for w in recent):
                stop_reason = f"Window < {WINDOW_THRESHOLD} for {CHECK_INTERVAL} cycles"
                break

except Exception as e:
    print(f"\n Exception occurred: {e}")
    stop_reason = f"Error: {e}"
    arc.config_selectors([]).execute()

finally:
    # ========= After loop =========
    elapsed = time.time() - start_time
    print(f"\n⛔ Test stopped: {stop_reason}")
    print(f"⏱ Total runtime: {elapsed:.2f} seconds")

    # ws.append([])
    # ws.append([f"Stop reason: {stop_reason}"])
    # ws.append([f"Runtime: {elapsed:.2f} seconds"])

    # ========= Plots (only if data exists) =========
    if len(hrs_list) > 0 and len(lrs_list) > 0:
        # 1. Resistance vs Cycle
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        ax1.plot(range(1, len(hrs_list)+1), hrs_list, "ro-", label="HRS")
        ax1.plot(range(1, len(lrs_list)+1), lrs_list, "bo-", label="LRS")
        ax1.set_xlabel("Cycle index")
        ax1.set_ylabel("Resistance (Ω)")
        ax1.set_yscale("log")
        ax1.set_title("Resistance vs Cycle")
        ax1.grid(True, alpha=0.3, which="both")
        ax1.legend()
        buf1 = io.BytesIO()
        fig1.savefig(buf1, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig1); buf1.seek(0)
        # ws.add_image(XLImage(buf1), "F2")

        # 2. HRS distribution
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        ax2.hist(hrs_list, bins=20, color="red", edgecolor="k", alpha=0.7)
        ax2.set_xlabel("HRS (Ω)")
        ax2.set_ylabel("Count")
        ax2.set_title("HRS Distribution")
        ax2.ticklabel_format(style="sci", axis="x", scilimits=(0,0))
        buf2 = io.BytesIO()
        fig2.savefig(buf2, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig2); buf2.seek(0)
        # ws.add_image(XLImage(buf2), "G33")

        # 3. LRS distribution
        fig3, ax3 = plt.subplots(figsize=(5, 4))
        ax3.hist(lrs_list, bins=20, color="blue", edgecolor="k", alpha=0.7)
        ax3.set_xlabel("LRS (Ω)")
        ax3.set_ylabel("Count")
        ax3.set_title("LRS Distribution")
        ax3.ticklabel_format(style="sci", axis="x", scilimits=(0,0))
        buf3 = io.BytesIO()
        fig3.savefig(buf3, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig3); buf3.seek(0)
        # ws.add_image(XLImage(buf3), "R33")

        del buf1, buf2, buf3
    else:
        print("⚠️ No data collected, skipping plots")

    # ========= Save =========
    # wb.save(save_path)
    print(f"\n✅ Done. Results saved to {save_path}")
