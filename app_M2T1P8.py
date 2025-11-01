# -*- coding: utf-8 -*-
"""
app_M2T1P8.py
Solver สำหรับตารางพนักงานพาร์ทไทม์
ใช้ร่วมกับ Streamlit app (app_ver_2.py)
"""


import pulp
import random
import numpy as np
random.seed(42)
np.random.seed(42)

def solver_parttime(data):
    # ตั้งค่า seed ให้ผลลัพธ์คงที่
    random.seed(42)
    np.random.seed(42)

    # ====== รับข้อมูลจาก app ======
    num_employees = data["num_employees"]
    W_per_t = data["W_per_t"]
    max_shift_i = data["max_shift_i"]
    all_employees_avail = data["P_idt"]
    cost_per_shift = data["cost_per_shift"]
    employee_absent = data.get("absent", {})

    # ====== Sets ======
    I = range(1, num_employees + 1)   # พนักงานพาร์ทไทม์ i = 1..N
    D = range(1, 7)                   # วัน d = 1..6 (อาทิตย์–ศุกร์)
    T = range(1, 5)                   # กะ t = 1..4

    # ====== Parameters ======
    C_it = {(i, t): cost_per_shift[t] for i in I for t in T}
    W_dt = {(d, t): W_per_t[t] for d in D for t in T}
    maxShift_i = {i: max_shift_i for i in I}

    # ====== Model ======
    model = pulp.LpProblem("PartTime_Scheduling", pulp.LpMinimize)

    # ====== Decision Variables ======
    M = pulp.LpVariable.dicts("main", (I, D, T), cat="Binary")     # พนักงานหลัก
    B = pulp.LpVariable.dicts("backup", (I, D, T), cat="Binary")   # พนักงานสำรอง

    # ====== Objective Function ======
    model += pulp.lpSum(C_it[(i, t)] * M[i][d][t] for i in I for d in D for t in T)

    # ====== Availability ======
    P_idt = {}
    for i in I:
        for d in D:
            for t in T:
                if d in all_employees_avail[i] and t in all_employees_avail[i][d]:
                    P_idt[(i, d, t)] = 1
                else:
                    P_idt[(i, d, t)] = 0

    # ====== Constraints ======


    # 5.1 จำนวนพนักงานหลักตามช่วงเวลา
    for d in D:
        for t in T:
            model += pulp.lpSum(M[i][d][t] for i in I) >= W_dt[(d, t)]

    # 5.2 จำนวนพนักงานสำรองตามช่วงเวลา
    for d in D:
        for t in T:
            model += pulp.lpSum(B[i][d][t] for i in I) >= W_dt[(d, t)]

    # 5.3 แต่ละคนต้องทำงานหลักอย่างน้อย 1 กะ/สัปดาห์
    for i in I:
        model += pulp.lpSum(M[i][d][t] for d in D for t in T) >= 1

    # 5.4 แต่ละคนต้องทำงานสำรองอย่างน้อย 1 กะ/สัปดาห์
    for i in I:
        model += pulp.lpSum(B[i][d][t] for d in D for t in T) >= 1

    # 5.5 จำกัดกะสูงสุดต่อสัปดาห์ (หลัก)
    for i in I:
        model += pulp.lpSum(M[i][d][t] for d in D for t in T) <= maxShift_i[i]

    # 5.6 จำกัดกะสูงสุดต่อสัปดาห์ (สำรอง)
    for i in I:
        model += pulp.lpSum(B[i][d][t] for d in D for t in T) <= maxShift_i[i]
    # 5.7 ห้ามเป็นหลักและสำรองในช่วงเวลาเดียวกัน
    for i in I:
        for d in D:
            for t in T:
                model += M[i][d][t] + B[i][d][t] <= 1
    # 5.8 ต้องเลือกจากพนักงานที่ว่าง
    for i in I:
        for d in D:
            for t in T:
              model += M[i][d][t] <= P_idt[(i, d, t)]
              model += B[i][d][t] <= P_idt[(i, d, t)]

    # 5.9 ความต่างของงานที่แต่ละคนได้รับไม่เกิน 1 กะ
    for i in I:
        for k in I:
            if i != k:
                model += (
                    pulp.lpSum(M[i][d][t] + B[i][d][t] for d in D for t in T) -
                    pulp.lpSum(M[k][d][t] + B[k][d][t] for d in D for t in T)
                ) <= 1
                model += (
                    pulp.lpSum(M[k][d][t] + B[k][d][t] for d in D for t in T) -
                    pulp.lpSum(M[i][d][t] + B[i][d][t] for d in D for t in T)
                ) <= 1
                
    for d in D:
        available = [i for i in I if any(all_employees_avail[i].get(d, []) and 1 in all_employees_avail[i][d])]
        print(f"Day {d} available for Shift 1:", available)
        
    for d in range(1,7):
        for t in range(1,5):
            avail = [i for i in data["P_idt"] if d in data["P_idt"][i] and t in data["P_idt"][i][d]]
            if len(avail) == 0:
                st.warning(f"⚠️ ไม่มีพนักงานว่างใน Day {d}, Shift {t}")

    # ====== Solve ======
    solver = pulp.PULP_CBC_CMD(msg=False, options=["randomSeed=42", "threads=1"])
    model.solve(solver)

    # ====== Results ======
    main_schedule = {(d, t): [i for i in I if pulp.value(M[i][d][t]) == 1] for d in D for t in T}
    backup_schedule = {(d, t): [i for i in I if pulp.value(B[i][d][t]) == 1] for d in D for t in T}
    total_cost = pulp.value(model.objective)
    

    return {
        "main": main_schedule,
        "backup": backup_schedule,
        "total_cost": total_cost,
        "status": pulp.LpStatus[model.status]
    }

