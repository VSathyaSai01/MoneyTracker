[app]

# App Title
title = MoneyTracker

# Package Information
package.name = moneytracker
package.domain = org.moneytracker

# Source
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ico

# Version
version = 1.0

# Requirements
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow

# Orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Permissions
android.permissions = INTERNET

# Automatically accept SDK licenses
android.accept_sdk_license = True

# Stable Android Configuration
android.api = 31
android.minapi = 21

# SDK / NDK
android.sdk = 25
android.ndk = 25b
android.ndk_api = 21

# Architectures
android.archs = arm64-v8a, armeabi-v7a

# Logging
log_level = 2
warn_on_root = 1


[buildozer]

log_level = 2
warn_on_root = 1
