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

# requirements - 轻量版！不用curl_cffi！
requirements = python3,kivy,requests

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

# 屏幕方向
orientation = portrait

# 是否全屏
fullscreen = 0

# 日志级别
log_level = 2

# Python版本
python3.version = 3.11
