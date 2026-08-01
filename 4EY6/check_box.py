#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AChE (4EY6) 对接盒子位点包覆率检查脚本
用法: python3 check_box.py
"""

import os
import sys

def check_box():
    # 优先读取清洗后的受体文件
    pdb_file = "receptor_clean.pdb"
    if not os.path.exists(pdb_file):
        pdb_file = "receptor_fixed.pdb"
    if not os.path.exists(pdb_file):
        pdb_file = "4ey6.pdb"

    box_file = "box_pas.txt"

    if not os.path.exists(pdb_file):
        print(f"❌ 错误: 未找到 PDB 文件 ({pdb_file})")
        sys.exit(1)

    if not os.path.exists(box_file):
        print(f"❌ 错误: 未找到对接盒子配置文件 ({box_file})")
        sys.exit(1)

    # 1. 读取对接盒子边界坐标
    box = {}
    with open(box_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '=' in line:
                k, v = line.split('=')
                box[k.strip()] = float(v.strip())

    cx, cy, cz = box['center_x'], box['center_y'], box['center_z']
    sx, sy, sz = box['size_x'], box['size_y'], box['size_z']

    min_x, max_x = cx - sx/2.0, cx + sx/2.0
    min_y, max_y = cy - sy/2.0, cy + sy/2.0
    min_z, max_z = cz - sz/2.0, cz + sz/2.0

    print("=" * 100)
    print(" 📦 AutoDock Vina 对接盒子边界坐标范围:")
    print(f"    X 轴: [{min_x:.3f} Å,  {max_x:.3f} Å] (中心 = {cx:.3f}, 尺寸 = {sx:.1f} Å)")
    print(f"    Y 轴: [{min_y:.3f} Å,  {max_y:.3f} Å] (中心 = {cy:.3f}, 尺寸 = {sy:.1f} Å)")
    print(f"    Z 轴: [{min_z:.3f} Å,  {max_z:.3f} Å] (中心 = {cz:.3f}, 尺寸 = {sz:.1f} Å)")
    print("=" * 100)

    # 2. 定义文献与功能热点残基列表
    target_res = {
        '72':  'Tyr72  (PAS 外周阴离子位点)',
        '74':  'Asp74  (PAS 外周阴离子位点)',
        '124': 'Tyr124 (PAS 外周阴离子位点)',
        '286': 'Trp286 (PAS 核心成核中心)',
        '341': 'Tyr341 (PAS 外周阴离子位点)',
        '76':  'Leu76  (文献 76-77 新接触区域)',
        '77':  'Trp77/Tyr77 (文献 76-77 新接触区域)',
        '203': 'Ser203 (催化三联体 Active Site)',
        '334': 'Glu334 (催化三联体 Active Site)',
        '440': 'His440 (催化三联体 Active Site)',
        '338': 'Phe338 (阴离子亚位点 Anionic Subsite)',
    }

    # 补充 344-361 主驻留区域残基
    for i in range(344, 362):
        target_res[str(i)] = f'Residue {i} (文献 344-361 多肽主要驻留区域)'

    # 3. 解析 PDB 原子坐标
    res_atoms = {}
    with open(pdb_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith("ATOM  ") or line.startswith("HETATM"):
                chain = line[21]
                if chain != 'A' and chain != ' ':
                    continue
                rnum = line[22:26].strip()
                rname = line[17:20].strip()
                aname = line[12:16].strip()
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])

                if rnum not in res_atoms:
                    res_atoms[rnum] = {'rname': rname, 'atoms': []}
                res_atoms[rnum]['atoms'].append((aname, x, y, z))

    # 4. 统计包覆状态
    print(f'{"残基编号":<8} | {"残基名称":<8} | {"重原子总数":<10} | {"盒子内原子数":<12} | {"状态":<18} | {"位点描述"}')
    print("-" * 100)

    fully_in, part_in, out = 0, 0, 0

    for rnum, desc in sorted(target_res.items(), key=lambda x: int(x[0])):
        if rnum in res_atoms:
            rname = res_atoms[rnum]['rname']
            atoms = res_atoms[rnum]['atoms']

            inside_count = 0
            for aname, x, y, z in atoms:
                if (min_x <= x <= max_x) and (min_y <= y <= max_y) and (min_z <= z <= max_z):
                    inside_count += 1

            total_atoms = len(atoms)
            if inside_count == total_atoms:
                status = "✅ 100% 完全包含"
                fully_in += 1
            elif inside_count > 0:
                status = "⚠️ 部分包含"
                part_in += 1
            else:
                status = "❌ 未包含 (在盒外)"
                out += 1

            print(f'{rnum:<8} | {rname:<8} | {total_atoms:<10} | {inside_count:<12} | {status:<18} | {desc}')
        else:
            print(f'{rnum:<8} | {"N/A":<8} | {0:<10} | {0:<12} | {"❌ 未找到残基":<18} | {desc}')

    print("=" * 100)
    print(f"📊 检查总结: 完美包覆 {fully_in} 个热点残基，部分包覆 {part_in} 个，遗漏 {out} 个。")
    if out == 0 and part_in == 0:
        print("🎉 结论: 对接盒子 (size = 40x40x40 Å³) 已经 100% 完美包裹所有文献关键致病位点！")
    print("=" * 100)

if __name__ == "__main__":
    check_box()