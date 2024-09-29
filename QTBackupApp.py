import os
import shutil
import time
from config.config import get_val, get_config
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QMessageBox, QHeaderView, QTableWidget, QComboBox, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl


class QTBackupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.config = get_config()

        if self.config is None:
            raise Exception("请检查配置")

        self.games_box_config = get_val(self.config, "games")
        self.win_config = get_val(self.config, "games")
        self.windows_config = get_val(self.config, "windows")

        self.current_game = None
        self.current_game_key = None

        # 选择游戏
        self.select_game_label = None
        self.games_box = None

        # 源路径
        self.label_source = None
        self.entry_source = None
        self.button_source = None

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
        self.button_source = QPushButton('选择目录', self)
        self.button_source.clicked.connect(self.browse_source_dir)

        self.archive_name_label = QLabel('存档名:')
        self.entry_archive_name = QLineEdit(self)

        # 开始备份按钮
        self.button_start_backup = QPushButton('开始备份', self)
        self.button_start_backup.clicked.connect(self.start_backup)

        # 回档按钮
        self.button_reset = QPushButton('最新回档', self)
        self.button_reset.clicked.connect(self.reset_backup)

        self.archive_table_label = QLabel('存档列表:')
        self.archive_table_label.setAlignment(Qt.AlignLeft)

        # 创建一个 QTableWidget 来显示存档文件和操作按钮
        self.archive_table = QTableWidget(self)
        columns = ["存档名", "存档时间", "打开目录", "回档", "删除"]
        self.archive_table.setHorizontalHeaderLabels(columns)
        self.archive_table.setColumnCount(len(columns))
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

        # 存档列表
        archive_name_layout = QHBoxLayout()
        archive_name_layout.addWidget(self.archive_name_label)
        archive_name_layout.addWidget(self.entry_archive_name)

        # 按钮
        but_layout = QHBoxLayout()
        but_layout.addWidget(self.button_start_backup)
        but_layout.addWidget(self.button_reset)

        # 存档列表
        archive_list_layout = QHBoxLayout()
        archive_list_layout.addWidget(self.archive_table_label)
        archive_list_layout.addWidget(self.archive_table)

        # 添加到总控件
        layout.addLayout(games_layout)
        layout.addLayout(source_layout)
        layout.addLayout(archive_name_layout)
        layout.addLayout(but_layout)
        layout.addLayout(archive_list_layout)
        # 设置布局
        self.setLayout(layout)
        # 初始化值
        self.init_val()

    def init_val(self):
        self.switch_game(self.games_box.itemData(0))

    def load_archive_table(self):
        """读取备份目录下的文件并添加到表格中"""
        current_backup_dir = os.path.join(self.backup_dir, self.current_game_key)

        if os.path.exists(current_backup_dir):
            # 获取目录下的一级文件名
            files = os.listdir(current_backup_dir)
            self.archive_table.setRowCount(len(files))  # 根据文件数量设置行数

            # 遍历文件并添加到表格中
            for row, file in enumerate(files):
                full_path = os.path.join(current_backup_dir, file)

                # 获取文件创建时间
                creation_time = os.path.getctime(full_path)

                # 将时间戳转换为可读的格式
                readable_time = time.ctime(creation_time)

                # 添加文件名到第一列
                self.archive_table.setItem(row, 0, QTableWidgetItem(file))
                self.archive_table.setItem(row, 1, QTableWidgetItem(readable_time))

                # 添加“打开目录”按钮到第二列
                open_button = QPushButton("打开目录")
                open_button.clicked.connect(lambda _, f=full_path: self.open_directory(f))  # 绑定按钮点击事件
                self.archive_table.setCellWidget(row, 2, open_button)

                # 添加“回档”按钮到第三列
                restore_button = QPushButton("回档")
                restore_button.clicked.connect(lambda _, f=full_path: self.restore_backup(f))  # 绑定按钮点击事件
                self.archive_table.setCellWidget(row, 3, restore_button)

                # 添加“回档”按钮到第三列
                del_button = QPushButton("删除")
                del_button.clicked.connect(lambda _, f=full_path: self.del_backup(f))  # 绑定按钮点击事件
                self.archive_table.setCellWidget(row, 4, del_button)

        else:
            self.archive_table.setRowCount(1)
            self.archive_table.setItem(0, 0, QTableWidgetItem("备份目录不存在"))

    def open_directory(self, path):
        """打开所选存档的目录"""
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.warning(self, "错误", "选中的路径无效或不存在！")

    def restore_backup(self, path):
        """执行回档操作"""
        if os.path.exists(path):
            # 实际的回档操作逻辑 (这里只是显示消息框)
            QMessageBox.information(self, "回档成功", f"成功回档: {path}")
        else:
            QMessageBox.warning(self, "错误", "选中的存档路径无效或不存在！")

    def del_backup(self, path):
        """执行删除回档操作"""
        if os.path.exists(path):
            # 实际的回档操作逻辑 (这里只是显示消息框)
            QMessageBox.information(self, "删除成功", f"删除存档成功: {path}")
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
        item = get_val(self.games_box_config, game_key)
        self.current_game = item
        self.current_game_key = game_key
        name = self.current_game.get("name")

        source = item.get("source")
        back = item.get("back")

        self.entry_source.setText(source)
        self.backup_dir = back
        self.source_dir = source

        # print(f"当前选择: {game_key}, game: {name}, source: {source}, back: {self.backup_dir}")
        print(f"当前选择: {self.current_game_key} : {name}")

        # 加载列表
        self.load_archive_table()

    def on_game_changed(self, index):
        """处理下拉框选项切换"""
        try:
            game_key = self.games_box.itemData(index)  # 选中的游戏的附加 userData (key)
            self.switch_game(game_key)
        except Exception as e:
            print(f"Error occurred: {e}")  # 捕获并打印任何异常

    def reset_input_widget(self, widget):
        widget.setText("")

    def start_backup(self):
        archive_name = self.entry_archive_name.text()
        print(f"准备对：{archive_name} 存档进行备份")

        if not self.source_dir or not self.backup_dir:
            QMessageBox.warning(self, "错误", "请填写源文件目录和备份目录")
            return

        # 获取当前时间戳
        if not archive_name:
            archive_name = time.strftime('%Y%m%d%H%M%S')

        # 备份的目标目录
        backup_path = os.path.join(self.backup_dir, self.current_game_key, archive_name)

        # 创建备份目录
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        # 备份文件的类型 (可以根据需要更改)
        file_extensions = ['.txt', '.log']

        # 遍历源目录并复制文件
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    source_file = os.path.join(root, file)
                    backup_file = os.path.join(backup_path, file)

                    # 执行文件拷贝
                    shutil.copy2(source_file, backup_file)
                    print(f"备份文件:{source_file}->{backup_file}")

        name = self.current_game.get("name")
        QMessageBox.information(self, "成功", f"备份《{name}》完成！")
        # QMessageBox.information(self, "成功", f"备份《{name}》完成！备份至: {backup_path}")

        # 加载列表
        self.load_archive_table()
        # 重置组件值
        self.reset_input_widget(self.entry_archive_name)

    def reset_backup(self):
        #
        print("开始回档")
