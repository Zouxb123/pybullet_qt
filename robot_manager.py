import os
from PyQt5.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class RobotManagerDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("机器人加工管理", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        
        # 创建主部件和布局
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建树形控件
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["机器人加工管理"])
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderHidden(False)
        
        # 添加树形控件到布局
        self.main_layout.addWidget(self.tree_widget)
        
        # 设置主部件
        self.setWidget(self.main_widget)
        
        # 初始化树形结构
        self.init_tree()
        
    def init_tree(self):
        # 获取图标路径
        ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ico")
        
        # 创建根节点
        self.root_item = QTreeWidgetItem(self.tree_widget, ["机器人加工管理"])
        self.root_item.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "load_robot.svg")))
        
        # 创建装配节点
        assembly_item = QTreeWidgetItem(self.root_item, ["装配"])
        assembly_item.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "file.svg")))
        
        # 创建子装配件1节点
        sub_assembly1 = QTreeWidgetItem(assembly_item, ["子装配件1"])
        sub_assembly1.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "file.svg")))
        
        # 添加子装配件1的零件
        part1_1 = QTreeWidgetItem(sub_assembly1, ["part1"])
        part1_1.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "file.svg")))
        
        part1_2 = QTreeWidgetItem(sub_assembly1, ["part2"])
        part1_2.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "file.svg")))
        
        # 创建子装配件2节点
        sub_assembly2 = QTreeWidgetItem(assembly_item, ["子装配件2"])
        sub_assembly2.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "file.svg")))
        
        # 添加子装配件2的零件
        part2_1 = QTreeWidgetItem(sub_assembly2, ["part1"])
        part2_1.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "file.svg")))
        
        part2_2 = QTreeWidgetItem(sub_assembly2, ["part2"])
        part2_2.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "file.svg")))
        
        # 创建坐标系节点
        coordinate_item = QTreeWidgetItem(self.root_item, ["坐标系"])
        coordinate_item.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "view.svg")))
        
        # 添加世界坐标系
        world_coord = QTreeWidgetItem(coordinate_item, ["世界坐标系"])
        world_coord.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "view.svg")))
        
        wcs_item = QTreeWidgetItem(world_coord, ["WCS"])
        wcs_item.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "view.svg")))
        
        # 添加用户坐标系
        user_coord = QTreeWidgetItem(coordinate_item, ["用户坐标系"])
        user_coord.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "view.svg")))
        
        ucs1_item = QTreeWidgetItem(user_coord, ["UCS1"])
        ucs1_item.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "view.svg")))
        
        ucs2_item = QTreeWidgetItem(user_coord, ["UCS2"])
        ucs2_item.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "view.svg")))
        
        # 创建工具节点
        tools_item = QTreeWidgetItem(self.root_item, ["工具"])
        tools_item.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "simulation_parameter.svg")))
        
        # 添加工具子节点
        external_tool = QTreeWidgetItem(tools_item, ["外部工具"])
        external_tool.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "simulation_parameter.svg")))
        
        method_tool = QTreeWidgetItem(tools_item, ["法兰工具"])
        method_tool.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "simulation_parameter.svg")))
        
        # 创建底座节点
        base_item = QTreeWidgetItem(self.root_item, ["底座"])
        base_item.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "simulation.svg")))
        
        # 创建机器人节点
        robot_item = QTreeWidgetItem(self.root_item, ["机器人"])
        robot_item.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "load_robot.svg")))
        
        # 添加机器人子节点
        coord_sys = QTreeWidgetItem(robot_item, ["坐标系"])
        coord_sys.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "view.svg")))
        
        robot_tool = QTreeWidgetItem(robot_item, ["工具"])
        robot_tool.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "simulation_parameter.svg")))
        
        robot_base = QTreeWidgetItem(robot_item, ["底座"])
        robot_base.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "simulation.svg")))
        
        robot_track = QTreeWidgetItem(robot_item, ["轨迹"])
        robot_track.setIcon(0, QIcon(os.path.join(ico_path, "tool_ico", "trajectory_planning.svg")))
        
        # 展开所有节点
        self.tree_widget.expandAll()