import numpy as np
import pybullet as p
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPainter, QLinearGradient, QPen, QBrush

class RobotRenderer(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumSize(QSize(640, 480))
        
        # 相机参数
        self.camera_distance = 2.0
        self.camera_yaw = 45.0
        self.camera_pitch = -30.0
        self.camera_target = [0, 0, 0]
        
        # 鼠标交互参数
        self.last_mouse_pos = None
        self.mouse_mode = None  # 'rotate', 'pan', 'zoom'
        
        # 渲染参数
        self.width = 640
        self.height = 480
        self.view_matrix = None
        self.projection_matrix = None
        
        # 设置边框和背景
        self.setStyleSheet("border: 2px solid #3498db; border-radius: 8px; background-color: #f8f9fa;")
        
        # 初始化渲染器
        self.init_renderer()
    
    def init_renderer(self):
        # 设置PyBullet渲染器
        self.view_matrix = p.computeViewMatrixFromYawPitchRoll(
            cameraTargetPosition=self.camera_target,
            distance=self.camera_distance,
            yaw=self.camera_yaw,
            pitch=self.camera_pitch,
            roll=0,
            upAxisIndex=2
        )
        
        aspect = self.width / self.height
        self.projection_matrix = p.computeProjectionMatrixFOV(
            fov=60,
            aspect=aspect,
            nearVal=0.1,
            farVal=100.0
        )
    
    def minimumSizeHint(self):
        return QSize(640, 480)
    
    def sizeHint(self):
        return QSize(800, 600)
    
    def update(self):
        # 更新渲染
        self.updateGL()
        super().update()
    
    def updateGL(self):
        # 更新OpenGL渲染
        if self.isVisible():
            self.makeCurrent()
            self.paintGL()
            self.doneCurrent()
    
    def initializeGL(self):
        # 初始化OpenGL
        self.setClearColor(QColor(240, 240, 245))  # 使用更柔和的背景色
    
    def resizeGL(self, width, height):
        # 处理窗口大小变化
        self.width = width
        self.height = height
        
        # 更新投影矩阵
        aspect = width / height
        self.projection_matrix = p.computeProjectionMatrixFOV(
            fov=60,
            aspect=aspect,
            nearVal=0.1,
            farVal=100.0
        )
    
    def paintGL(self):
        # 渲染场景
        if not hasattr(self.parent, 'physics_client') or self.parent.physics_client is None:
            return
        
        # 更新视图矩阵
        self.view_matrix = p.computeViewMatrixFromYawPitchRoll(
            cameraTargetPosition=self.camera_target,
            distance=self.camera_distance,
            yaw=self.camera_yaw,
            pitch=self.camera_pitch,
            roll=0,
            upAxisIndex=2
        )
        
        # 获取PyBullet渲染的图像
        img_arr = p.getCameraImage(
            width=self.width,
            height=self.height,
            viewMatrix=self.view_matrix,
            projectionMatrix=self.projection_matrix,
            renderer=p.ER_BULLET_HARDWARE_OPENGL
        )
        
        # 提取RGB图像数据
        rgb = img_arr[2]
        rgb_array = np.reshape(rgb, (self.height, self.width, 4))
        
        # 使用QPainter绘制图像
        painter = QPainter(self)
        
        # 绘制渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height)
        gradient.setColorAt(0, QColor(220, 230, 240))
        gradient.setColorAt(1, QColor(240, 245, 250))
        painter.fillRect(0, 0, self.width, self.height, gradient)
        
        # 绘制图像
        painter.drawImage(0, 0, self.convert_array_to_qimage(rgb_array))
        
        # 绘制边框
        pen = QPen(QColor(52, 152, 219))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width-2, self.height-2)
        
        painter.end()
    
    def convert_array_to_qimage(self, array):
        # 将numpy数组转换为QImage
        from PyQt5.QtGui import QImage
        height, width, channel = array.shape
        bytes_per_line = 4 * width
        return QImage(array.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
    
    def setClearColor(self, color):
        # 设置背景颜色
        self.clear_color = color
    
    def mousePressEvent(self, event):
        # 处理鼠标按下事件
        self.last_mouse_pos = event.pos()
        
        if event.button() == Qt.LeftButton:
            self.mouse_mode = 'rotate'
        elif event.button() == Qt.MiddleButton:
            self.mouse_mode = 'pan'
        elif event.button() == Qt.RightButton:
            self.mouse_mode = 'zoom'
    
    def mouseReleaseEvent(self, event):
        # 处理鼠标释放事件
        self.mouse_mode = None
    
    def mouseMoveEvent(self, event):
        # 处理鼠标移动事件
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return
        
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        self.last_mouse_pos = event.pos()
        
        if self.mouse_mode == 'rotate':
            # 旋转相机
            self.camera_yaw += dx * 0.5
            self.camera_pitch -= dy * 0.5
            self.camera_pitch = max(min(self.camera_pitch, 89.9), -89.9)  # 限制俯仰角
        
        elif self.mouse_mode == 'pan':
            # 平移相机目标点
            forward = np.array([np.cos(np.radians(self.camera_yaw)) * np.cos(np.radians(self.camera_pitch)),
                               np.sin(np.radians(self.camera_yaw)) * np.cos(np.radians(self.camera_pitch)),
                               np.sin(np.radians(self.camera_pitch))])
            right = np.cross(forward, np.array([0, 0, 1]))
            right = right / np.linalg.norm(right)
            up = np.cross(right, forward)
            
            pan_speed = 0.01 * self.camera_distance
            self.camera_target[0] -= right[0] * dx * pan_speed
            self.camera_target[1] -= right[1] * dx * pan_speed
            self.camera_target[2] -= right[2] * dx * pan_speed
            
            self.camera_target[0] += up[0] * dy * pan_speed
            self.camera_target[1] += up[1] * dy * pan_speed
            self.camera_target[2] += up[2] * dy * pan_speed
        
        elif self.mouse_mode == 'zoom':
            # 缩放相机距离
            self.camera_distance -= dy * 0.05
            self.camera_distance = max(0.5, self.camera_distance)  # 限制最小距离
        
        self.update()
    
    def wheelEvent(self, event):
        # 处理鼠标滚轮事件
        delta = event.angleDelta().y()
        self.camera_distance -= delta * 0.01
        self.camera_distance = max(0.5, self.camera_distance)  # 限制最小距离
        self.update()