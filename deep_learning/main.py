import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

from models.mlp import MLP
from utils.train_utils import train_epoch, evaluate_epoch

def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() and args.use_cuda else "cpu")
    print(f"Using device: {device}")

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    train_dataset = datasets.MNIST(root=args.data_path, train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST(root=args.data_path, train=False, download=True, transform=transform)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)

    model = MLP(input_dim=784, hidden_dim=args.hidden_dim, num_classes=10).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    print("\nStarting training...")
    for epoch in range(args.epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        eval_loss, eval_acc = evaluate_epoch(model, test_loader, criterion, device)
        
        print(f"Epoch {epoch+1}/{args.epochs}")
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
        print(f"Test Loss: {eval_loss:.4f}, Test Acc: {eval_acc:.4f}")
    
    print("\nTraining complete.")
    model_save_path = "./model_params/mlp_mnist.pth"
    torch.save(model.state_dict(), model_save_path)
    print(f"Model saved to {model_save_path}")

    final_test_loss, final_test_acc = evaluate_epoch(model, test_loader, criterion, device)
    print(f"\nFinal Test Loss: {final_test_loss:.4f}, Final Test Accuracy: {final_test_acc:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MNIST MLP Classifier")

    parser.add_argument('--epochs', type=int, default=5, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size for training')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--hidden_dim', type=int, default=256, help='Dimension of hidden layers')

    parser.add_argument('--data_path', type=str, default='./data', help='Path to MNIST dataset')
    parser.add_argument('--use_cuda', action='store_true', help='Use CUDA for training if available')
    
    args = parser.parse_args()
    
    main(args)