# 🤖 AI Pathfinder — Uninformed Search Algorithms

**AI 2002 - Artificial Intelligence | Assignment 1 | Spring 2026**  
**Developer: Ahmed Shakeel**

A fully animated AI Pathfinder that visualizes 6 uninformed (blind) search algorithms on an interactive grid with dynamic obstacle generation and real-time re-planning.

---

## 🎯 Algorithms Implemented

| # | Algorithm | Data Structure | Optimal? |
|---|-----------|---------------|----------|
| 1 | Breadth-First Search (BFS) | Queue (FIFO) | ✅ Yes |
| 2 | Depth-First Search (DFS) | Stack (LIFO) | ❌ No |
| 3 | Uniform-Cost Search (UCS) | Min-Heap | ✅ Yes |
| 4 | Depth-Limited Search (DLS) | Stack + Depth | ❌ No |
| 5 | Iterative Deepening DFS (IDDFS) | Stack (Restart) | ✅ Yes |
| 6 | Bidirectional Search | Two Queues | ✅ Yes |

---

## ✨ Features

- 🎨 **Step-by-step animation** — watch algorithms think in real time
- 🧱 **Draw/Erase walls** — Left click to draw, Right click to erase
- ⚡ **Dynamic Obstacles** — random walls spawn during search
- 🔄 **Auto Re-planning** — agent detects blockage and recalculates
- ⌨️ **Keyboard shortcuts** — Space, R, N, 1-6 keys
- 📊 **Live stats** — step counter and re-plan event tracker

---

## 🚀 Installation & Running

### 1. Clone the Repository
```bash
git clone https://github.com/AhmedShakeel/AI-Pathfinder-Uninformed-Search.git
cd AI-Pathfinder-Uninformed-Search
```

### 2. Install Dependencies
```bash
pip install pygame
```

### 3. Run the App
```bash
python ai_pathfinder.py
```

---

## 🎮 Controls

| Control | Action |
|---------|--------|
| `LEFT CLICK` drag | Draw static wall |
| `RIGHT CLICK` drag | Erase wall |
| `SPACE` | Start / Pause / Resume |
| `R` | Reset |
| `N` | Generate new maze |
| `1` to `6` | Select algorithm |
| `→ Arrow` | Manual step (when paused) |

---

## 🎨 Color Guide

| Color | Meaning |
|-------|---------|
| 🟢 Green | Start point |
| 🔴 Red | Target point |
| ⬛ Dark Grey | Static wall |
| 🟠 Orange | Dynamic obstacle |
| 🔵 Blue | Frontier (waiting) |
| 🟣 Purple | Explored nodes |
| 🟡 Yellow | Final path |

---

## 📁 Project Structure
```
AI-Pathfinder-Uninformed-Search/
│
├── ai_pathfinder.py     # Main application (all code)
├── README.md            # This file
└── requirements.txt     # Dependencies
```

---

## 📦 Requirements
```
pygame>=2.0.0
```

---

## 👨‍💻 Developer

**Ahmed Shakeel**  
AI 2002 — Artificial Intelligence  
Spring 2026

---

## 📝 License

This project is for educational purposes — AI 2002 Assignment 1.
```

---

## Step 3: requirements.txt — Ye Banao

GitHub pe **Add file → Create new file** karo

**File name:**
```
requirements.txt
```

**Content:**
```
pygame>=2.0.0
```

---

## Step 4: ai_pathfinder.py Upload Karo

GitHub pe **Add file → Upload files** → apni `ai_pathfinder.py` file drag karo → **Commit changes**

---

## Step 5: Commit Messages (Important for Viva!)

Har file alag commit mein daalo with these messages:
```
Initial commit: Project structure and README
```
```
Add: Core grid and dynamic obstacle system
```
```
Add: BFS and DFS implementations
```
```
Add: UCS with priority queue
```
```
Add: DLS and IDDFS implementations
```
```
Add: Bidirectional search algorithm
```
```
Add: Pygame GUI with step-by-step animation
```
```
Final: Complete AI Pathfinder with all 6 algorithms
