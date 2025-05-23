import sys
import os
import time
import numpy as np
import pybullet as p
import pybullet_data
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSlider, QGroupBox, QComboBox, QAction,
                             QMenuBar, QToolBar, QDockWidget, QTabWidget, QSplitter, QFileDialog,
                             QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from robot_renderer import RobotRenderer
from control_panel import ControlPanel
from robot_manager import RobotManagerDock

class RobotSimulationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("西交机器人运动仿真软件")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置应用程序图标
        self.setWindowIcon(QIcon("ico/XJTU.ico"))
        
        # 初始化PyBullet
        self.physics_client = None
        self.robot_id = None
        self.init_pybullet()
        
        # 创建UI组件
        self.init_ui()
        
        # 设置定时器用于更新仿真
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(50)  # 20 FPS
        
    def init_pybullet(self):
        # 初始化PyBullet物理引擎
        self.physics_client = p.connect(p.DIRECT)  # 无GUI模式，渲染将通过PyQt完成
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.loadURDF("plane.urdf")
        
    def init_ui(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建3D渲染区域
        self.renderer = RobotRenderer(self)
        splitter.addWidget(self.renderer)
        
        # 创建控制面板
        self.control_panel = ControlPanel(self)
        splitter.addWidget(self.control_panel)
        
        # 设置分割比例
        splitter.setSizes([800, 400])
        
        # 创建机器人加工管理DockWidget
        self.robot_manager_dock = RobotManagerDock(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.robot_manager_dock)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_tool_bar()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
        
    def create_menu_bar(self):
        # 创建菜单栏
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        load_robot_action = QAction(QIcon("ico/tool_ico/load_robot.svg"), "加载机器人模型", self)
        load_robot_action.triggered.connect(self.load_robot)
        file_menu.addAction(load_robot_action)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 仿真菜单
        sim_menu = menu_bar.addMenu("仿真")
        
        start_sim_action = QAction(QIcon("ico/tool_ico/start_simulation.svg"), "开始仿真", self)
        start_sim_action.triggered.connect(self.start_simulation)
        sim_menu.addAction(start_sim_action)
        
        stop_sim_action = QAction(QIcon("ico/tool_ico/stop_simulation.svg"), "停止仿真", self)
        stop_sim_action.triggered.connect(self.stop_simulation)
        sim_menu.addAction(stop_sim_action)
        
        reset_sim_action = QAction(QIcon("ico/tool_ico/reset_simulation.svg"), "重置仿真", self)
        reset_sim_action.triggered.connect(self.reset_simulation)
        sim_menu.addAction(reset_sim_action)
        
        # 视图菜单
        view_menu = menu_bar.addMenu("视图")
        view_menu.setIcon(QIcon("ico/tool_ico/view.svg"))
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        about_action = QAction(QIcon("ico/tool_ico/help.svg"), "关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        # 创建工具栏
        tool_bar = QToolBar("工具栏", self)
        self.addToolBar(tool_bar)
        
        # 添加工具栏按钮
        load_button = QPushButton("加载机器人")
        load_button.setIcon(QIcon("ico/tool_ico/load_robot.svg"))
        load_button.clicked.connect(self.load_robot)
        tool_bar.addWidget(load_button)
        
        start_button = QPushButton("开始仿真")
        start_button.setIcon(QIcon("ico/tool_ico/start_simulation.svg"))
        start_button.clicked.connect(self.start_simulation)
        tool_bar.addWidget(start_button)
        
        stop_button = QPushButton("停止仿真")
        stop_button.setIcon(QIcon("ico/tool_ico/stop_simulation.svg"))
        stop_button.clicked.connect(self.stop_simulation)
        tool_bar.addWidget(stop_button)
        
        reset_button = QPushButton("重置仿真")
        reset_button.setIcon(QIcon("ico/tool_ico/reset_simulation.svg"))
        reset_button.clicked.connect(self.reset_simulation)
        tool_bar.addWidget(reset_button)
        
    def load_robot(self):
        # 打开文件对话框选择URDF文件
        file_path, _ = QFileDialog.getOpenFileName(self, "选择机器人URDF文件", "", "URDF文件 (*.urdf)")
        
        if file_path:
            # 如果已有机器人模型，先移除
            if self.robot_id is not None:
                p.removeBody(self.robot_id)
            
            # 加载新的机器人模型
            self.robot_id = p.loadURDF(file_path)
            
            # 更新控制面板
            self.control_panel.update_robot_info(self.robot_id)
            
            self.statusBar.showMessage(f"已加载机器人模型: {os.path.basename(file_path)}")
    
    def start_simulation(self):
        if not self.timer.isActive():
            self.timer.start(50)
            self.statusBar.showMessage("仿真运行中")
    
    def stop_simulation(self):
        if self.timer.isActive():
            self.timer.stop()
            self.statusBar.showMessage("仿真已暂停")
    
    def reset_simulation(self):
        # 重置仿真
        p.resetSimulation()
        p.setGravity(0, 0, -9.81)
        p.loadURDF("plane.urdf")
        
        # 重新加载机器人模型
        self.robot_id = None
        self.control_panel.update_robot_info(None)
        
        self.statusBar.showMessage("仿真已重置")
    
    def update_simulation(self):
        # 更新物理仿真
        p.stepSimulation()
        
        # 更新渲染
        self.renderer.update()
        
        # 更新控制面板信息
        if self.robot_id is not None:
            self.control_panel.update_joint_info()
    
    def show_about(self):
        QMessageBox.about(self, "关于", "机器人运动仿真软件 v1.0\n基于PyQt5和PyBullet开发")
    
    def closeEvent(self, event):
        # 关闭PyBullet连接
        if self.physics_client is not None:
            p.disconnect()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # 加载样式表
    with open("style.qss", "r", encoding="utf-8") as f:
        style = f.read()
        app.setStyleSheet(style)
    
    window = RobotSimulationApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()