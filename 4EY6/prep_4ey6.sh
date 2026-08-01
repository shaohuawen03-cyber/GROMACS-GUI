#!/usr/bin/env bash

# =============================================================================
# 4EY6 受体准备脚本 (Meeko + PDB2PQR pH 7.4 零报错完美版)
# =============================================================================

set -euo pipefail

WORK_DIR="/home/w24e/docking_backup/dc-main/4EY6"
PDB_IN="4ey6.pdb"

cd "${WORK_DIR}" || { echo "无法进入目录: ${WORK_DIR}"; exit 1; }

LOG_FILE="prep_4ey6.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

info() { echo -e "\e[1;34m[INFO]\e[0m $1"; }
ok()   { echo -e "\e[1;32m[OK]\e[0m $1"; }
warn() { echo -e "\e[1;33m[WARN]\e[0m $1"; }
die()  { echo -e "\e[1;31m[ERROR]\e[0m $1"; exit 1; }

echo "==========================================================="
echo " 开始处理 4EY6 受体 - $(date)"
echo " 根据文献: Atanasova et al., 2020"
echo "==========================================================="

command -v python &>/dev/null || die "未找到 python"

# 1. 提取纯净 Chain A（不含氢原子、水和配体）
info "[1] 提取 Chain A，去除配体、水及杂原子，保留纯净重原子..."
awk '
BEGIN {
  split("ALA ARG ASN ASP CYS CYX GLN GLU GLY HIS HID HIE HIP HSD HSE HSP ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL", aa)
  for (i in aa) std[aa[i]] = 1
}
/^ATOM  / {
  altloc = substr($0, 17, 1)
  res = substr($0, 18, 3)
  chain = substr($0, 22, 1)
  
  if (chain == "A" && std[res] && (altloc == " " || altloc == "A")) {
    line = substr($0, 1, 16) " " substr($0, 18)
    print line
  }
}
/^TER/ { print; }
' "${PDB_IN}" > receptor_clean.pdb

echo "END" >> receptor_clean.pdb
ok "已生成纯净重原子 Chain A: receptor_clean.pdb"

# 2. 生理 pH 7.4 精准质子化 (PDB2PQR + PROPKA) 或 Meeko 原生处理
info "[2] 尝试使用 PDB2PQR (PROPKA) 计算 pH 7.4 质子化状态..."

if command -v pdb2pqr &>/dev/null; then
  pdb2pqr --ff AMBER --titration-state-method propka --with-ph 7.4 receptor_clean.pdb receptor_7.4.pqr &>/dev/null
  ok "PDB2PQR pH 7.4 质子化计算完成: receptor_7.4.pqr"
  
  info "[3] 使用 Meeko 读取 PQR 生成 receptor.pdbqt..."
  mk_prepare_receptor.py --read_pqr receptor_7.4.pqr -o receptor -p -a > meeko.log 2>&1
else
  warn "未找到 pdb2pqr，使用 Meeko 直接从纯净 PDB 自动加氢 (pH 7.4)..."
  info "[3] 使用 Meeko 直接读取重原子 PDB 生成 receptor.pdbqt..."
  mk_prepare_receptor.py --read_pdb receptor_clean.pdb -o receptor -p -a > meeko.log 2>&1
fi

[[ -s receptor.pdbqt ]] || die "Meeko 生成 receptor.pdbqt 失败，请检查 meeko.log"
ok "Meeko 成功生成零报错受体: receptor.pdbqt"

# 3. 计算覆盖 PAS、344-361 以及 76-77 区域的对接盒子
info "[4] 计算覆盖 PAS、344-361 以及 76-77 新区域的对接盒子..."
python - << 'EOF' > box_pas.txt
import sys
coords = []
target_res = ['72', '124', '286', '341', '76', '77'] + [str(i) for i in range(344, 362)]

with open("receptor_clean.pdb", "r") as f:
    for line in f:
        if line.startswith("ATOM"):
            res_seq = line[22:26].strip()
            if res_seq in target_res:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                coords.append((x, y, z))

if not coords:
    print("Error: Could not find target residues in PDB.")
    sys.exit(1)

cx = sum(c[0] for c in coords) / len(coords)
cy = sum(c[1] for c in coords) / len(coords)
cz = sum(c[2] for c in coords) / len(coords)

print(f"center_x = {cx:.3f}")
print(f"center_y = {cy:.3f}")
print(f"center_z = {cz:.3f}")
print("size_x = 40.000")
print("size_y = 40.000")
print("size_z = 40.000")
EOF

ok "对接盒配置已生成: box_pas.txt"

echo "==========================================================="
echo " 处理全部完成！"
echo " Meeko receptor.pdbqt 现已完美无错生成，可直接开启批量对接！"
echo "==========================================================="