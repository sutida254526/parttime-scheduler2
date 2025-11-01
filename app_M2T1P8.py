# -*- coding: utf-8 -*-
"""
app_M2T1P8.py
Solver สำหรับตารางพนักงานพาร์ทไทม์
ใช้ร่วมกับ Streamlit app (app_ver_2.py)
"""

import pulp
import random
import numpy as np

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
    employee_absent = data["absent"]

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

    # 1️⃣ จำนวนพนักงานหลักตามช่วงเวลา
    for d in D:
        for t in T:
            model += pulp.lpSum(M[i][d][t] for i in I) >= W_dt[(d, t)]

    # 2️⃣ จำนวนพนักงานสำรองตามช่วงเวลา
    for d in D:
        for t in T:
            model += pulp.lpSum(B[i][d][t] for i in I) >= W_dt[(d, t)]

    # 3️⃣ แต่ละคนต้องทำงานหลักอย่างน้อย 1 กะ/สัปดาห์
    for i in I:
        model += pulp.lpSum(M[i][d][t] for d in D for t in T) >= 1

    # 4️⃣ แต่ละคนต้องทำงานสำรองอย่างน้อย 1 กะ/สัปดาห์
    for i in I:
        model += pulp.lpSum(B[i][d][t] for d in D for t in T) >= 1

    # 5️⃣ จำกัดจำนวนกะสูงสุดต่อสัปดาห์
    for i in I:
        model += pulp.lpSum(M[i][d][t] + B[i][d][t] for d in D for t in T) <= maxShift_i[i]

    # 6️⃣ ห้ามเป็นหลักและสำรองในช่วงเวลาเดียวกัน
    for i in I:
        for d in D:
            for t in T:
                model += M[i][d][t] + B[i][d][t] <= 1

    # 7️⃣ ต้องเลือกจากพนักงานที่ว่าง
    for i in I:
        for d in D:
            for t in T:
                model += M[i][d][t] <= P_idt[(i, d, t)]
                model += B[i][d][t] <= P_idt[(i, d, t)]

    # 8️⃣ ห้ามให้คนที่ "ขาด" มาทำกะนั้น
    for i in I:
        if i in employee_absent:
            for (d, t) in employee_absent[i]:
                model += M[i][d][t] == 0
                model += B[i][d][t] == 0

    # 9️⃣ ความต่างของจำนวนกะที่แต่ละคนได้รับไม่เกิน 1
    for i in I:
        for k in I:
            if i != k:
                diff = pulp.lpSum(M[i][d][t] + B[i][d][t] for d in D for t in T) - \
                       pulp.lpSum(M[k][d][t] + B[k][d][t] for d in D for t in T)
                model += diff <= 1
                model += -diff <= 1

    # ====== Solve ======
    solver = pulp.PULP_CBC_CMD(msg=False, options=["randomSeed=42"])
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

