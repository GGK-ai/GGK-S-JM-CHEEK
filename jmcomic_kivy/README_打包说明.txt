=============================================
   ✨ 邪王真眼 · 禁漫宝 安卓版
   在线APK打包说明
=============================================

【方法一：用GitHub Actions免费打包（推荐）】
1. 把这个文件夹整个上传到你的GitHub仓库
2. 在仓库根目录创建 .github/workflows/build.yml 文件
3. 用以下内容：

name: Build APK
on: [push, workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
          pip install --upgrade pip
          pip install buildozer cython
      - name: Build APK with Buildozer
        run: |
          cd jmcomic_kivy
          buildozer android debug
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: jmcomic-app
          path: jmcomic_kivy/bin/*.apk

4. 推送到GitHub后，进入 Actions 标签页
5. 等待打包完成（大约30-60分钟）
6. 打包完成后下载APK文件安装到手机

【方法二：使用在线APK打包网站】
可以搜索以下在线服务上传打包：
- AppBuilder（需注册）
- 云编译平台如 Codemagic

【方法三：在电脑上用WSL/Linux本地打包】
如果有Linux环境，直接运行：
  cd jmcomic_kivy
  buildozer android debug

【注意】
- 打包过程较长，请耐心等待
- APK包大约 30-50MB
- 安装后首次打开需要网络连接
- 需要给APP「读写存储空间」权限

有问题联系作者：邪王真眼使者·六花
