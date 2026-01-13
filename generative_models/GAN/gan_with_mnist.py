from __future__ import print_function
import argparse
import torch
import torch.utils.data
from torch import nn, optim
from torchvision import datasets, transforms
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='VAE MNIST Example')
parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                    help='input batch size for training (default: 128)')
parser.add_argument('--epochs', type=int, default=50, metavar='N',
                    help='number of epochs to train (default: 100)')
parser.add_argument('--no-accel', action='store_true', 
                    help='disables accelerator (default: True)')
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                    help='how many batches to wait before logging training status')
args = parser.parse_args()

use_accel = not args.no_accel and torch.accelerator.is_available()

torch.manual_seed(args.seed)


if use_accel:
    device = torch.accelerator.current_accelerator()
else:
    device = torch.device("cpu")

print(f"Using device: {device}")

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

kwargs = {'num_workers': 1, 'pin_memory': True} if use_accel else {}
train_loader = torch.utils.data.DataLoader(
    datasets.MNIST('./data', train=True, download=True, transform=transform),
    batch_size=args.batch_size, shuffle=True, drop_last=True, **kwargs)
test_loader = torch.utils.data.DataLoader(
    datasets.MNIST('./data', train=False, transform=transform),
    batch_size=args.batch_size, shuffle=False, drop_last=True, **kwargs)

Z_DIM, IMAGE_DIM, HIDDEN_DIM = 100, 28**2, 256
LR, BETA1, BETA2 = 0.0002, 0.5, 0.999

class Generator(nn.Module):
    def __init__(self, z_dim, img_dim, hidden_dim):
        super().__init__()

        self.linear1 = nn.Linear(z_dim, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, hidden_dim * 2)
        self.linear3 = nn.Linear(hidden_dim * 2, img_dim)
        self.leaky_relu = nn.LeakyReLU(0.2)
        self.tanh = nn.Tanh()
    
    def forward(self, x):
        x = self.leaky_relu(self.linear1(x))
        x = self.leaky_relu(self.linear2(x))
        x = self.tanh(self.linear3(x))
        return x.view(-1, 1, 28, 28)    # (N, 784) => (N, 1, 28, 28)

class Discriminator(nn.Module):
    def __init__(self, img_dim, hidden_dim):
        super().__init__()
        self.img_dim = img_dim

        self.linear1 = nn.Linear(img_dim, hidden_dim * 2)
        self.linear2 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.linear3 = nn.Linear(hidden_dim, 1)
        self.leaky_relu = nn.LeakyReLU(0.2)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = x.view(-1, self.img_dim)    # (N, 1, 28, 28) => (N, 784)
        x = self.leaky_relu(self.linear1(x))
        x = self.leaky_relu(self.linear2(x))
        x = self.sigmoid(self.linear3(x))
        return x

G = Generator(Z_DIM, IMAGE_DIM, HIDDEN_DIM).to(device)
D = Discriminator(IMAGE_DIM, HIDDEN_DIM).to(device)

criterion = nn.BCELoss()
G_optimizer = optim.Adam(G.parameters(), lr=LR, betas=(BETA1, BETA2))
D_optimizer = optim.Adam(D.parameters(), lr=LR, betas=(BETA1, BETA2))

fixed_noise = torch.randn(64, Z_DIM).to(device)

def train(epoch):
    G.train(); D.train()

    for batch_idx, (real_imgs, _) in enumerate(train_loader):
        real_imgs = real_imgs.to(device)

        noise = torch.randn(args.batch_size, Z_DIM).to(device)

        real_labels = torch.ones(args.batch_size, 1).to(device)
        fake_labels = torch.zeros(args.batch_size, 1).to(device)

        # ---------------------------
        # (1) Discriminator Training
        # ---------------------------
        D_optimizer.zero_grad()
        D_real = D(real_imgs)
        d_real_loss = criterion(D_real, real_labels)

        fake_imgs = G(noise).detach()   # G의 기울기 계산 방지 
        D_fake = D(fake_imgs)
        d_fake_loss = criterion(D_fake, fake_labels)

        d_loss = (d_real_loss + d_fake_loss) / 2
        d_loss.backward()
        D_optimizer.step()

        # ---------------------------
        # (2) Generator Training
        # ---------------------------
        G_optimizer.zero_grad()
        fake_imgs = G(noise)
        D_output = D(fake_imgs)
        g_loss = criterion(D_output, real_labels)
        g_loss.backward()
        G_optimizer.step()

        if batch_idx % args.log_interval == 0:
            print(
                f"Epoch [{epoch+1}/{args.epochs}] Batch [{batch_idx+1}/{len(train_loader)}]"
                f"D Loss: {d_loss.item():.4f}, G Loss: {g_loss.item():.4f}"
            )

if __name__ == "__main__":
    import os
    ROOT_DIR = r"./GAN/results/MNIST/"

    for epoch in range(1, args.epochs + 1):
        train(epoch)
        G.eval()
        with torch.no_grad():
            fake_imgs = G(fixed_noise).cpu().detach()

            if (epoch+1) % 10 == 0:
                fig, axes = plt.subplots(4, 4, figsize=(10, 10))
                for i, ax in enumerate(axes.flat):
                    if i < fake_imgs.size(0):
                        img = fake_imgs[i].view(28, 28)
                        ax.imshow(img, cmap='gray')
                        ax.axis('off')
                plt.savefig(os.path.join(ROOT_DIR, f"sample_{str(epoch)}.png"))
                plt.close(fig)