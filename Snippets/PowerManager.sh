#!/bin/bash

set -o errexit -o nounset

power_manager() {
    # Kill subprocesses on exit
    trap 'pkill --parent "$$"' EXIT

    # Lock and turn off screen on inactivity, sleep and hibernate
    xset dpms 0 0 300
    xss-lock i3lock &

    upower --monitor | while read -r _; do
        local plugged capacity lid
        plugged=$(cat '/sys/class/power_supply/ADP1/online')
        capacity=$(cat '/sys/class/power_supply/BAT0/capacity')
        lid=$(cat '/proc/acpi/button/lid/LID0/state')

        # Update i3blocks power block
        pkill -RTMIN+13 i3blocks

        # Critical power at 10% of battery. By default UPower launches hybrid
        # sleep at 2% of battery charge. See '/etc/UPower/UPower.conf'.
        if [[ "$plugged" -eq 0 && "$capacity" -le 10 ]]; then
            systemctl hibernate
        fi

        # Handle lid
        if [[ "$lid" == 'state:      closed' ]]; then
            systemctl hibernate
        fi
    done
}

if [[ "$*" == '--launch' ]]; then
    power_manager
else
    systemd-inhibit \
        --what='handle-power-key:handle-suspend-key:handle-hibernate-key:handle-lid-switch:handle-reboot-key' \
        --why='power manager' --mode='block' \
        "$0" --launch
fi
