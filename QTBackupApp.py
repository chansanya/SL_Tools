import os
import stat
import shutil
import time
from config.config import get_val, get_config
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QMenuBar, QFrame, QAction, QDialog, QFormLayout,QDialogButtonBox,QScrollArea,
                             QFileDialog, QMessageBox, QHeaderView, QTableWidget, QComboBox, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
import logging
import sys
import zipfile
from config.config import update_config


def create_dir(backup_path):
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
        # 设置文件夹为可读写
        os.chmod(backup_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    else:
        os.chmod(backup_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


create_dir("./logs")

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为INFO
    format='%(asctime)s %(levelname)s %(message)s',  # 日志格式
    handlers=[
        logging.FileHandler('logs/run.log', mode='a', encoding='utf-8'),  # 追加模式写入文件，解决中文乱码
        logging.StreamHandler(sys.stdout)  # 输出到控制台
    ]
)


class QTBackupApp(QWidget):
    def __init__(self):
        super().__init__()

        self.config = get_config()

        if self.config is None:
            logging.error("请检查配置")
            raise Exception("请检查配置")

        self.games_box_config = get_val(self.config, "games")
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
        self.button_reset_new = None
        self.button_reset_init = None
        self.button_refresh = None

        # 最新存档
        self.new_archive_label = None
        self.new_archive_val = None

        # 存档表
        self.archive_table_label = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('SL工具')

        # 创建布局
        layout = QVBoxLayout()
        # 创建菜单栏
        menu_bar = QMenuBar(self)

        # 添加"管理游戏"菜单项
        manage_games_action = QAction("管理游戏", self)
        menu_bar.addAction(manage_games_action)
        # 连接菜单点击事件
        manage_games_action.triggered.connect(self.open_manage_games_dialog)

        # 添加"设置"菜单项
        manage_settings_action = QAction("设置", self)
        menu_bar.addAction(manage_settings_action)
        # 连接菜单点击事件
        manage_settings_action.triggered.connect(self.open_manage_games_dialog)


        w = get_val(self.windows_config, "w")
        h = get_val(self.windows_config, "h")
        self.setFixedSize(w, h)  # 如果你想让窗口固定大小，不允许用户调整大小


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
        self.button_reset_new = QPushButton('回档至最新', self)
        self.button_reset_new.clicked.connect(self.restore_backup_new)
        # 回档按钮
        self.button_reset_init = QPushButton('回档至初始', self)
        self.button_reset_init.clicked.connect(self.restore_backup_init)

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
        self.archive_table.setEditTriggers(QTableWidget.NoEditTriggers)

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
        but_layout.addWidget(self.button_reset_new)
        but_layout.addWidget(self.button_reset_init)
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

        # 设置菜单栏
        layout.setMenuBar(menu_bar)
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

    def open_manage_games_dialog(self):
        """打开管理游戏弹窗"""
        dialog = QDialog(self)
        dialog.setWindowTitle("管理游戏")
        dialog.setFixedSize(500, 400)

        # 外部布局
        dialog_layout = QVBoxLayout(dialog)

        # 添加可滚动区域来显示卡片
        scroll_area = QScrollArea(dialog)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)


        # 添加游戏的表单
        form_layout = QFormLayout()

        # 游戏名输入框
        game_name_edit = QLineEdit(dialog)
        form_layout.addRow("游戏名:", game_name_edit)

        # 源路径输入框和选择按钮
        source_dir_edit = QLineEdit(dialog)
        source_dir_button = QPushButton("选择源路径", dialog)
        source_dir_button.clicked.connect(lambda: self.choose_directory(source_dir_edit))
        source_layout = QHBoxLayout()
        source_layout.addWidget(source_dir_edit)
        source_layout.addWidget(source_dir_button)
        form_layout.addRow("源路径:", source_layout)

        # 存档路径输入框和选择按钮
        backup_dir_edit = QLineEdit(dialog)
        backup_dir_button = QPushButton("选择存档路径", dialog)
        backup_dir_button.clicked.connect(lambda: self.choose_directory(backup_dir_edit))
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(backup_dir_edit)
        backup_layout.addWidget(backup_dir_button)
        form_layout.addRow("存档路径:", backup_layout)

        dialog_layout.addLayout(form_layout)
        dialog_layout.addWidget(scroll_area)

        # 确认和取消按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        dialog_layout.addWidget(buttons)

        # 添加游戏按钮的事件
        buttons.accepted.connect(
            lambda: self.add_game_card(game_name_edit.text(), source_dir_edit.text(), backup_dir_edit.text(),
                                       scroll_layout, dialog))
        buttons.rejected.connect(dialog.reject)

        dialog.exec_()

    def choose_directory(self, line_edit):
        """打开文件选择器并将选择的路径设置到对应的 QLineEdit"""
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
        if directory:
            line_edit.setText(directory)

    def add_game_card(self, game_name, source_dir, backup_dir, scroll_layout, dialog):
        """添加新的游戏卡片到滚动区域"""
        if not game_name or not source_dir or not backup_dir:
            QMessageBox.warning(self, "错误", "请填写所有字段")
            return

        # 创建卡片小部件
        card = QFrame()
        card.setFrameShape(QFrame.Box)
        card_layout = QHBoxLayout(card)

        # 添加卡片内容
        game_label = QLabel(f"游戏名: {game_name}\n源路径: {source_dir}\n存档路径: {backup_dir}", card)
        card_layout.addWidget(game_label)

        # 删除按钮
        delete_button = QPushButton("删除", card)
        delete_button.clicked.connect(lambda: self.remove_game_card(card, scroll_layout))
        card_layout.addWidget(delete_button)

        # 将卡片添加到布局
        scroll_layout.addWidget(card)

        # 清空输入框
        dialog.findChild(QLineEdit, "").setText("")

    def remove_game_card(self, card, scroll_layout):
        """删除游戏卡片"""
        scroll_layout.removeWidget(card)
        card.deleteLater()

    def start_backup_at_startup(self):
        """程序启动时备份源目录为压缩包"""
        if self.source_dir and os.path.exists(self.source_dir):
            # 组装当前存档目录
            backup_path = os.path.join(self.backup_dir, self.current_game_key, f"{self.current_game_name}默认备份")
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
            logging.info(f"{self.current_game_name}:源目录 :{self.source_dir} 不存在，无法备份！")
            QMessageBox.warning(self, "错误", f"《{self.current_game_name}》源目录不存在,请检查游戏路径！")

    def refresh_table(self):
        """读取备份目录下的文件并添加到表格中"""
        current_backup_dir = os.path.join(self.backup_dir, self.current_game_key)

        if os.path.exists(current_backup_dir):
            # 获取目录下的一级文件名
            # dirs = os.listdir(current_backup_dir)
            zip_files = [f for f in os.listdir(current_backup_dir) if f.endswith('.zip')]
            # 清空表格，重置表格行数为 0
            self.archive_table.setRowCount(0)

            zip_paths = [os.path.join(current_backup_dir, file) for file in zip_files]
            if len(zip_files) > 0:
                latest_file = max(zip_paths, key=os.path.getctime)
                latest_file_name = os.path.basename(latest_file)
                # 设置最新存档
                self.new_archive_val.setText(latest_file_name)

                # 遍历文件并添加到表格中
                for row, zip_name in enumerate(zip_files):
                    item1 = QTableWidgetItem(os.path.splitext(zip_name)[0])
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
                    restore_button.clicked.connect(lambda _, f=dir_path, n=zip_name: self.restore_backup(f, n))
                    # 添加“回档”按钮到按钮组
                    button_group_layout.addWidget(restore_button)

                    del_button = QPushButton("删除")
                    # 绑定按钮点击事件
                    del_button.clicked.connect(lambda _, f=dir_path, n=zip_name: self.del_backup(f, n))
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

    def tip_columns(self, game_name, handle=None):
        self.archive_table.setRowCount(1)
        message = f"《{game_name}》无存档记录"

        message = handle(message) if handle else message
        item = QTableWidgetItem(message)

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

    def del_backup(self, path, zip_name):
        """执行删除回档操作"""
        if "默认备份.zip" in zip_name:
            reply = QMessageBox.question(
                None,  # 父窗口, 如果有的话
                "确认操作",  # 弹窗标题
                f"删除默认存档出现问题将无法恢复存档，您确定要删除嘛？",  # 弹窗内容
                QMessageBox.Yes | QMessageBox.No,  # 按钮选择
                QMessageBox.No  # 默认按钮
            )

            # 如果用户点击了 "Yes"
            if reply == QMessageBox.Yes:
                logging.info(f"允许删除默认配置：{path}")
            else:
                # QMessageBox.information(self, "提示", f"操作取消")
                return

        if os.path.exists(path):
            # 实际的回档操作逻辑 (这里只是显示消息框)
            logging.info(f"删除存档：{path}")
            try:
                os.remove(path)
                QMessageBox.information(self, "删除成功", f"删除存档成功")
                logging.info(f"删除存档成功: {path}")
                # 加载列表
                self.refresh_table()
            except Exception as e:
                logging.info(f"Error occurred: {e}")  # 捕获并打印任何异常
        else:
            QMessageBox.warning(self, "错误", "选中的存档路径无效或不存在！")
            logging.error(f"选中的存档路径无效或不存在: {path}")

    def browse_source_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择源文件目录")
        if directory:
            # 修复路径
            old = self.config["games"][self.current_game_key]
            print(f"需要修改:{old}  directory:{directory}")
            self.config["games"][self.current_game_key]["source"] = directory
            update_config(self.config)
            self.entry_source.setText(directory)

    def switch_game(self, game_key):
        # 当前游戏信息
        self.current_game = get_val(self.games_box_config, game_key)
        self.current_game_key = game_key
        self.current_game_name = self.current_game.get("name")

        # 识别环境变量 expandvars
        self.source_dir = os.path.expandvars(self.current_game.get("source"))
        self.source_dir = self.source_dir.replace("\\", "/")
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
            logging.info(f"切换游戏失败: {e}")  # 捕获并打印任何异常

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
        QMessageBox.information(self, "成功", f"《{archive_name}》存档成功！")

        logging.info(f"{archive_name} 存档生成成功 ，存档路径：{zip_file_path}")
        # 加载列表
        self.refresh_table()
        # 重置存档名
        self.entry_archive_name.setText("")

    def restore_backup_new(self):
        archive_name = self.new_archive_val.text()
        self.restore_backup_to_archive_name(archive_name, f"程序初始存档为《{archive_name}》，您确定回档至此嘛？")

    def restore_backup_init(self):
        archive_name = f"{self.current_game_name}默认备份.zip"
        self.restore_backup_to_archive_name(archive_name, f"程序初始存档为《{archive_name}》，您确定回档至此嘛？")

    def restore_backup_to_archive_name(self, archive_name, message):
        backup_path = os.path.join(self.backup_dir, self.current_game_key, archive_name)
        reply = QMessageBox.question(
            None,  # 父窗口, 如果有的话
            "确认操作",  # 弹窗标题
            message,  # 弹窗内容
            QMessageBox.Yes | QMessageBox.No,  # 按钮选择
            QMessageBox.No  # 默认按钮
        )
        if reply == QMessageBox.Yes:
            logging.info(f"允许回档至：{archive_name}")
        else:
            # QMessageBox.information(self, "提示", f"操作取消")
            return

        self.restore_backup(backup_path, archive_name)

    def restore_backup(self, backup_path, zip_name):
        logging.info(f"此次回档：{zip_name} -> {backup_path} ")
        """执行回档操作"""
        # 检查备份路径是否存在
        if not os.path.exists(backup_path):
            QMessageBox.warning(self, "错误", "选中的存档路径不存在！")
            return

        # 确保备份路径是一个 ZIP 文件
        if not zipfile.is_zipfile(backup_path):
            QMessageBox.warning(self, "错误", "选中的不是有效的 ZIP 文件！")
            return

        # 源目录（要回档到的目标目录）
        source_dir = self.source_dir

        # 检查源目录是否存在，如果不存在则创建
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)

        try:
            # 打开并解压缩 ZIP 文件
            with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                zip_ref.extractall(source_dir)  # 将压缩包中的所有文件解压到源目录

            logging.info(f"成功解压 {backup_path} 到 {source_dir}")
            QMessageBox.information(self, f"回档成功", f"回档《{os.path.splitext(zip_name)[0]}》成功！")

        except Exception as e:
            logging.error(f"回档过程中出错: {str(e)}", exc_info=True)
            QMessageBox.warning(self, "回档失败", f"回档过程中出错: {str(e)}")
