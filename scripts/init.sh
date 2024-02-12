if ! grep -q "# DEVCONTAINER HOUSING-GPT INIT" ~/.bashrc; then
    echo "Initializing..."
    echo "# DEVCONTAINER HOUSING-GPT INIT #" >> ~/.bashrc;
    echo "export USER_NAME=$(id -un)" >> ~/.bashrc;
    echo "export USER_ID=$(id -u)" >> ~/.bashrc;
    echo "export USER_GID=$(id -g)" >> ~/.bashrc;
    echo "export USER_GNAME=$(id -gn)" >> ~/.bashrc;
fi
echo "Initialization complete..."
