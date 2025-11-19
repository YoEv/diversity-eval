#!/bin/bash

# LLark Environment Management Script

case "$1" in
    "activate")
        echo "Activating LLark conda environment..."
        eval "$(conda shell.bash hook)"
        conda activate llark
        echo "LLark environment activated. Use 'conda deactivate' to exit."
        ;;
    "deactivate")
        echo "Deactivating conda environment..."
        conda deactivate
        ;;
    "list")
        echo "Available conda environments:"
        conda env list
        ;;
    "remove")
        echo "Removing LLark conda environment..."
        conda env remove -n llark -y
        echo "LLark environment removed."
        ;;
    "info")
        echo "LLark Environment Information:"
        conda env list | grep llark || echo "LLark environment not found"
        if conda env list | grep -q llark; then
            echo ""
            echo "Installed packages:"
            conda activate llark
            pip list | grep -E "(torch|transformers|librosa|music)"
            conda deactivate
        fi
        ;;
    "jupyter")
        echo "Starting Jupyter notebook in LLark environment..."
        eval "$(conda shell.bash hook)"
        conda activate llark
        cd /home/hice1/xli3252/Desktop/diversity-eval/external/llark
        jupyter notebook
        ;;
    *)
        echo "LLark Environment Management"
        echo "Usage: $0 {activate|deactivate|list|remove|info|jupyter}"
        echo ""
        echo "Commands:"
        echo "  activate    - Activate LLark conda environment"
        echo "  deactivate  - Deactivate current conda environment"
        echo "  list        - List all conda environments"
        echo "  remove      - Remove LLark conda environment"
        echo "  info        - Show LLark environment information"
        echo "  jupyter     - Start Jupyter notebook in LLark environment"
        ;;
esac
