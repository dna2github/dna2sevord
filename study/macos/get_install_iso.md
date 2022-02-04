# get MacOS installation ISO


1. download full `MacOS Big Sur.app` about 12GB: `softwareupdate --fetch-full-installer --full-installer-version 11.6`
2. create dmg file: `hdiutil create -o ~/Desktop/macOS.dmg -size 12945m -volname macOS -layout SPUD -fs HFS+J`
3. mount dmg to a folder: `hdiutil attach ~/Desktop/macOS.dmg -noverify -mountpoint /Volumes/macOS`
4. create MacOX boot disk: `sudo /Applications/Install\ macOS\ Big\ Sur.app/Contents/Resources/createinstallmedia --volume /Volumes/macOS --nointeraction`
5. unmount `MacOS Big Sur.app`: `hdiutil detach -force /Volumes/Install\ macOS\ Big\ Sur`
6. Convert dmg to iso: `hdiutil convert ~/Desktop/macOS.dmg -format UDTO -o ~/Desktop/macos-big-sur && mv ~/Desktop/macos-big-sur.cdr ~/Desktop/macos-big-sur.iso`

ref: https://graspingtech.com/download-macos-installer/
ref: https://graspingtech.com/create-bootable-macos-iso/
ref: https://graspingtech.com/vmware-fusion-macos-big-sur/
