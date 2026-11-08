[app]

# (str) Title of your application
title = Platformer

# (str) Package name
package.name = platformer

# (str) Package domain (needed for android packaging)
package.domain = org.platformer

# (list) Source files to include (let git decide or specify extensions)
source.dir = .

# (list) Source files to include (allow extension)
source.include_exts = py,png,jpg,kv,atlas,mp3,wav

# (list) List of inclusion/exclusion patterns
source.include_patterns = assets/*,Servers/*

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pygame

# (str) Custom source folders for python modules
#source.main.ext = py

# (str) Application versioning
version = 0.1

# (list) Supported orientations
# Valid options are: landscape, portrait, all
orientation = landscape

# (list) List of permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android arch to build for, options: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) Automatically accept SDK license
android.accept_sdk_license = True


[buildozer]

# (int) Log level (0 = error, 1 = info, 2 = debug (with command output))
log_level = 2

# (str) Path to build artifact, default is ./.git/../bin
bin_dir = ./bin
