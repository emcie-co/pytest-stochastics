#!/bin/bash

# Function to print color blocks
print_color() {
    for fg in 30 31 32 33 34 35 36 37; do
        for bg in 40 41 42 43 44 45 46 47; do
            echo -en "\e[${fg}m\e[${bg}m ${fg};${bg} \e[0m"
        done
        echo
    done
}

# Function to print 256 color blocks
print_256_color() {
    for fgbg in 38 48; do
        for color in {0..255}; do
            printf "\e[${fgbg};5;%sm  %3s  \e[0m" $color $color
            if [ $((($color + 1) % 6)) == 4 ]; then
                echo
            fi
        done
        echo
    done
}

echo "Standard Colors:"
print_color

echo -e "\n8-bit (256) Colors:"
echo "Foreground Colors (38;5;XXXm):"
print_256_color

echo -e "\nBackground Colors (48;5;XXXm):"
print_256_color

echo -e "\nTrue Color Examples:"
echo -e "\e[38;2;255;0;0mRed Foreground\e[0m"
echo -e "\e[48;2;0;255;0mGreen Background\e[0m"
echo -e "\e[38;2;0;0;255m\e[48;2;255;255;0mBlue on Yellow\e[0m"