from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QGroupBox, 
                             QFormLayout, QComboBox, QLineEdit, 
                             QMessageBox, QFileDialog, QCheckBox,
                             QScrollArea, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
import os
import shutil

class ComplexTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.runner = main_window.runner
        self.cwd = None
        
        self.ligand_itp = None
        self.ligand_gro = None
        self.ff_index_edit = None   # will be created in init_ui

        self.init_ui()

    def init_ui(self):
        # === 彻底解决“挤在一起、无法拉伸、显示不开” ===
        # 外层使用 QScrollArea，内部内容使用大间距
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(2, 2, 2, 2)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(22)   # 非常大的组间距，避免拥挤

        scroll.setWidget(content_widget)
        outer_layout.addWidget(scroll)

        # 强制让 tab 内容可以随主窗口拉伸 + 滚动
        self.setMinimumWidth(540)
        content_widget.setMinimumHeight(820)  # 足够内容高度，触发滚动
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )
        content_widget.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )

        # 0. 状态信息
        self.status_label = QLabel("等待配体拓扑...")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)

        # 1. 处理受体蛋白 (pdb2gmx)
        pdb_group = QGroupBox("1. 处理受体蛋白 (pdb2gmx)")
        pdb_layout = QFormLayout()

        file_layout = QHBoxLayout()
        self.pdb_input = QLineEdit()
        self.pdb_input.setPlaceholderText("选择输入的蛋白 .pdb 文件...")
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self.browse_pdb)
        file_layout.addWidget(self.pdb_input)
        file_layout.addWidget(btn_browse)
        pdb_layout.addRow("受体 PDB:", file_layout)

        self.ff_combo = QComboBox()
        self.ff_combo.addItems(["amber03", "amber94", "amber96", "amber99", "amber99sb", "amber99sb-ildn", "charmm27", "oplsaa"])
        self.ff_combo.setCurrentText("oplsaa")
        pdb_layout.addRow("力场 (-ff):", self.ff_combo)

        # === 关键新增：手动力场编号（解决“只有默认力场成功，其余力场报错”）===
        ff_idx_layout = QHBoxLayout()
        self.ff_index_edit = QLineEdit("15")
        self.ff_index_edit.setFixedWidth(55)
        self.ff_index_edit.setToolTip("重要！\n不同GROMACS版本力场编号不同。\n请先在终端运行一次 \"gmx pdb2gmx\" 看交互提示里的编号，\n然后在这里填写（oplsaa 通常是15）。\n切换力场后记得改这个编号！")
        ff_idx_layout.addWidget(self.ff_index_edit)
        ff_idx_layout.addWidget(QLabel("← 力场编号 (手动修改)"))
        ff_idx_layout.addStretch()
        pdb_layout.addRow("力场交互编号:", ff_idx_layout)

        # 切换力场时自动建议编号
        self.ff_combo.currentTextChanged.connect(self._update_ff_suggestion)

        self.water_combo = QComboBox()
        self.water_combo.addItems(["spce", "tip3p", "tip4p", "tip5p"])
        self.water_combo.setCurrentText("spce")
        pdb_layout.addRow("水模型 (-water):", self.water_combo)

        self.ignh_check = QCheckBox("忽略输入文件中的氢原子 (-ignh)")
        self.ignh_check.setChecked(True)
        pdb_layout.addRow("", self.ignh_check)

        btn_run_pdb2gmx = QPushButton("运行 pdb2gmx")
        btn_run_pdb2gmx.clicked.connect(self.run_pdb2gmx)
        pdb_layout.addRow("", btn_run_pdb2gmx)

        pdb_group.setLayout(pdb_layout)
        layout.addWidget(pdb_group)

        # 初始建议一次
        self._update_ff_suggestion(self.ff_combo.currentText())

        # 2. 构建复合物
        build_group = QGroupBox("2. 构建复合物")
        build_layout = QVBoxLayout()
        
        build_info = QLabel("将合并蛋白与配体坐标，并自动更新 topol.top。")
        build_layout.addWidget(build_info)
        
        btn_build_complex = QPushButton("合并生成复合物 (complex.gro & topol.top)")
        btn_build_complex.clicked.connect(self.build_complex)
        build_layout.addWidget(btn_build_complex)
        
        build_group.setLayout(build_layout)
        layout.addWidget(build_group)

        # 新增：配体位置限制（用户要求：能量最小化后需要加配体位置限制）
        posre_group = QGroupBox("生成配体位置限制 (推荐在能量最小化前后执行)")
        posre_layout = QVBoxLayout()

        posre_info = QLabel(
            "为配体生成位置限制文件 (posre_ligand.itp)。\n"
            "后续 NVT/NPT 平衡时可通过 define = -DPOSRES_LIG 启用配体限制，防止配体漂移。"
        )
        posre_info.setStyleSheet("color: #555; font-size: 11px;")
        posre_layout.addWidget(posre_info)

        btn_gen_posre = QPushButton("生成 posre_ligand.itp (genrestr)")
        btn_gen_posre.clicked.connect(self.generate_ligand_posre)
        btn_gen_posre.setStyleSheet("background-color: #006400; color: white; font-weight: bold;")
        posre_layout.addWidget(btn_gen_posre)

        tip_posre = QLabel("提示：将自动使用【配体准备】导入的纯配体 .gro（组 0），无需任何交互窗口。适合大体系（em.gro 不会被使用）。")
        tip_posre.setStyleSheet("color: #006400; font-size: 10px; font-weight: bold;")
        posre_layout.addWidget(tip_posre)

        posre_group.setLayout(posre_layout)
        layout.addWidget(posre_group)

        # 3. 定义盒子与溶剂化 (editconf & solvate)
        box_group = QGroupBox("3. 定义盒子与溶剂化")
        box_layout = QFormLayout()

        self.box_type = QComboBox()
        self.box_type.addItems(["cubic", "triclinic", "dodecahedron", "octahedron"])
        self.box_type.setCurrentText("cubic")
        box_layout.addRow("盒子形状 (-bt):", self.box_type)

        self.box_dist = QLineEdit("1.0")
        box_layout.addRow("边缘距离 (-d, nm):", self.box_dist)

        btn_run_box_solv = QPushButton("运行 editconf & solvate")
        btn_run_box_solv.clicked.connect(self.run_box_solv)
        box_layout.addRow("", btn_run_box_solv)

        box_group.setLayout(box_layout)
        layout.addWidget(box_group)

        # 4. 添加离子 (genion)
        genion_group = QGroupBox("4. 中和系统电荷 (genion)")
        genion_layout = QFormLayout()
        
        genion_info = QLabel("将自动运行 grompp 生成 ions.tpr，并使用 genion 替换水分子添加离子。\n"
                             "⚠️ 大体系（含配体）常因溶剂组号错误失败！请查看控制台 [GMX] Group 列表后输入正确组。")
        genion_info.setWordWrap(True)
        genion_info.setStyleSheet("color:#c00; font-size:11px;")
        genion_layout.addRow(genion_info)

        self.conc_input = QLineEdit("0.15")
        genion_layout.addRow("盐浓度 (-conc, mol/L):", self.conc_input)

        self.pname_input = QLineEdit("NA")
        genion_layout.addRow("阳离子名称 (-pname):", self.pname_input)

        self.nname_input = QLineEdit("CL")
        genion_layout.addRow("阴离子名称 (-nname):", self.nname_input)
        
        self.neutral_check = QCheckBox("中和系统净电荷 (-neutral)")
        self.neutral_check.setChecked(True)
        genion_layout.addRow("", self.neutral_check)

        # === 关键修复：溶剂组可配置 ===
        solvent_layout = QHBoxLayout()
        self.solvent_group_input = QLineEdit("SOL")
        self.solvent_group_input.setPlaceholderText("SOL 或组号 (如 13 / 23)")
        self.solvent_group_input.setFixedWidth(140)
        self.solvent_group_input.setToolTip("大体系常见：\n"
                                            "• SOL (水组名)\n"
                                            "• 13 (配体组，常出现在日志)\n"
                                            "• 23 或更高 (Water_and_ions)\n"
                                            "运行失败后请在全局日志里找 Group 列表，填入对应数字最稳！")
        
        btn_group_help = QPushButton("查看组号建议")
        btn_group_help.setFixedWidth(100)
        btn_group_help.clicked.connect(self.show_genion_group_help)
        
        solvent_layout.addWidget(QLabel("溶剂组 (最重要):"))
        solvent_layout.addWidget(self.solvent_group_input)
        solvent_layout.addWidget(btn_group_help)
        solvent_layout.addStretch()
        genion_layout.addRow("", solvent_layout)

        btn_run_genion = QPushButton("运行 grompp & genion")
        btn_run_genion.setStyleSheet("background-color:#8B0000; color:white; font-weight:bold;")
        btn_run_genion.clicked.connect(self.run_genion)
        genion_layout.addRow("", btn_run_genion)
        
        genion_group.setLayout(genion_layout)
        layout.addWidget(genion_group)

        layout.addStretch()

    def _update_ff_suggestion(self, ff_name):
        """根据选择的力场自动建议力场交互编号（可手动覆盖）。
        请先在终端运行 `gmx pdb2gmx` 查看实际提示中的编号！
        """
        ff_suggestions = {
            "amber03": "1",
            "amber94": "2",
            "amber96": "3",
            "amber99": "4",
            "amber99sb": "5",
            "amber99sb-ildn": "6",
            "charmm27": "8",
            "oplsaa": "15",
        }
        suggested = ff_suggestions.get(ff_name, "15")
        if self.ff_index_edit is not None:
            self.ff_index_edit.setText(suggested)
        if hasattr(self, 'main_window') and self.main_window:
            try:
                self.main_window.log(f"[建议] 力场 {ff_name} 推荐交互编号: {suggested} （请用终端 gmx pdb2gmx 确认真实编号！）")
            except Exception:
                pass

    def update_ligand_info(self, cwd, itp_path, gro_path):
        self.cwd = cwd
        self.ligand_itp = os.path.basename(itp_path)
        self.ligand_gro = os.path.basename(gro_path)
        self.status_label.setText(f"✅ 已加载配体: {self.ligand_itp}, {self.ligand_gro} (工作目录: {self.cwd})")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")

    def browse_pdb(self):
        if not self.cwd:
            QMessageBox.warning(self, "警告", "请先在第一步【配体准备】中设置工作目录并导入配体！")
            return
        f, _ = QFileDialog.getOpenFileName(self, "选择蛋白 PDB 文件", self.cwd, "PDB Files (*.pdb)")
        if f:
            target_path = os.path.join(self.cwd, os.path.basename(f))
            if os.path.abspath(f) != os.path.abspath(target_path):
                shutil.copy(f, target_path)
            self.pdb_input.setText(os.path.basename(f))

    def set_buttons_enabled(self, enabled):
        for child in self.findChildren(QPushButton):
            child.setEnabled(enabled)

    def run_pdb2gmx(self):
        pdb_filename = self.pdb_input.text()
        if not pdb_filename or not self.cwd:
            QMessageBox.warning(self, "警告", "请选择蛋白文件或确保已设置工作目录。\n\n请先去【配体准备】标签页导入配体并设置工作目录。")
            return

        # 检查文件是否存在（与 Solution Simulator 一致的清晰错误）
        full_path = os.path.join(self.cwd, pdb_filename)
        if not os.path.exists(full_path):
            QMessageBox.warning(self, "警告", f"在工作目录中未找到文件: {pdb_filename}\n\n完整路径: {full_path}\n\n请确保：\n1. 文件已复制到工作目录\n2. 文件名正确（包括扩展名）\n3. 已通过【配体准备】正确设置工作目录")
            return

        ff = self.ff_combo.currentText()
        water = self.water_combo.currentText()
        ignh = self.ignh_check.isChecked()

        # ★★★ 关键修复（和 Solution Simulator 完全一致）★★★
        # 绝对不要传 -ff，否则会出现 "Force field 'oplsaa' occurs in 2 places"
        args = ["pdb2gmx", "-f", pdb_filename, "-o", "protein.gro", "-p", "topol.top", "-water", water]
        if ignh:
            args.append("-ignh")

        # 通过 stdin 自动选择力场
        # 优先使用用户在界面上手动输入的编号（解决“只有默认力场成功，其余力场报错”）
        try:
            manual_idx = self.ff_index_edit.text().strip()
            if manual_idx and manual_idx.isdigit():
                selection = manual_idx + "\n"
            else:
                # fallback 到常见映射
                ff_map = {
                    "amber03": "1", "amber94": "2", "amber96": "3", "amber99": "4",
                    "amber99sb": "5", "amber99sb-ildn": "6", "charmm27": "8",
                    "oplsaa": "15",
                }
                selection = ff_map.get(ff, "15") + "\n"
        except Exception:
            selection = "15\n"

        print(f"[Complex] pdb2gmx args without -ff, stdin={repr(selection)}")
        self.main_window.log(f">>> 使用力场编号 stdin: {selection.strip()} (力场: {ff})")

        self.worker_pdb2gmx = self.runner.create_worker(args, cwd=self.cwd, input_text=selection)
        self.worker_pdb2gmx.output_signal.connect(self.main_window.log, Qt.ConnectionType.QueuedConnection)
        self.worker_pdb2gmx.finished_signal.connect(self.on_pdb2gmx_finished, Qt.ConnectionType.QueuedConnection)
        
        self.set_buttons_enabled(False)
        self.worker_pdb2gmx.start()

    def on_pdb2gmx_finished(self, success, message):
        self.set_buttons_enabled(True)
        if success:
            QMessageBox.information(self, "成功", "pdb2gmx 运行成功，已生成 protein.gro 和 topol.top")
        else:
            QMessageBox.critical(self, "错误", f"pdb2gmx 失败:\n{message}")

    def get_ligand_molecule_name(self, itp_path):
        """解析 itp 文件获取分子名称"""
        try:
            with open(itp_path, 'r') as f:
                lines = f.readlines()
            
            in_moleculetype = False
            for line in lines:
                line = line.strip()
                if line.startswith(';') or not line:
                    continue
                if line.startswith('[') and 'moleculetype' in line:
                    in_moleculetype = True
                    continue
                if in_moleculetype and not line.startswith('['):
                    parts = line.split()
                    if parts:
                        return parts[0]
                if in_moleculetype and line.startswith('['):
                    in_moleculetype = False
        except Exception as e:
            print(f"Error parsing ITP: {e}")
        return "UNL" # default fallback

    def build_complex(self):
        if not self.cwd or not self.ligand_gro or not self.ligand_itp:
            QMessageBox.warning(self, "警告", "配体信息缺失！")
            return
            
        prot_gro = os.path.join(self.cwd, "protein.gro")
        lig_gro = os.path.join(self.cwd, self.ligand_gro)
        comp_gro = os.path.join(self.cwd, "complex.gro")
        top_file = os.path.join(self.cwd, "topol.top")
        lig_itp_path = os.path.join(self.cwd, self.ligand_itp)
        
        if not os.path.exists(prot_gro) or not os.path.exists(top_file):
            QMessageBox.warning(self, "警告", "未找到 protein.gro 或 topol.top，请先运行 pdb2gmx！")
            return
            
        try:
            # 1. 合并 GRO 文件
            with open(prot_gro, 'r') as f:
                prot_lines = f.readlines()
            with open(lig_gro, 'r') as f:
                lig_lines = f.readlines()
                
            prot_atoms = int(prot_lines[1].strip())
            lig_atoms = int(lig_lines[1].strip())
            total_atoms = prot_atoms + lig_atoms
            
            with open(comp_gro, 'w') as f:
                f.write("Complex: Protein + Ligand\n")
                f.write(f"{total_atoms:5d}\n")
                # 写入蛋白原子 (去掉前两行和最后一行 box)
                f.writelines(prot_lines[2:-1])
                # 写入配体原子 (去掉前两行和最后一行 box)
                f.writelines(lig_lines[2:-1])
                # 写入 box 向量 (使用蛋白的)
                f.write(prot_lines[-1])
                
            # 2. 更新 TOP 文件
            with open(top_file, 'r') as f:
                top_lines = f.readlines()
                
            # 寻找插入 #include "ligand.itp" 的位置 (通常在力场 include 之后)
            insert_itp_idx = -1
            for i, line in enumerate(top_lines):
                if '#include' in line and ('forcefield.itp' in line or 'ffnonbonded.itp' in line):
                    insert_itp_idx = i
            
            lig_name = self.get_ligand_molecule_name(lig_itp_path)
            include_line = f'#include "{self.ligand_itp}"'
            ligand_include_exists = any(include_line in line for line in top_lines)
            
            new_top_lines = []
            itp_inserted = False
            for i, line in enumerate(top_lines):
                new_top_lines.append(line)
                # 如果找到了 forcefield include，就在它后面插入
                if insert_itp_idx != -1 and i == insert_itp_idx and not itp_inserted and not ligand_include_exists:
                    new_top_lines.append(f'\n; Include ligand topology\n')
                    new_top_lines.append(f'#include "{self.ligand_itp}"\n\n')
                    itp_inserted = True
                # 如果没找到，就在 [ system ] 之前插入
                elif insert_itp_idx == -1 and '[ system ]' in line and not itp_inserted and not ligand_include_exists:
                    new_top_lines.insert(-1, f'; Include ligand topology\n#include "{self.ligand_itp}"\n\n')
                    itp_inserted = True
                    
            # 在 [ molecules ] 段中按坐标顺序插入配体分子数量
            # complex.gro / complex_solv.gro 的原子顺序是 Protein -> Ligand -> Solvent/Ions
            # 因此 topol.top 中的 [ molecules ] 也必须保持相同顺序，否则 genion 会报 SOL 组不连续
            has_ligand_in_mols = False
            in_molecules_sec = False
            molecules_header_idx = -1
            for i, line in enumerate(new_top_lines):
                if '[ molecules ]' in line:
                    in_molecules_sec = True
                    molecules_header_idx = i
                if in_molecules_sec and lig_name in line:
                    has_ligand_in_mols = True
                    
            if not has_ligand_in_mols:
                insert_mol_idx = len(new_top_lines)
                if molecules_header_idx != -1:
                    insert_mol_idx = molecules_header_idx + 1
                    # 跳过 [ molecules ] 标题后的注释/空行/已有蛋白条目，
                    # 并在第一个溶剂或离子条目前插入配体
                    for i in range(molecules_header_idx + 1, len(new_top_lines)):
                        stripped = new_top_lines[i].strip()
                        if not stripped or stripped.startswith(';'):
                            continue

                        parts = stripped.split()
                        mol_name = parts[0] if parts else ""
                        if mol_name in {"SOL", "WAT", "HOH", "NA", "CL", "K", "CA", "MG"}:
                            insert_mol_idx = i
                            break
                        insert_mol_idx = i + 1

                new_top_lines.insert(insert_mol_idx, f'{lig_name:<15} 1\n')
                
            with open(top_file, 'w') as f:
                f.writelines(new_top_lines)
                
            QMessageBox.information(self, "成功", f"复合物构建成功！\n已生成 complex.gro\n已更新 topol.top (添加了 {lig_name})")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"构建复合物时出错: {str(e)}")

    def run_box_solv(self):
        if not self.cwd: return
        bt = self.box_type.currentText()
        d = self.box_dist.text()
        
        # Editconf
        args_editconf = ["editconf", "-f", "complex.gro", "-o", "complex_newbox.gro", "-c", "-d", d, "-bt", bt]
        self.main_window.log(f"\n>>> 运行 editconf: {' '.join(args_editconf)}")
        
        self.worker_editconf = self.runner.create_worker(args_editconf, cwd=self.cwd)
        self.worker_editconf.output_signal.connect(self.main_window.log)
        self.worker_editconf.finished_signal.connect(self.on_editconf_finished)
        
        self.set_buttons_enabled(False)
        self.worker_editconf.start()

    def on_editconf_finished(self, success, message):
        if not success:
            self.set_buttons_enabled(True)
            QMessageBox.critical(self, "错误", f"editconf 失败:\n{message}")
            return
            
        # Solvate
        args_solvate = ["solvate", "-cp", "complex_newbox.gro", "-cs", "spc216.gro", "-o", "complex_solv.gro", "-p", "topol.top"]
        self.main_window.log(f"\n>>> 运行 solvate: {' '.join(args_solvate)}")
        
        self.worker_solvate = self.runner.create_worker(args_solvate, cwd=self.cwd)
        self.worker_solvate.output_signal.connect(self.main_window.log)
        self.worker_solvate.finished_signal.connect(self.on_solvate_finished)
        self.worker_solvate.start()

    def on_solvate_finished(self, success, message):
        self.set_buttons_enabled(True)
        if success:
            QMessageBox.information(self, "成功", "已完成定义盒子与溶剂化，生成 complex_solv.gro")
        else:
            QMessageBox.critical(self, "错误", f"solvate 失败:\n{message}")

    def run_genion(self):
        if not self.cwd: return
        
        # 先运行 grompp 生成 ions.tpr
        ions_mdp_path = os.path.join(self.cwd, "ions.mdp")
        with open(ions_mdp_path, "w") as f:
            f.write("; ions.mdp - used as input into grompp to generate ions.tpr\n")
            f.write("integrator  = steep\n")
            f.write("emtol       = 1000.0\n")
            f.write("emstep      = 0.01\n")
            f.write("nsteps      = 50000\n")
            f.write("nstlist     = 1\n")
            f.write("cutoff-scheme = Verlet\n")
            f.write("ns_type     = grid\n")
            f.write("coulombtype = PME\n")
            f.write("rcoulomb    = 1.0\n")
            f.write("rvdw        = 1.0\n")
            f.write("pbc         = xyz\n")

        args_grompp = ["grompp", "-f", "ions.mdp", "-c", "complex_solv.gro", "-p", "topol.top", "-o", "ions.tpr", "-maxwarn", "2"]
        
        self.main_window.log(f"\n>>> 运行 grompp (为 genion 准备): {' '.join(args_grompp)}")
        self.worker_grompp = self.runner.create_worker(args_grompp, cwd=self.cwd)
        self.worker_grompp.output_signal.connect(self.main_window.log)
        self.worker_grompp.finished_signal.connect(self.on_genion_grompp_finished)
        
        self.set_buttons_enabled(False)
        self.worker_grompp.start()

    def on_genion_grompp_finished(self, success, message):
        if not success:
            self.set_buttons_enabled(True)
            QMessageBox.critical(self, "错误", f"grompp (ions) 失败:\n{message}")
            return
            
        # 运行 genion
        conc = self.conc_input.text()
        pname = self.pname_input.text()
        nname = self.nname_input.text()
        
        args_genion = ["genion", "-s", "ions.tpr", "-o", "complex_solv_ions.gro", "-p", "topol.top", "-pname", pname, "-nname", nname]
        if self.neutral_check.isChecked():
            args_genion.append("-neutral")
        if conc:
            args_genion.extend(["-conc", conc])
            
        self.main_window.log(f"\n>>> 运行 genion: {' '.join(args_genion)}")
        
        # === 关键修复：使用用户指定的溶剂组 ===
        solvent = self.solvent_group_input.text().strip() or "SOL"
        # 确保以换行结束
        if not solvent.endswith('\n'):
            solvent += '\n'
        
        self.main_window.log(f">>> 使用溶剂组输入: {repr(solvent.strip())} （推荐大体系用组号如 23）")
        
        self.worker_genion = self.runner.create_worker(args_genion, cwd=self.cwd, input_text=solvent)
        self.worker_genion.output_signal.connect(self.main_window.log)
        self.worker_genion.finished_signal.connect(self.on_genion_finished)
        self.worker_genion.start()

    def on_genion_finished(self, success, message):
        self.set_buttons_enabled(True)
        if success:
            QMessageBox.information(self, "成功", "离子添加成功，生成 complex_solv_ions.gro！\n复合物系统准备完毕。")
        else:
            QMessageBox.critical(self, "错误", f"genion 失败:\n{message}")

    def show_genion_group_help(self):
        """帮助用户理解大体系 genion 组号问题"""
        help_text = """大体系（含配体）genion 失败常见原因及解决：

1. 常见问题：
   • 配体加入后，溶剂组号发生了变化（不再是 13）。
   • 你日志中常看到：
     Group    13 (            UNK) ...
     Group    23 ( Water_and_ions) ...

2. 推荐做法：
   • 运行 genion 之前，先看全局日志里的 Group 列表。
   • 填入 **数字组号**（例如 23）最可靠。
   • 或者输入 "SOL" （如果 gmx 识别名称）。

3. 快速查看组号方法：
   在终端手动运行：
   gmx make_ndx -f complex_solv.gro -o /tmp/ndxtest.ndx
   （输入 q 退出后看输出）

4. 当前输入框支持：
   • SOL
   • 13
   • 23
   • 任何数字组号

如果还是失败，请复制 genion 失败时的完整 [GMX] 输出发给我。"""
        QMessageBox.information(self, "genion 溶剂组选择帮助", help_text)

    # ========== 严格版：配体位置限制（永远使用纯配体小文件 + 自动组0，无阻塞） ==========
    def generate_ligand_posre(self):
        """
        生成 posre_ligand.itp —— 严格使用配体准备阶段导入的**纯配体 .gro**

        核心原则（解决大体系 genrestr 阻塞问题）：
        - 永远只使用 self.ligand_gro（来自【配体准备】导入的原始小文件，如 UNK.gro）。
        - 纯配体文件只有 1-2 个组，genrestr 立即打印并退出。
        - 自动发送 "0\n" （组 0 几乎总是配体）。
        - **绝不** fallback 到 em.gro / complex.gro 等大文件（那是卡死的根源）。
        - 如果没有纯配体文件 → 给出清晰警告，要求用户重新导入。
        """
        self.main_window.log("\n>>> [posre] 用户点击了生成 posre_ligand.itp")

        if not self.cwd:
            QMessageBox.warning(self, "警告", "请先设置工作目录（通过【配体准备】导入配体时会自动设置）")
            return

        if not getattr(self, 'ligand_gro', None):
            QMessageBox.warning(
                self, "警告",
                "未检测到纯配体结构文件！\n\n"
                "请先切换到【1. 配体准备】标签页，\n"
                "同时选择 .itp 和 .gro/.pdb 文件后点击「确认导入」\n"
                "（支持任意原始文件名，如 ligand.gro / UNK.gro 等）。\n\n"
                "导入成功后上方会显示绿色“✅ 已加载配体”，\n"
                "然后再回到此页点击绿色按钮。"
            )
            return

        p = os.path.join(self.cwd, self.ligand_gro)
        if not os.path.exists(p):
            QMessageBox.warning(
                self, "警告",
                f"在工作目录中未找到文件: {self.ligand_gro}\n\n"
                f"完整路径: {p}\n\n"
                "解决办法：\n"
                "1. 返回【配体准备】重新导入配体 .gro 文件\n"
                "2. 确认工作目录正确（状态栏显示的目录）\n"
                "3. 确认文件没有被移动或删除"
            )
            return

        ligand_struct = self.ligand_gro
        self.main_window.log(f"\n>>> [posre] 强制使用纯配体文件: {ligand_struct} (cwd={self.cwd})")
        self.main_window.log(">>> （来自配体准备阶段，文件很小，只有1-2个组，不会阻塞）")

        args = ["genrestr", "-f", ligand_struct, "-o", "posre_ligand.itp", "-fc", "1000", "1000", "1000"]
        input_text = "0\n"

        self.main_window.log(f"\n>>> 正在运行: gmx {' '.join(args)}")
        self.main_window.log(">>> 自动发送组号: 0 （纯配体组0）")

        self.worker_posre = self.runner.create_worker(args, cwd=self.cwd, input_text=input_text)
        self.worker_posre.output_signal.connect(self.main_window.log)
        self.worker_posre.finished_signal.connect(self.on_posre_finished)

        self.set_buttons_enabled(False)
        self.worker_posre.start()

    def on_posre_finished(self, success, message):
        self.set_buttons_enabled(True)
        if success:
            posre_file = os.path.join(self.cwd, "posre_ligand.itp")
            if os.path.exists(posre_file):
                self.main_window.log(f"✅✅✅ 配体位置限制文件已生成: {posre_file}")
                QMessageBox.information(
                    self, "成功",
                    "配体位置限制文件 posre_ligand.itp 已生成！\n\n"
                    "后续使用方法（NVT / NPT 平衡时）：\n"
                    "1. 在 mdp 文件中添加：\n"
                    "   define                  = -DPOSRES_LIG\n\n"
                    "2. 在 topol.top 合适位置（通常在 [ moleculetype ] 段之后，或 #include 配体 itp 附近）添加：\n"
                    "#ifdef POSRES_LIG\n"
                    '#include "posre_ligand.itp"\n'
                    "#endif\n\n"
                    "注意：请根据需要调整力常数（-fc 参数），并确认 topol.top 中正确包含了配体 itp。"
                )
            else:
                self.main_window.log("genrestr 运行成功，但未找到 posre_ligand.itp，请检查输出。")
        else:
            QMessageBox.critical(self, "错误", f"生成配体位置限制失败:\n{message}")
            self.main_window.log(f"❌ posre 生成失败: {message}")
