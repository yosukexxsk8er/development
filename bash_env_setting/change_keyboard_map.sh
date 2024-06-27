#!/bin/bash

# Update package lists
sudo apt update

# Install necessary packages
sudo apt install -y gnome-tweaks x11-xserver-utils

# Backup existing keyboard configuration
sudo cp /etc/default/keyboard /etc/default/keyboard.bak

# Update keyboard configuration for swapping Ctrl and Caps Lock
sudo sed -i 's/^XKBOPTIONS=.*/XKBOPTIONS="ctrl:swapcaps"/' /etc/default/keyboard

# Reconfigure keyboard settings
sudo dpkg-reconfigure -f noninteractive keyboard-configuration

# Create or update .Xmodmap for swapping Esc and Zenkaku_Hankaku and setting underscore without Shift
cat <<EOF > ~/.Xmodmap
keycode 49 = Escape
keycode 9 = Zenkaku_Hankaku
keycode 20 = underscore
EOF

# Apply the .Xmodmap configuration
xmodmap ~/.Xmodmap

# Ensure .xprofile runs xmodmap on startup
if ! grep -q "xmodmap ~/.Xmodmap" ~/.xprofile; then
  echo "xmodmap ~/.Xmodmap" >> ~/.xprofile
fi

echo "Keyboard remapping completed. Please restart your session for changes to take effect."
