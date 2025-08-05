#!/bin/bash

# CareMuse + Mnemo Setup Script
# This script helps set up the development environment

set -e

echo "🧠 CareMuse + Mnemo Setup Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
        return 0
    else
        print_error "Docker is not installed. Please install Docker first."
        return 1
    fi
}

# Check if Docker Compose is installed
check_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        print_success "Docker Compose is available"
        return 0
    else
        print_error "Docker Compose is not available. Please install Docker Compose."
        return 1
    fi
}

# Check Python installation
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION is installed"
        return 0
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        return 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p backend/data
    mkdir -p frontend/static
    mkdir -p logs
    
    print_success "Directories created"
}

# Setup Python virtual environment for local development
setup_venv() {
    if [ "$1" = "--local" ]; then
        print_status "Setting up Python virtual environment for local development..."
        
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            print_success "Virtual environment created"
        fi
        
        source venv/bin/activate
        
        print_status "Installing backend dependencies..."
        pip install -r backend/requirements.txt
        
        print_status "Installing frontend dependencies..."
        pip install -r frontend/requirements.txt
        
        print_success "Dependencies installed"
        
        # Create a simple activation script
        cat > activate_env.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
echo "Virtual environment activated!"
echo "To run the backend: cd backend && python app.py"
echo "To run the frontend: cd frontend && streamlit run pages/home.py"
EOF
        chmod +x activate_env.sh
        
        print_success "Created activation script: ./activate_env.sh"
    fi
}

# Setup Ollama
setup_ollama() {
    if [ "$1" = "--local" ]; then
        print_status "Checking for Ollama installation..."
        
        if command -v ollama &> /dev/null; then
            print_success "Ollama is installed"
            
            print_status "Pulling Mistral model..."
            ollama pull mistral
            
            print_success "Mistral model ready"
        else
            print_warning "Ollama not found. Please install Ollama manually:"
            echo "  curl -fsSL https://ollama.ai/install.sh | sh"
            echo "  ollama pull mistral"
        fi
    else
        print_status "Ollama will be set up via Docker"
    fi
}

# Build and start Docker services
start_docker() {
    print_status "Building and starting Docker services..."
    
    docker-compose build
    docker-compose up -d
    
    print_success "Services started!"
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Pull Mistral model in Ollama container
    print_status "Setting up Mistral model in Ollama container..."
    docker-compose exec ollama ollama pull mistral
    
    print_success "Setup complete!"
    
    echo ""
    echo "🎉 CareMuse + Mnemo is now running!"
    echo "   Frontend: http://localhost:8501"
    echo "   Backend API: http://localhost:8000"
    echo "   Ollama: http://localhost:11434"
    echo ""
    echo "To stop the services: docker-compose down"
    echo "To view logs: docker-compose logs -f"
}

# Main setup function
main() {
    echo ""
    print_status "Starting setup process..."
    
    # Parse arguments
    LOCAL_SETUP=false
    DOCKER_SETUP=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --local)
                LOCAL_SETUP=true
                DOCKER_SETUP=false
                shift
                ;;
            --docker)
                DOCKER_SETUP=true
                LOCAL_SETUP=false
                shift
                ;;
            --help)
                echo "Usage: $0 [--local|--docker]"
                echo ""
                echo "Options:"
                echo "  --local   Set up for local development (requires Python, Ollama)"
                echo "  --docker  Set up using Docker (default)"
                echo "  --help    Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Create directories
    create_directories
    
    if [ "$LOCAL_SETUP" = true ]; then
        print_status "Setting up for local development..."
        
        check_python || exit 1
        setup_venv --local
        setup_ollama --local
        
        print_success "Local setup complete!"
        echo ""
        echo "🎉 Development environment ready!"
        echo ""
        echo "To start development:"
        echo "  1. Activate environment: source ./activate_env.sh"
        echo "  2. Start backend: cd backend && python app.py"
        echo "  3. Start frontend: cd frontend && streamlit run pages/home.py"
        echo ""
        
    elif [ "$DOCKER_SETUP" = true ]; then
        print_status "Setting up with Docker..."
        
        check_docker || exit 1
        check_docker_compose || exit 1
        start_docker
    fi
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi