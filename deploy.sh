#!/bin/bash

echo "🚀 ULTIMATE DEPLOYMENT SCRIPT"
echo "=============================="

# Build Docker image
echo "📦 Building Docker image..."
docker build -t ultimate-analyzer .

# Deploy to different platforms
echo "🌐 Choose deployment platform:"
echo "1) Local Docker"
echo "2) Heroku"
echo "3) AWS ECS"
echo "4) Google Cloud Run"
echo "5) Azure Container Instances"

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "🐳 Starting local Docker container..."
        docker run -p 8501:8501 ultimate-analyzer
        ;;
    2)
        echo "🚀 Deploying to Heroku..."
        heroku container:push web -a ultimate-analyzer
        heroku container:release web -a ultimate-analyzer
        ;;
    3)
        echo "☁️ Deploying to AWS ECS..."
        aws ecs create-service --cluster ultimate-cluster --service-name ultimate-analyzer
        ;;
    4)
        echo "🌟 Deploying to Google Cloud Run..."
        gcloud run deploy ultimate-analyzer --image gcr.io/PROJECT/ultimate-analyzer
        ;;
    5)
        echo "🔷 Deploying to Azure..."
        az container create --resource-group ultimate-rg --name ultimate-analyzer
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac

echo "✅ Deployment complete!"
echo "🌐 Access your app at the provided URL"