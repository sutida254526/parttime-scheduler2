# -*- coding: utf-8 -*-
import streamlit as st
from app_M2T1P8 import solver_parttime
import random, numpy as np

# --- ตั้ง seed ---
random.seed(42)
np.random.seed(42)

st.set_page_config(page_title="Part-time Scheduler", layout="wide")
st.title("🗓️ Part-time Employee Scheduler")
st.markdown("จัดตารางพนักงานพาร์ทไทม์สำหรับร้านอาหาร")

# --- ฟังก์ชันหัวข้อสวย ๆ (Card style) ---
def card_section(number, title, subtitle=None, bg_color="#F0F2F6"):
    st.markdown(f"""
    <div style="background-color:{bg_color}; padding:12px 16px; border-radius:12px; margin-bottom:16px;">
        <div style="display:flex; align-items:center; margin-bottom:6px;">
            <div style="
                width:32px; height:32px; 
                background-color:#1A2A4F; 
                border-radius:50%; 
                display:flex; 
                align-items:center; 
                justify-content:center; 
                color:white; font-weight:bold; font-size:16px;
                margin-right:10px;">
                {number}
            </div>
            <h3 style="margin:0; font-size:18px;">{title}</h3>
        </div>
        {f'<p style="color:#555; margin:0 0 0 42px;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

# --- 1. รายชื่อพนักงาน ---
card_section(1, "รายชื่อพนักงาน", "กรอกชื่อพนักงานคั่นด้วย ,")
employee_names_input = st.text_input("กรอกรายชื่อพนักงาน (คั่นด้วย ,)")
employee_names = [name.strip() for name in employee_names_input.split(",") if name.strip()]
num_employees = len(employee_names)

# --- 2. เงื่อนไขพนักงาน ---
card_section(2, "เงื่อนไขพนักงาน", "เลือกวันและกะที่สะดวกของแต่ละพนักงาน")
all_employees_avail = {}
day_map = {"อาทิตย์":1,"จันทร์":2,"อังคาร":3,"พุธ":4,"พฤหัส":5,"ศุกร์":6}
shift_map = {"1":1,"2":2,"3":3,"4":4}

for idx, name in enumerate(employee_names, start=1):
    with st.expander(f"🧑 {name}"):
        days = st.multiselect("วันสะดวก", list(day_map.keys()), key=f"days_{idx}")
        shifts = st.multiselect("กะสะดวก", list(shift_map.keys()), key=f"shifts_{idx}")
        emp_avail = {d_num: [shift_map[s] for s in shifts] if d_name in days and shifts else []
                     for d_name, d_num in day_map.items()}
        all_employees_avail[idx] = emp_avail

# --- 3. จำนวนพนักงานหลัก ---
card_section(3, "จำนวนพนักงานหลัก", "กรอกจำนวนพนักงานหลักที่ต้องการต่อแต่ละกะ")
cols = st.columns(4)
W_per_t = {t: col.number_input(f"กะ{t} ({t*2+9}:00-{t*2+11}:00)", min_value=0, value=1, step=1, key=f"main_{t}")
           for t, col in enumerate(cols, start=1)}

# --- 4. จำนวนพนักงานสำรอง ---
card_section(4, "จำนวนพนักงานสำรอง", "กรอกจำนวนพนักงานสำรองที่ต้องการต่อแต่ละกะ")
cols = st.columns(4)
W_backup = {t: col.number_input(f"กะ{t} ({t*2+9}:00-{t*2+11}:00)", min_value=0, value=1, step=1, key=f"backup_{t}")
            for t, col in enumerate(cols, start=1)}

# --- 5. จำกัดจำนวนกะสูงสุด/ต่ำสุด ---
card_section(5, "จำกัดจำนวนกะ", "กำหนดจำนวนกะสูงสุดและต่ำสุด/สัปดาห์ สำหรับพนักงานแต่ละประเภท")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**พนักงานหลัก**")
    max_shift_main = st.number_input("สูงสุด (กะ/สัปดาห์)", min_value=1, value=5)
    min_shift_main = st.number_input("ต่ำสุด (กะ/สัปดาห์)", min_value=0, value=2)
with col2:
    st.markdown("**พนักงานสำรอง**")
    max_shift_backup = st.number_input("สูงสุด (กะ/สัปดาห์)", min_value=1, value=3)
    min_shift_backup = st.number_input("ต่ำสุด (กะ/สัปดาห์)", min_value=0, value=1)

# --- เลือกเดือน ---
month = st.selectbox("เลือกเดือน", ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน",
                                     "กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"])

# --- ปุ่ม Solve ---
if st.button("สร้างตารางงาน"):
    data = {
        "num_employees": num_employees,
        "W_per_t": W_per_t,
        "max_shift_i": max_shift_main,
        "min_shift_i": min_shift_main,
        "P_idt": all_employees_avail,
        "cost_per_shift": {1:320,2:160,3:160,4:160},
        "absent": {}
    }
    result = solver_parttime(data)

    st.success(f"✅ ค่าใช้จ่ายรวม: {result['total_cost']} บาท/สัปดาห์")

    # ตารางพนักงานหลัก
    card_section("📝", "ตารางพนักงานหลัก (Main)")
    for d in range(1,7):
        st.write(f"Day {d}")
        for t in range(1,5):
            st.write(f"Shift {t}: {result['main'][(d,t)]}")

    # ตารางพนักงานสำรอง
    card_section("📝", "ตารางพนักงานสำรอง (Backup)")
    for d in range(1,7):
        st.write(f"Day {d}")
        for t in range(1,5):
            st.write(f"Shift {t}: {result['backup'][(d,t)]}")
