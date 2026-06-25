[app]

# 应用名称
title = JMComic禁漫宝

# 包名
package.name = jmcomic

# 完整包域名
package.domain = org.jmcomic.app

# 源码目录
source.dir = .

# 源码文件扩展名
source.include_exts = py,png,jpg,kv,atlas

# 版本
version = 1.0.0

# 版本号
version.code = 1

# requirements
requirements = python3,kivy,jmcomic,curl_cffi,pycryptodome,pyyaml, Pillow

# 权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API level
android.api = 31

# Android NDK version
android.ndk = 23b

# Android SDK version
android.sdk = 31

# 最低安卓版本
android.minapi = 21

# 目标安卓版本
android.targetapi = 31

# 是否启用AndroidX
android.enable_androidx = True

# 是否使用默认的Activity作为启动画面
android.use_default_activity = True

# 支持的架构
android.archs = arm64-v8a

# 图标文件（可选的，可以放一个png）
# android.icon = icon.png

# 屏幕方向
orientation = portrait

# 是否全屏
fullscreen = 0

# 日志级别
log_level = 2

# 是否启用广告
android.enable_ads = False

# 是否启用Google Play服务
android.enable_google_play = False

# Python版本
python3.version = 3.11

# 一些额外的jar/aar文件
# android.add_aars =

# 确保curl_cffi有底层依赖
android.extra_libs_dirs = 
