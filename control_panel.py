import numpy as np
import pybullet as p
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSlider, QGroupBox, QTabWidget, QComboBox, QDoubleSpinBox,
                             QSpinBox, QFormLayout, QLineEdit, QCheckBox, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.robot_id = None
        self.joint_sliders = {}
        self.joint_labels = {}
        self.joint_info = {}
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标签页控件
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 创建关节控制标签页
        joint_control_tab = QWidget()
        tab_widget.addTab(joint_control_tab, "关节控制")
        
        # 创建仿真参数标签页
        sim_params_tab = QWidget()
        tab_widget.addTab(sim_params_tab, "仿真参数")
        
        # 创建轨迹规划标签页
        trajectory_tab = QWidget()
        tab_widget.addTab(trajectory_tab, "轨迹规划")
        
        # 创建数据可视化标签页
        visualization_tab = QWidget()
        tab_widget.addTab(visualization_tab, "数据可视化")
        
        # 设置关节控制标签页的布局
        self.setup_joint_control_tab(joint_control_tab)
        
        # 设置仿真参数标签页的布局
        self.setup_sim_params_tab(sim_params_tab)
        
        # 设置轨迹规划标签页的布局
        self.setup_trajectory_tab(trajectory_tab)
        
        # 设置数据可视化标签页的布局
        self.setup_visualization_tab(visualization_tab)
    
    def setup_joint_control_tab(self, tab):
        # 创建滚动区域以支持大量关节
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建滚动区域的内容部件
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        # 创建布局
        layout = QVBoxLayout(scroll_content)
        
        # 创建关节控制组
        joint_group = QGroupBox("关节控制")
        layout.addWidget(joint_group)
        
        # 关节控制组的布局
        self.joint_layout = QVBoxLayout(joint_group)
        
        # 添加提示标签
        hint_label = QLabel("请加载机器人模型以显示关节控制")
        hint_label.setAlignment(Qt.AlignCenter)
        self.joint_layout.addWidget(hint_label)
        
        # 添加控制按钮组
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)
        
        # 添加重置按钮
        reset_button = QPushButton("重置关节位置")
        reset_button.clicked.connect(self.reset_joint_positions)
        buttons_layout.addWidget(reset_button)
        
        # 添加随机位置按钮
        random_button = QPushButton("随机关节位置")
        random_button.clicked.connect(self.set_random_positions)
        buttons_layout.addWidget(random_button)
        
        # 设置滚动区域为标签页的内容
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll_area)
    
    def setup_sim_params_tab(self, tab):
        # 创建布局
        layout = QVBoxLayout(tab)
        
        # 创建物理参数组
        physics_group = QGroupBox("物理参数")
        layout.addWidget(physics_group)
        physics_layout = QFormLayout(physics_group)
        
        # 重力设置
        gravity_layout = QHBoxLayout()
        gravity_x = QDoubleSpinBox()
        gravity_x.setRange(-100, 100)
        gravity_x.setValue(0)
        gravity_y = QDoubleSpinBox()
        gravity_y.setRange(-100, 100)
        gravity_y.setValue(0)
        gravity_z = QDoubleSpinBox()
        gravity_z.setRange(-100, 100)
        gravity_z.setValue(-9.81)
        gravity_layout.addWidget(QLabel("X:"))
        gravity_layout.addWidget(gravity_x)
        gravity_layout.addWidget(QLabel("Y:"))
        gravity_layout.addWidget(gravity_y)
        gravity_layout.addWidget(QLabel("Z:"))
        gravity_layout.addWidget(gravity_z)
        physics_layout.addRow("重力 (m/s²):", gravity_layout)
        
        # 连接重力设置的信号
        gravity_x.valueChanged.connect(lambda: self.update_gravity(gravity_x.value(), gravity_y.value(), gravity_z.value()))
        gravity_y.valueChanged.connect(lambda: self.update_gravity(gravity_x.value(), gravity_y.value(), gravity_z.value()))
        gravity_z.valueChanged.connect(lambda: self.update_gravity(gravity_x.value(), gravity_y.value(), gravity_z.value()))
        
        # 时间步长设置
        time_step = QDoubleSpinBox()
        time_step.setRange(1/240, 1/10)
        time_step.setSingleStep(1/240)
        time_step.setValue(1/240)
        time_step.valueChanged.connect(self.update_time_step)
        physics_layout.addRow("时间步长 (s):", time_step)
        
        # 创建渲染参数组
        render_group = QGroupBox("渲染参数")
        layout.addWidget(render_group)
        render_layout = QFormLayout(render_group)
        
        # 渲染频率设置
        fps = QSpinBox()
        fps.setRange(10, 60)
        fps.setValue(20)
        fps.valueChanged.connect(self.update_render_fps)
        render_layout.addRow("渲染帧率 (FPS):", fps)
        
        # 添加一些空白空间
        layout.addStretch()
    
    def setup_trajectory_tab(self, tab):
        # 创建布局
        layout = QVBoxLayout(tab)
        
        # 创建轨迹类型选择组
        trajectory_group = QGroupBox("轨迹类型")
        layout.addWidget(trajectory_group)
        trajectory_layout = QVBoxLayout(trajectory_group)
        
        # 轨迹类型选择下拉框
        trajectory_type = QComboBox()
        trajectory_type.addItems(["关节空间轨迹", "笛卡尔空间轨迹", "圆弧轨迹", "自定义轨迹"])
        trajectory_layout.addWidget(trajectory_type)
        
        # 创建轨迹参数组
        params_group = QGroupBox("轨迹参数")
        layout.addWidget(params_group)
        params_layout = QFormLayout(params_group)
        
        # 轨迹持续时间
        duration = QDoubleSpinBox()
        duration.setRange(0.1, 60)
        duration.setValue(5)
        params_layout.addRow("持续时间 (s):", duration)
        
        # 轨迹点数量
        points = QSpinBox()
        points.setRange(2, 1000)
        points.setValue(100)
        params_layout.addRow("轨迹点数量:", points)
        
        # 创建轨迹控制按钮组
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)
        
        # 生成轨迹按钮
        generate_button = QPushButton("生成轨迹")
        buttons_layout.addWidget(generate_button)
        
        # 执行轨迹按钮
        execute_button = QPushButton("执行轨迹")
        buttons_layout.addWidget(execute_button)
        
        # 停止轨迹按钮
        stop_button = QPushButton("停止轨迹")
        buttons_layout.addWidget(stop_button)
        
        # 添加一些空白空间
        layout.addStretch()
    
    def setup_visualization_tab(self, tab):
        # 创建布局
        layout = QVBoxLayout(tab)
        
        # 创建数据选择组
        data_group = QGroupBox("数据选择")
        layout.addWidget(data_group)
        data_layout = QVBoxLayout(data_group)
        
        # 数据类型选择
        data_type = QComboBox()
        data_type.addItems(["关节位置", "关节速度", "关节力矩", "末端位置", "末端速度"])
        data_layout.addWidget(data_type)
        
        # 创建可视化选项组
        options_group = QGroupBox("可视化选项")
        layout.addWidget(options_group)
        options_layout = QFormLayout(options_group)
        
        # 显示网格
        show_grid = QCheckBox()
        show_grid.setChecked(True)
        options_layout.addRow("显示网格:", show_grid)
        
        # 显示坐标轴
        show_axes = QCheckBox()
        show_axes.setChecked(True)
        options_layout.addRow("显示坐标轴:", show_axes)
        
        # 显示轨迹
        show_trajectory = QCheckBox()
        show_trajectory.setChecked(True)
        options_layout.addRow("显示轨迹:", show_trajectory)
        
        # 添加一些空白空间
        layout.addStretch()
    
    def update_robot_info(self, robot_id):
        # 更新机器人ID
        self.robot_id = robot_id
        
        # 清空现有的关节控制器
        for i in reversed(range(self.joint_layout.count())):
            widget = self.joint_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        self.joint_sliders = {}
        self.joint_labels = {}
        self.joint_info = {}
        
        if robot_id is None:
            # 如果没有机器人，显示提示
            hint_label = QLabel("请加载机器人模型以显示关节控制")
            hint_label.setAlignment(Qt.AlignCenter)
            self.joint_layout.addWidget(hint_label)
            return
        
        # 获取机器人关节信息
        num_joints = p.getNumJoints(robot_id)
        
        for i in range(num_joints):
            joint_info = p.getJointInfo(robot_id, i)
            joint_name = joint_info[1].decode('utf-8')
            joint_type = joint_info[2]
            
            # 只为可移动的关节创建控制器
            if joint_type != p.JOINT_FIXED:
                lower_limit = joint_info[8]
                upper_limit = joint_info[9]
                
                # 如果关节限制无效，设置默认值
                if lower_limit > upper_limit:
                    lower_limit = -3.14
                    upper_limit = 3.14
                
                # 存储关节信息
                self.joint_info[i] = {
                    'name': joint_name,
                    'type': joint_type,
                    'lower_limit': lower_limit,
                    'upper_limit': upper_limit
                }
                
                # 创建关节控制组
                joint_group = QGroupBox(f"关节 {i}: {joint_name}")
                self.joint_layout.addWidget(joint_group)
                joint_layout = QVBoxLayout(joint_group)
                
                # 创建关节位置滑块
                slider_layout = QHBoxLayout()
                joint_layout.addLayout(slider_layout)
                
                # 创建滑块
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(int(lower_limit * 100))
                slider.setMaximum(int(upper_limit * 100))
                slider.setValue(0)
                slider.setTickPosition(QSlider.TicksBelow)
                slider.setTickInterval(int((upper_limit - lower_limit) * 10))
                slider_layout.addWidget(slider)
                
                # 创建数值显示标签
                value_label = QLabel("0.00")
                slider_layout.addWidget(value_label)
                
                # 存储滑块和标签的引用
                self.joint_sliders[i] = slider
                self.joint_labels[i] = value_label
                
                # 连接滑块的信号
                slider.valueChanged.connect(lambda value, joint=i: self.update_joint_position(joint, value/100))
    
    def update_joint_info(self):
        # 更新关节信息显示
        if self.robot_id is None:
            return
        
        for joint_id, info in self.joint_info.items():
            # 获取当前关节状态
            joint_state = p.getJointState(self.robot_id, joint_id)
            current_pos = joint_state[0]
            
            # 更新滑块位置（不触发信号）
            self.joint_sliders[joint_id].blockSignals(True)
            self.joint_sliders[joint_id].setValue(int(current_pos * 100))
            self.joint_sliders[joint_id].blockSignals(False)
            
            # 更新标签
            self.joint_labels[joint_id].setText(f"{current_pos:.2f}")
    
    def update_joint_position(self, joint_id, position):
        # 更新关节位置
        if self.robot_id is not None:
            p.setJointMotorControl2(
                bodyUniqueId=self.robot_id,
                jointIndex=joint_id,
                controlMode=p.POSITION_CONTROL,
                targetPosition=position
            )
            
            # 更新标签
            self.joint_labels[joint_id].setText(f"{position:.2f}")
    
    def reset_joint_positions(self):
        # 重置所有关节位置
        if self.robot_id is not None:
            for joint_id in self.joint_info.keys():
                # 设置为0位置
                p.resetJointState(self.robot_id, joint_id, 0)
                
                # 更新滑块
                self.joint_sliders[joint_id].setValue(0)
    
    def set_random_positions(self):
        # 设置随机关节位置
        if self.robot_id is not None:
            for joint_id, info in self.joint_info.items():
                lower = info['lower_limit']
                upper = info['upper_limit']
                
                # 生成随机位置
                random_pos = np.random.uniform(lower, upper)
                
                # 设置关节位置
                p.resetJointState(self.robot_id, joint_id, random_pos)
                
                # 更新滑块
                self.joint_sliders[joint_id].setValue(int(random_pos * 100))
    
    def update_gravity(self, x, y, z):
        # 更新重力设置
        if self.parent.physics_client is not None:
            p.setGravity(x, y, z)
    
    def update_time_step(self, time_step):
        # 更新仿真时间步长
        if self.parent.physics_client is not None:
            p.setTimeStep(time_step)
    
    def update_render_fps(self, fps):
        # 更新渲染帧率
        if hasattr(self.parent, 'timer'):
            interval = int(1000 / fps)  # 转换为毫秒
            self.parent.timer.setInterval(interval)