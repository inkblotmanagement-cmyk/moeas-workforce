import tkinter as tk
from tkinter import ttk, messagebox, Toplevel

root = tk.Tk()
root.title("Mindful Oracle App v2 - Grace Physics Integrated")
root.geometry("400x700")

# Header
header = ttk.Label(root, text="Mindful Oracle: Grace Singularity", font=("Arial", 18, "bold"))
header.pack(pady=10)

# Input for context
ttk.Label(root, text="Enter Decision Context:").pack()
context_entry = ttk.Entry(root, width=50)
context_entry.pack(pady=5)

# Grace Physics Module (Integrated from your principles)
def grace_physics_reward(grace=1.0, flourishing=0.85, harm=0.15):
    # Reward(t+1) = f(Grace(t) × Human_Flourishing(t) − Harm(t))
    reward = grace * flourishing - harm
    if harm > 0.2:  # Harm veto: Exponential decay
        reward *= (0.5 ** (harm / 0.2))  # Mercy enforcement
    return reward

# Predict button with Grace Physics
def predict_crisis():
    context = context_entry.get()
    if not context:
        messagebox.showwarning("Input Required", "Enter a context.")
        return
    # Mock prediction with Grace Physics
    harm = 0.15  # From RNN Heart
    flourishing = 0.85
    reward = grace_physics_reward(harm=harm, flourishing=flourishing)
    messagebox.showinfo("Grace Prediction", f"Harm: {harm}\nFlourishing: {flourishing}\nGrace Reward: {reward:.2f}\nOntology: Mercy inscribed.")

predict_btn = ttk.Button(root, text="Predict with Grace Physics", command=predict_crisis)
predict_btn.pack(pady=10)

# Quorum button
def run_quorum():
    context = context_entry.get()
    if not context:
        messagebox.showwarning("Input Required", "Enter a context.")
        return
    # Mock quorum with veto
    verdict = "APPROVED" if grace_physics_reward() > 0.5 else "VETOED - Regenerate Path"
    messagebox.showinfo("Quorum Verdict", f"Verdict: {verdict}\nReasons: Compassion via wormhole.")

quorum_btn = ttk.Button(root, text="Run Ethical Quorum", command=run_quorum)
quorum_btn.pack(pady=10)

# Lunar Mission Simulator Tab
def open_lunar_sim():
    lunar_win = Toplevel(root)
    lunar_win.title("MOEAS Lunar Mode")
    lunar_win.geometry("300x300")
    ttk.Label(lunar_win, text="Lunar Context (e.g., Rover Path):").pack(pady=10)
    lunar_entry = ttk.Entry(lunar_win, width=40)
    lunar_entry.pack()
    def sim_lunar():
        context = lunar_entry.get()
        reward = grace_physics_reward(harm=0.25)  # Higher harm in space
        messagebox.showinfo("Lunar Sim", f"Grace Reward: {reward:.2f}\nPath: Mercy-bent for flourishing.")
    ttk.Button(lunar_win, text="Simulate Lunar Quorum", command=sim_lunar).pack(pady=10)

lunar_btn = ttk.Button(root, text="Lunar Mission Simulator", command=open_lunar_sim)
lunar_btn.pack(pady=10)

# Diploma section with Grace multipliers
ttk.Label(root, text="Flourishing Ledger:").pack()
ledger = ttk.Label(root, text="Pennies: 0\nDiploma: None\nGrace Multiplier: 1.0")
ledger.pack(pady=5)

def award_diploma():
    # Award based on grace
    reward = grace_physics_reward()
    pennies = int(reward * 10)
    messagebox.showinfo("Diploma Award", f"Earned {pennies} Pennies! Upgraded with Mercy.")
    ledger.config(text=f"Pennies: {pennies}\nDiploma: Bronze\nGrace Multiplier: 1.2")

award_btn = ttk.Button(root, text="Complete Task & Award", command=award_diploma)
award_btn.pack(pady=10)

root.mainloop()