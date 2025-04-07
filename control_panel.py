import numpy as np
import pybullet as p
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QSlider, QGroupBox, QTabWidget, QComboBox, QDoubleSpinBox,
                             QSpinBox, QFormLayout, QLineEdit, QCheckBox, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.robot_id = None
        self.joint_sliders = {}
        self.joint_labels = {}
        self.joint_info = {}
        
        # 设置字体
        self.title_font = QFont()
        self.title_font.setPointSize(10)
        self.title_font.setBold(True)
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 添加标题标签
        title_label = QLabel("控制面板")
        title_label.setFont(self.title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; padding: 5px; background-color: #ecf0f1; border-radius: 4px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页控件
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)  # 使标签页看起来更现代
        main_layout.addWidget(tab_widget)
        
        # 创建关节控制标签页
        joint_control_tab = QWidget()
        tab_widget.addTab(joint_control_tab, QIcon("ico/load_robot.png"), "关节控制")
        
        # 创建仿真参数标签页
        sim_params_tab = QWidget()
        tab_widget.addTab(sim_params_tab, QIcon("ico/start_simulation.png"), "仿真参数")
        
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
        
        # 添加状态信息区域
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel("未加载机器人模型")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        main_layout.addWidget(status_group)
    
    def setup_joint_control_tab(self, tab):
        # 创建滚动区域以支持大量关节
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)  # 移除边框
        
        # 创建滚动区域的内容部件
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        # 创建布局
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 创建关节控制组
        joint_group = QGroupBox("关节控制")
        joint_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout.addWidget(joint_group)
        
        # 关节控制组的布局
        self.joint_layout = QVBoxLayout(joint_group)
        self.joint_layout.setSpacing(8)
        
        # 添加提示标签
        hint_label = QLabel("请加载机器人模型以显示关节控制")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("padding: 20px; color: #7f8c8d; font-style: italic;")
        self.joint_layout.addWidget(hint_label)
        
        # 添加控制按钮组
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        layout.addLayout(buttons_layout)
        
        # 添加重置按钮
        reset_button = QPushButton("重置关节位置")
        reset_button.setIcon(QIcon("ico/reset_simulation.png"))
        reset_button.clicked.connect(self.reset_joint_positions)
        buttons_layout.addWidget(reset_button)
        
        # 添加随机位置按钮
        random_button = QPushButton("随机关节位置")
        random_button.clicked.connect(self.set_random_positions)
        buttons_layout.addWidget(random_button)
        
        # 设置滚动区域为标签页的内容
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)
    
    def setup_sim_params_tab(self, tab):
        # 创建布局
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)
        
        # 创建物理参数组
        physics_group = QGroupBox("物理参数")
        physics_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout.addWidget(physics_group)
        physics_layout = QFormLayout(physics_group)
        physics_layout.setLabelAlignment(Qt.AlignRight)
        physics_layout.setSpacing(10)
        
        # 重力设置
        gravity_layout = QHBoxLayout()
        gravity_layout.setSpacing(5)
        
        gravity_x = QDoubleSpinBox()
        gravity_x.setRange(-100, 100)
        gravity_x.setValue(0)
        gravity_x.setDecimals(2)
        gravity_x.setSingleStep(0.1)
        
        gravity_y = QDoubleSpinBox()
        gravity_y.setRange(-100, 100)
        gravity_y.setValue(0)
        gravity_y.setDecimals(2)
        gravity_y.setSingleStep(0.1)
        
        gravity_z = QDoubleSpinBox()
        gravity_z.setRange(-100, 100)
        gravity_z.setValue(-9.81)
        gravity_z.setDecimals(2)
        gravity_z.setSingleStep(0.1)
        
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
        time_step.setDecimals(4)
        time_step.valueChanged.connect(self.update_time_step)
        physics_layout.addRow("时间步长 (s):", time_step)
        
        # 创建渲染参数组
        render_group = QGroupBox("渲染参数")
        render_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout.addWidget(render_group)
        render_layout = QFormLayout(render_group)
        render_layout.setLabelAlignment(Qt.AlignRight)
        render_layout.setSpacing(10)
        
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
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)
        
        # 创建轨迹类型选择组
        trajectory_group = QGroupBox("轨迹类型")
        trajectory_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout.addWidget(trajectory_group)
        trajectory_layout = QVBoxLayout(trajectory_group)
        trajectory_layout.setSpacing(10)
        
        # 轨迹类型选择下拉框
        trajectory_type = QComboBox()
        trajectory_type.addItems(["关节空间轨迹", "笛卡尔空间轨迹", "圆弧轨迹", "自定义轨迹"])
        trajectory_layout.addWidget(trajectory_type)
        
        # 创建轨迹参数组
        params_group = QGroupBox("轨迹参数")
        params_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout.addWidget(params_group)
        params_layout = QFormLayout(params_group)
        params_layout.setLabelAlignment(Qt.AlignRight)
        params_layout.setSpacing(10)
        
        # 轨迹持续时间
        duration = QDoubleSpinBox()
        duration.setRange(0.1, 60)
        duration.setValue(5)
        duration.setDecimals(1)
        duration.setSingleStep(0.1)
        params_layout.addRow("持续时间 (s):", duration)
        
        # 轨迹点数量
        points = QSpinBox()
        points.setRange(2, 1000)
        points.setValue(100)
        params_layout.addRow("轨迹点数量:", points)
        
        # 创建轨迹控制按钮组
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        layout.addLayout(buttons_layout)
        
        # 生成轨迹按钮
        generate_button = QPushButton("生成轨迹")
        generate_button.setIcon(QIcon("ico/start_simulation.png"))
        buttons_layout.addWidget(generate_button)
        
        # 执行轨迹按钮
        execute_button = QPushButton("执行轨迹")
        buttons_layout.addWidget(execute_button)
        
        # 停止轨迹按钮
        stop_button = QPushButton("停止轨迹")
        stop_button.setIcon(QIcon("ico/stop_simulation.png"))
        buttons_layout.addWidget(stop_button)
        
        # 添加一些空白空间
        layout.addStretch()
    
    def setup_visualization_tab(self, tab):
        # 创建布局
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)
        
        # 创建可视化选项组
        options_group = QGroupBox("可视化选项")
        options_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout.addWidget(options_group)
        options_layout = QVBoxLayout(options_group)
        
        # 添加复选框
        show_axes = QCheckBox("显示坐标轴")
        show_axes.setChecked(True)
        options_layout.addWidget(show_axes)
        
        show_trajectory = QCheckBox("显示轨迹")
        show_trajectory.setChecked(True)
        options_layout.addWidget(show_trajectory)
        
        show_grid = QCheckBox("显示网格")
        show_grid.setChecked(True)
        options_layout.addWidget(show_grid)
        
        # 创建数据图表组
        chart_group = QGroupBox("数据图表")
        chart_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        layout.addWidget(chart_group)
        chart_layout = QVBoxLayout(chart_group)
        
        # 添加图表类型选择
        chart_type = QComboBox()
        chart_type.addItems(["关节位置", "关节速度", "关节力矩", "末端位置"])
        chart_layout.addWidget(chart_type)
        
        # 添加图表占位符
        chart_placeholder = QLabel("选择数据类型显示图表")
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_placeholder.setStyleSheet("background-color: #ecf0f1; padding: 40px; border-radius: 4px; color: #7f8c8d;")
        chart_layout.addWidget(chart_placeholder)
        
        # 添加一些空白空间
        layout.addStretch()
    
    def update_robot_info(self, robot_id):
        self.robot_id = robot_id
        
        # 清空现有的关节控制器
        for i in reversed(range(self.joint_layout.count())): 
            self.joint_layout.itemAt(i).widget().setParent(None)
        
        self.joint_sliders = {}
        self.joint_labels = {}
        self.joint_info = {}
        
        if robot_id is None:
            # 如果没有机器人模型，显示提示信息
            hint_label = QLabel("请加载机器人模型以显示关节控制")
            hint_label.setAlignment(Qt.AlignCenter)
            hint_label.setStyleSheet("padding: 20px; color: #7f8c8d; font-style: italic;")
            self.joint_layout.addWidget(hint_label)
            self.status_label.setText("未加载机器人模型")
            return
        
        # 获取机器人关节信息
        num_joints = p.getNumJoints(robot_id)
        self.status_label.setText(f"已加载机器人模型，关节数量: {num_joints}")
        
        # 为每个关节创建控制器
        for i in range(num_joints):
            joint_info = p.getJointInfo(robot_id, i)
            joint_name = joint_info[1].decode('utf-8')
            joint_type = joint_info[2]
            lower_limit = joint_info[8]
            upper_limit = joint_info[9]
            
            # 只为可移动的关节创建控制器
            if joint_type != p.JOINT_FIXED:
                # 创建关节组
                joint_group = QGroupBox(f"关节 {i}: {joint_name}")
                joint_group.setStyleSheet("QGroupBox { font-weight: bold; }")
                self.joint_layout.addWidget(joint_group)
                
                joint_layout = QVBoxLayout(joint_group)
                
                # 创建滑块和标签
                slider_layout = QHBoxLayout()
                joint_layout.addLayout(slider_layout)
                
                # 如果关节有限制，使用这些限制作为滑块范围
                if lower_limit < upper_limit:
                    min_val = lower_limit
                    max_val = upper_limit
                else:
                    min_val = -3.14
                    max_val = 3.14
                
                # 创建滑块
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(int(min_val * 100))
                slider.setMaximum(int(max_val * 100))
                slider.setValue(0)
                slider.setTickPosition(QSlider.TicksBelow)
                slider.setTickInterval(int((max_val - min_val) * 25))
                slider_layout.addWidget(slider)
                
                # 创建数值显示标签
                value_label = QLabel("0.00")
                value_label.setMinimumWidth(60)
                value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                slider_layout.addWidget(value_label)
                
                # 存储关节信息
                self.joint_sliders[i] = slider
                self.joint_labels[i] = value_label
                self.joint_info[i] = {
                    'name': joint_name,
                    'type': joint_type,
                    'lower_limit': lower_limit,
                    'upper_limit': upper_limit
                }
                
                # 连接滑块的信号
                slider.valueChanged.connect(lambda value, joint=i: self.update_joint_position(joint, value / 100.0))
        
        # 如果没有可移动的关节，显示提示信息
        if not self.joint_sliders:
            hint_label = QLabel("该机器人模型没有可控制的关节")
            hint_label.setAlignment(Qt.AlignCenter)
            hint_label.setStyleSheet("padding: 20px; color: #7f8c8d; font-style: italic;")
            self.joint_layout.addWidget(hint_label)
    
    def update_joint_position(self, joint_id, position):
        if self.robot_id is not None and joint_id in self.joint_sliders:
            p.setJointMotorControl2(self.robot_id, joint_id, p.POSITION_CONTROL, targetPosition=position)
            self.joint_labels[joint_id].setText(f"{position:.2f}")
    
    def update_joint_info(self):
        if self.robot_id is not None:
            for joint_id in self.joint_sliders.keys():
                joint_state = p.getJointState(self.robot_id, joint_id)
                position = joint_state[0]
                self.joint_labels[joint_id].setText(f"{position:.2f}")
                self.joint_sliders[joint_id].blockSignals(True)
                self.joint_sliders[joint_id].setValue(int(position * 100))
                self.joint_sliders[joint_id].blockSignals(False)
    
    def reset_joint_positions(self):
        if self.robot_id is not None:
            for joint_id in self.joint_sliders.keys():
                p.resetJointState(self.robot_id, joint_id, 0)
                self.joint_sliders[joint_id].setValue(0)
    
    def set_random_positions(self):
        if self.robot_id is not None:
            for joint_id in self.joint_sliders.keys():
                info = self.joint_info[joint_id]
                lower = info['lower_limit']
                upper = info['upper_limit']
                
                # 如果关节有限制，在限制范围内随机选择位置
                if lower < upper:
                    position = lower + np.random.random() * (upper - lower)
                else:
                    position = np.random.uniform(-3.14, 3.14)
                
                p.resetJointState(self.robot_id, joint_id, position)
                self.joint_sliders[joint_id].setValue(int(position * 100))
    
    def update_gravity(self, x, y, z):
        p.setGravity(x, y, z)
    
    def update_time_step(self, time_step):
        p.setTimeStep(time_step)
    
    def update_render_fps(self, fps):
        if hasattr(self.parent, 'timer'):
            interval = int(1000 / fps)
            self.parent.timer.setInterval(interval)