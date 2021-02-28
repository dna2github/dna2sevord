# Android

> ref: https://stackoverflow.com/questions/41132753/how-can-i-build-an-android-apk-without-gradle-on-the-command-line

> ref: https://github.com/WanghongLin/miscellaneous/blob/master/tools/build-apk-manually.sh

```shell
#!/bin/bash

set -xe
# A Simple Script to build a simple APK without ant/gradle
# Copyright 2016 Wanghong Lin 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# 	http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 

# create a simple Android application to test this script
# 
# $ android create project -n MyApplication -p MyApplication -k com.example -a MainActivity --target 8
#
# copy this script to the root of your Android project and run

[ x$ANDROID_SDK_ROOT == x ] && {
    printf '\e[31mANDROID_SDK_ROOT not set\e[30m\n'
	exit 1
}

[ ! -d $ANDROID_SDK_ROOT ] && {
    printf "\e[31mInvalid ANDROID_SDK_ROOT ---> $ANDROID_SDK_ROOT\e[30m\n"
	exit 1
}

# usuage:
# bash build.sh android-xx someApp

# use the latest build tool version
# and the oldest platform version for compatibility
_BUILD_TOOLS_VERSION=$(ls $ANDROID_SDK_ROOT/build-tools | sort -n |tail -1)
_PLATFORM=$1 #$(ls $ANDROID_SDK_ROOT/platforms | sort -nr |tail -1) 
_APK_BASENAME=$2
_ANDROID_CP=$ANDROID_SDK_ROOT/platforms/$_PLATFORM/android.jar
_AAPT=$ANDROID_SDK_ROOT/build-tools/$_BUILD_TOOLS_VERSION/aapt
_DX=$ANDROID_SDK_ROOT/build-tools/$_BUILD_TOOLS_VERSION/dx
_D8=$ANDROID_SDK_ROOT/build-tools/$_BUILD_TOOLS_VERSION/d8
_ZIPALIGN=$ANDROID_SDK_ROOT/build-tools/$_BUILD_TOOLS_VERSION/zipalign
_ADB=$ANDROID_SDK_ROOT/platform-tools/adb
_INTERMEDIATE="bin gen ${_APK_BASENAME}.apk.unaligned"

printf "\e[32mBuild with configuration: \n\tbuild tools version: $_BUILD_TOOLS_VERSION \n\tplatform: $_PLATFORM\e[0m\n"

rm -rf $_INTERMEDIATE
mkdir bin gen

$_AAPT package -f -m -J gen -M AndroidManifest.xml -S res -I $_ANDROID_CP

javac -classpath $_ANDROID_CP \
	-sourcepath 'src:gen' \
	-d 'bin' -target 1.7 -source 1.7 \
	`find . -name "*.java"`

$_DX --dex --min-sdk-version=26 --output=classes.dex bin

$_AAPT package -f -M AndroidManifest.xml -S res -I $_ANDROID_CP -F ${_APK_BASENAME}.apk.unaligned

$_AAPT add ${_APK_BASENAME}.apk.unaligned classes.dex

jarsigner -keystore ~/.android/debug.keystore -storepass 'android' ${_APK_BASENAME}.apk.unaligned androiddebugkey
# create a release version with your keys
# jarsigner -keystore /path/to/your/release/keystore -storepass 'yourkeystorepassword' ${_APK_BASENAME}.apk.unaligned yourkeystorename 

$_ZIPALIGN -f 4 ${_APK_BASENAME}.apk.unaligned ${_APK_BASENAME}-debug.apk

rm -rf $_INTERMEDIATE

#find bin -type f | xargs -I {} $_D8 --lib $_ANDROID_CP --min-api 25 {}
#$_D8 --lib $_ANDROID_CP --min-api 26 ${_APK_BASENAME}-debug.apk

#$_ADB get-state 1>/dev/null 2>&1 && $_ADB install -r ${_APK_BASENAME}-debug.apk || printf '\e[31mNo Android device attach\e[30m\n'
```

# Flutter

```shell
flutter create <project_name>
flutter pub get
flutter devices
flutter run
flutter build apk --split-per-abi
flutter install
```

ref: https://flutter.dev/docs/deployment/android
