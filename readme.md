SL工具

支持
- 黑神话悟空
- 艾尔登法环


## 运行
```shell
python main.py
```

## 打包成exe
### 安装 pyinstaller
```shell
pip install pyinstaller
```
### 设置打包
```shell
pyinstaller --onefile main.py
```

### 无控制台输出打包
```shell
pyinstaller --onefile --noconsole main.py
```

###  清理打包文件
```shell
rm  -Force  -Recurse dist,build,*.spec,*.log
```


