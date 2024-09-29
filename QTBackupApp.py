import os
import stat
import shutil
import time
from config.config import get_val, get_config
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QMessageBox, QHeaderView, QTableWidget, QComboBox, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
import logging
import sys

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为INFO
    format='%(asctime)s %(levelname)s %(message)s',  # 日志格式
    handlers=[
        logging.FileHandler('sl.log', mode='a', encoding='utf-8'),  # 追加模式写入文件，解决中文乱码
        logging.StreamHandler(sys.stdout)  # 输出到控制台
    ]
)

def create_dir(backup_path):
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
        # 设置文件夹为可读写
        os.chmod(backup_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    else:
        os.chmod(backup_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


class QTBackupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.config = get_config()

        if self.config is None:
            logging.error("请检查配置")
            raise Exception("请检查配置")

        self.games_box_config = get_val(self.config, "games")
        self.win_config = get_val(self.config, "games")
        self.windows_config = get_val(self.config, "windows")
        self.app_config = get_val(self.config, "app")

        self.current_game = None
        self.current_game_key = None
        self.current_game_name = None

        # 选择游戏
        self.select_game_label = None
        self.games_box = None

        # 源路径
        self.label_source = None
        self.entry_source = None
        self.button_source = None
        self.button_open_source = None

        # 存档名
        self.archive_name_label = None
        self.entry_archive_name = None

        # 存档列表
        self.archive_table_label = None
        self.archive_table = None

        # 源路径
        self.source_dir = None

        # 备份路径
        self.backup_dir = None

        self.button_start_backup = None
        self.button_reset = None
        self.button_refresh = None

        # 最新存档
        self.new_archive_label = None
        self.new_archive_val = None

        # 存档表
        self.archive_table_label = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SL工具')

        w = get_val(self.windows_config, "w")
        h = get_val(self.windows_config, "h")
        self.setFixedSize(w, h)  # 如果你想让窗口固定大小，不允许用户调整大小

        # 创建布局
        layout = QVBoxLayout()
        # 创建标签
        self.select_game_label = QLabel("选择游戏:")
        # 创建下拉框
        self.games_box = QComboBox(self)

        for key in self.games_box_config:
            item = get_val(self.games_box_config, key)
            self.games_box.addItem(item.get("name"), userData=key)

        self.games_box.currentIndexChanged.connect(self.on_game_changed)

        # 源文件目录输入行
        self.label_source = QLabel('源存档目录:')
        self.entry_source = QLineEdit(self)
        self.button_source = QPushButton('重新选择', self)
        self.button_source.clicked.connect(self.browse_source_dir)

        self.button_open_source = QPushButton('打开目录', self)
        self.button_open_source.clicked.connect(self.open_source_directory)

        self.archive_name_label = QLabel('存档名:')
        self.entry_archive_name = QLineEdit(self)
        self.entry_archive_name.setPlaceholderText('请输入存档名或留空自动生成')

        # 开始备份按钮
        self.button_start_backup = QPushButton('存档', self)
        self.button_start_backup.clicked.connect(self.start_backup)

        # 回档按钮
        self.button_reset = QPushButton('最新回档', self)
        self.button_reset.clicked.connect(self.restore_backup)

        # 刷新
        self.button_refresh = QPushButton('刷新', self)
        self.button_refresh.clicked.connect(self.refresh_table)

        self.new_archive_label = QLabel('最新存档:')
        self.new_archive_val = QLabel(self)

        self.archive_table_label = QLabel('存档列表:')
        self.archive_table_label.setAlignment(Qt.AlignLeft)

        # 创建一个 QTableWidget 来显示存档文件和操作按钮
        self.archive_table = QTableWidget(self)
        columns = ["存档名", "存档时间", "操作"]
        self.archive_table.setColumnCount(len(columns))
        self.archive_table.setHorizontalHeaderLabels(columns)

        # 设置列宽自适应窗口宽度
        self.archive_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置行高自适应窗口高度
        # self.archive_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 选择游戏控件
        games_layout = QHBoxLayout()
        games_layout.setAlignment(Qt.AlignLeft)
        # 将标签和下拉框添加到水平布局
        games_layout.addWidget(self.select_game_label)
        games_layout.addWidget(self.games_box)

        # 源路径控件
        source_layout = QHBoxLayout()
        source_layout.addWidget(self.label_source)
        source_layout.addWidget(self.entry_source)
        source_layout.addWidget(self.button_source)
        source_layout.addWidget(self.button_open_source)

        # 存档列表
        archive_name_layout = QHBoxLayout()
        archive_name_layout.addWidget(self.archive_name_label)
        archive_name_layout.addWidget(self.entry_archive_name)

        # 按钮
        but_layout = QHBoxLayout()
        but_layout.addWidget(self.button_start_backup)
        but_layout.addWidget(self.button_reset)
        but_layout.addWidget(self.button_refresh)

        # 最新存档
        new_archive_layout = QHBoxLayout()
        new_archive_layout.setAlignment(Qt.AlignLeft)
        new_archive_layout.addWidget(self.new_archive_label)
        new_archive_layout.addWidget(self.new_archive_val)

        # 存档列表
        archive_list_layout = QHBoxLayout()
        archive_list_layout.addWidget(self.archive_table_label)
        archive_list_layout.addWidget(self.archive_table)

        # 添加到总控件
        layout.addLayout(games_layout)
        layout.addLayout(source_layout)
        layout.addLayout(archive_name_layout)
        layout.addLayout(but_layout)
        layout.addLayout(new_archive_layout)
        layout.addLayout(archive_list_layout)
        # 设置布局
        self.setLayout(layout)
        # 初始化值
        self.init_val()

    def init_val(self):
        self.switch_game(self.games_box.itemData(0))

        # 创建一个定时器
        timer = QTimer(self)
        # 设定每 1000 毫秒
        timer.setInterval(get_val(self.app_config, "table_refresh"))
        # 连接定时器的 timeout 信号到要执行的函数
        timer.timeout.connect(self.refresh_table)
        timer.start()

    def start_backup_at_startup(self):
        """程序启动时备份源目录为压缩包"""
        if self.source_dir and os.path.exists(self.source_dir):
            # 组装当前存档目录
            backup_path = os.path.join(self.backup_dir,self.current_game_key, f"{self.current_game_name}默认备份")
            if os.path.exists(f"{backup_path}.zip"):
                logging.warning(f"无须再次备份: {backup_path}")
                return
            try:
                # 将源目录压缩为 ZIP 包
                zip_file_path = shutil.make_archive(backup_path, 'zip', self.source_dir)
                logging.info(f"启动备份完成，压缩包路径：{zip_file_path}")
            except Exception as e:
                logging.info(f"压缩备份时出错: {str(e)}")
        else:
            logging.info("源目录不存在，无法备份！")

    def refresh_table(self):
        """读取备份目录下的文件并添加到表格中"""
        current_backup_dir = os.path.join(self.backup_dir, self.current_game_key)

        if os.path.exists(current_backup_dir):
            # 获取目录下的一级文件名
            # dirs = os.listdir(current_backup_dir)
            zip_files = [f for f in os.listdir(current_backup_dir) if f.endswith('.zip')]
            # 清空表格，重置表格行数为 0
            self.archive_table.setRowCount(0)

            if len(zip_files) > 0:
                # 遍历文件并添加到表格中
                for row, zip_name in enumerate(zip_files):
                    # 添加文件名到第一列
                    if row == len(zip_files) - 1:
                        # 设置最新存档
                        # logging.info(f"设置最新存档：{file}")
                        self.new_archive_val.setText(zip_name)

                    item1 = QTableWidgetItem(zip_name)
                    # 设置文本居中对齐（水平和垂直）
                    item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.archive_table.insertRow(row)
                    self.archive_table.setItem(row, 0, item1)

                    # 添加时间到到二列
                    dir_path = os.path.join(current_backup_dir, zip_name)
                    # 目录创建时间
                    dir_create_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                                    time.localtime(os.path.getctime(dir_path))
                                                    )

                    item2 = QTableWidgetItem(dir_create_time)
                    # 设置文本居中对齐（水平和垂直）
                    item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.archive_table.setItem(row, 1, item2)

                    # 按钮组
                    button_group_widget = QWidget()
                    # 按钮组布局
                    button_group_layout = QHBoxLayout(button_group_widget)
                    button_group_layout.setContentsMargins(0, 0, 0, 0)  # 消除布局的外边距

                    open_button = QPushButton("打开")
                    # 绑定按钮点击事件
                    open_button.clicked.connect(lambda _, f=dir_path: self.open_directory(f))
                    # 添加“打开”按钮到按钮组
                    button_group_layout.addWidget(open_button)

                    restore_button = QPushButton("回档")
                    # 绑定按钮点击事件
                    restore_button.clicked.connect(lambda _, f=dir_path: self.restore_backup(f))
                    # 添加“回档”按钮到按钮组
                    button_group_layout.addWidget(restore_button)

                    del_button = QPushButton("删除")
                    # 绑定按钮点击事件
                    del_button.clicked.connect(lambda _, f=dir_path: self.del_backup(f))
                    # 添加“删除”按钮到按钮组
                    button_group_layout.addWidget(del_button)

                    # 添加按钮组到第三列
                    self.archive_table.setCellWidget(row, 2, button_group_widget)
            else:
                # 无存档
                self.tip_columns(self.current_game_name)
        else:
            # 目录不存在
            create_dir(current_backup_dir)
            self.tip_columns(self.current_game_name)

    def tip_columns(self, game_name):
        self.archive_table.setRowCount(1)
        item = QTableWidgetItem(f"《{game_name}》无存档记录")
        # 设置文本居中
        item.setTextAlignment(Qt.AlignCenter)
        self.archive_table.setItem(0, 0, item)
        self.archive_table.setSpan(0, 0, 1, 5)

        self.new_archive_val.setText("")

    def open_source_directory(self):
        self.open_directory(self.source_dir)

    def open_directory(self, path):
        logging.info(f"打开目录:{path}")
        """打开所选存档的目录"""
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.warning(self, "错误", "选中的路径无效或不存在！")

    def del_backup(self, path):
        """执行删除回档操作"""
        if os.path.exists(path):
            # 实际的回档操作逻辑 (这里只是显示消息框)
            logging.info(f"删除存档：{path}")
            try:
                os.remove(path)
                QMessageBox.information(self, "删除成功", f"删除存档成功: {path}")
                # 加载列表
                self.refresh_table()
            except Exception as e:
                logging.info(f"Error occurred: {e}")  # 捕获并打印任何异常
        else:
            QMessageBox.warning(self, "错误", "选中的存档路径无效或不存在！")

    def browse_source_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择源文件目录")
        if directory:
            self.entry_source.setText(directory)

    def browse_backup_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择备份目录")
        if directory:
            self.entry_backup.setText(directory)

    def switch_game(self, game_key):
        # 当前游戏信息
        self.current_game = get_val(self.games_box_config, game_key)
        self.current_game_key = game_key
        self.current_game_name = self.current_game.get("name")

        # 识别环境变量 expandvars
        self.source_dir = os.path.expandvars(self.current_game.get("source"))
        self.backup_dir = os.path.expandvars(self.current_game.get("back"))
        self.entry_source.setText(self.source_dir)
        # logging.info(f"当前选择: {game_key}, game: {name}, source: {source}, back: {self.backup_dir}")
        logging.debug(f"当前选择: {self.current_game_key} : {self.current_game_name}")

        # 自动备份源目录
        self.start_backup_at_startup()

        # 加载列表
        self.refresh_table()

    def on_game_changed(self, index):
        """处理下拉框选项切换"""
        try:
            game_key = self.games_box.itemData(index)  # 选中的游戏的附加 userData (key)
            self.switch_game(game_key)
        except Exception as e:
            logging.info(f"Error occurred: {e}")  # 捕获并打印任何异常

    def start_backup(self):
        # 得到存档名
        archive_name = self.entry_archive_name.text()

        # 检测源文件夹和备份文件夹
        if not self.source_dir or not self.backup_dir:
            QMessageBox.warning(self, "错误", "请填写源文件目录和备份目录")
            return

        # 获取当前时间戳
        if not archive_name:
            archive_name = time.strftime('%Y%m%d%H%M%S')

        logging.info(f"准备对：{archive_name} 存档进行备份")
        # 组装当前存档目录
        backup_path = os.path.join(self.backup_dir, self.current_game_key, archive_name)
        # 创建备份目录
        create_dir(backup_path)
        # 创建备份数据

        zip_file_path = shutil.make_archive(backup_path, 'zip', self.source_dir)
        QMessageBox.information(self, "成功", f"备份《{zip_file_path}》完成！")

        # self.backup_data(backup_path)
        # 加载列表
        self.refresh_table()
        # 重置存档名
        self.entry_archive_name.setText("")

    def backup_data(self, backup_path):
        # 遍历源目录并复制文件
        for root, dirs, files in os.walk(self.source_dir):
            # 计算当前目录相对于 self.source_dir 的相对路径
            relative_path = os.path.relpath(root, self.source_dir)
            # 构造备份目录中的当前文件夹路径
            dest_dir = os.path.join(backup_path, relative_path)

            # 如果目标目录不存在，创建它
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                logging.info(f"创建目录:{dest_dir}")

            # 复制文件
            for file in files:
                source_file = os.path.join(root, file)
                backup_file = os.path.join(dest_dir, file)
                shutil.copy2(source_file, backup_file)
                logging.info(f"备份文件: {source_file} -> {backup_file}")

        QMessageBox.information(self, "成功", f"备份《{self.current_game_name}》完成！")

    def restore_backup(self, backup_path):
        """执行回档操作"""
        # 检查备份路径是否存在
        if not os.path.exists(backup_path):
            QMessageBox.warning(self, "错误", "选中的备份路径不存在！")
            return

        # 源目录（要回档到的目标目录）
        source_dir = self.source_dir

        # 2. 复制备份目录的内容到源目录
        try:
            for root, dirs, files in os.walk(backup_path):
                relative_path = os.path.relpath(root, backup_path)  # 相对路径
                target_dir = os.path.join(source_dir, relative_path)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)  # 创建目标目录

                # 复制文件
                for file in files:
                    shutil.copy2(os.path.join(root, file), os.path.join(target_dir, file))

            QMessageBox.information(self, "回档成功", "存档回档成功！")
        except Exception as e:
            QMessageBox.warning(self, "回档失败", f"回档过程中出错: {str(e)}")
