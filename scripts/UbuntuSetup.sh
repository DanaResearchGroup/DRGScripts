#! /bin/bash

# run this script on a fresh Ubuntu install with the new temporary password as the first argument,
# provide the common group name as the second argument
# if new users, append them in order of desired ID to USERS list
# once we start removing users/students leave group...

INITPW=$1
GNAME=$2

sudo apt update && sudo apt upgrade

#set to auto update (sometime late, basically random)
echo "11 2    * * *   root    apt update && apt upgrade -y" | sudo tee -a /etc/crontab

# add our current users and groups
# this will have to be changed once we drop users, but for now it's ok
USERS=(
    # list usernames here in order from UID 1002 on
    # UID/GID 1000 is the admin who did the install
    # UID/GID 1001 is the common group/user
)

STARTUID=1001
STARTGID=$STARTUID

# common account
sudo useradd -m -u $STARTUID $GNAME -p $INITPW
((STARTUID++))

#individual user accounts
for USER in "${USERS[@]}"; do
	sudo useradd -m -u $((STARTUID++)) -g $STARTGID $USER -p $INITPW
done


#SSH
sudo apt install net-tools && \
sudo apt install openssh-server && \
sudo systemctl enable ssh

#make record of machine hardware
sudo apt install hw-probe && sudo -E hw-probe -all -upload

#important utilities
sudo apt install git gcc g++ make numlockx vim zsh

#KDE
sudo apt install kde-plasma-desktop


## IDEs
#Codium
wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg \
    | gpg --dearmor \
    | sudo dd of=/usr/share/keyrings/vscodium-archive-keyring.gpg
echo 'deb [ signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg ] https://download.vscodium.com/debs vscodium main' \
    | sudo tee /etc/apt/sources.list.d/vscodium.list
sudo apt update && sudo apt install codium

#PyCharm
sudo snap install pycharm-community --classic

#Slack
sudo snap install slack --classic

#AnyDesk
wget -qO - https://keys.anydesk.com/repos/DEB-GPG-KEY | sudo apt-key add -
echo "deb http://deb.anydesk.com/ all main" | sudo tee /etc/apt/sources.list.d/anydesk-stable.list
sudo apt update && sudo apt install anydesk


#Other stuff I like
#sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
