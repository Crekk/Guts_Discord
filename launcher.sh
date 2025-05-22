#!/bin/bash

clear
echo "=============================================="
echo "       Guts Berserk 2 Discord Launcher"
echo "=============================================="
echo ""
echo "Please select which version to launch:"
echo "1. CharacterAI"
echo "2. OpenAI API"
echo "3. KoboldCCP"
echo "Q. Quit"
echo "=============================================="

read -p "Enter your choice (1, 2, or Q): " choice

cd "$(dirname "$0")" || exit 1

if command -v gnome-terminal >/dev/null 2>&1; then
    TERMINAL="gnome-terminal -- bash -c"
elif command -v xfce4-terminal >/dev/null 2>&1; then
    TERMINAL="xfce4-terminal --hold -e bash -c"
elif command -v konsole >/dev/null 2>&1; then
    TERMINAL="konsole --noclose -e bash -c"
elif command -v xterm >/dev/null 2>&1; then
    TERMINAL="xterm -hold -e"
else
    echo "No known terminal emulator found! Please install one (e.g. gnome-terminal, xfce4-terminal, konsole, xterm)."
    exit 1
fi

case "$choice" in
    1)
        echo "Launching CharacterAI Version..."
        $TERMINAL "python3 guts_cai.py; exec bash"
        ;;
    2)
        echo "Launching OpenAI Version..."
        $TERMINAL "python3 guts_openai.py; exec bash"
        ;;
    3)
        echo "Launching KoboldCCP Version..."
        $TERMINAL "python3 guts_llm.py; exec bash"
        ;;
    [Qq])
        echo "Quitting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo "Launching Guts..."
$TERMINAL "python3 guts.py; exec bash"
