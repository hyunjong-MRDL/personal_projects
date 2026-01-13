from __future__ import print_function
import argparse
import torch
import torch.utils.data
from torch import nn, optim
from torch.nn import functional as F
from torchvision import transforms
from torchvision.utils import save_image
from PIL import Image
import cv2
from pathlib import Path
import numpy as np
from torch.amp import autocast, GradScaler


parser = argparse.ArgumentParser(description='Medical Data Augmentation using VAE')
parser.add_argument('--batch-size', type=int, default=16, metavar='N',
                    help='input batch size for training (default: 1)')
parser.add_argument('--epochs', type=int, default=10, metavar='N',
                    help='number of epochs to train (default: 10)')
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


class ChestXRay(torch.utils.data.Dataset):
    def __init__(self, data_paths, labels):
        super().__init__()
        self.paths = data_paths
        self.labels = labels
        self.transform = transforms.Compose([
            transforms.Resize((64, 64)),
            transforms.ToTensor()
        ])
    
    def __len__(self):
        return len(self.paths)
    
    def __getitem__(self, index):
        datapath = self.paths[index]
        img = cv2.imread(datapath, cv2.IMREAD_GRAYSCALE)
        if self.transform is not None:
            image = self.transform(Image.fromarray(img))
        label = torch.from_numpy(self.labels[index])

        return image, label
    
root_dir = Path(r"/home/hyunjong/data/chest_xray")
if root_dir.exists() and root_dir.is_dir():
    NORMAL_dir = root_dir / "NORMAL"
    NORMAL = [N_path.absolute() for N_path in NORMAL_dir.iterdir() if N_path.is_file()]
    PNEUMONIA_dir = root_dir / "PNEUMONIA"
    PNEUMONIA = [P_path.absolute() for P_path in PNEUMONIA_dir.iterdir() if P_path.is_file()]
else:
    print("Failed to read data.")

train_dataset = ChestXRay(NORMAL[:100], np.array([[1,0] for _ in range(100)])) + ChestXRay(PNEUMONIA[:100], np.array([[0,1] for _ in range(100)]))
test_dataset = ChestXRay(NORMAL[100:150], np.array([[1,0] for _ in range(50)])) + ChestXRay(PNEUMONIA[100:150], np.array([[0,1] for _ in range(50)]))


# what is 'pin_memory'?
kwargs = {'num_workers': 1, 'pin_memory': False} if use_accel else {}

train_loader = torch.utils.data.DataLoader(
    dataset=train_dataset,
    batch_size=args.batch_size, shuffle=True, **kwargs)
test_loader = torch.utils.data.DataLoader(
    dataset=test_dataset,
    batch_size=args.batch_size, shuffle=False, **kwargs)


class VAE(nn.Module):
    def __init__(self):
        super(VAE, self).__init__()
        self.fc1 = nn.Linear(64**2, 400)
        self.fc21 = nn.Linear(400, 20)
        self.fc22 = nn.Linear(400, 20)
        self.fc3 = nn.Linear(20, 400)
        self.fc4 = nn.Linear(400, 64**2)

    def encode(self, x):
        h1 = F.relu((self.fc1(x)))
        return self.fc21(h1), self.fc22(h1)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5*logvar)
        eps = torch.randn_like(std)
        return mu + eps*std

    def decode(self, z):
        h3 = F.relu((self.fc3(z)))
        return torch.sigmoid(self.fc4(h3))

    def forward(self, x):
        mu, logvar = self.encode(x.view(-1, 64**2))
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar


model = VAE().to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)


# Reconstruction + KL divergence losses summed over all elements and batch
def loss_function(recon_x, x, mu, logvar):
    # BCE = F.binary_cross_entropy(recon_x, x.view(-1, 128**2), reduction='sum')
    BCE = nn.BCEWithLogitsLoss()(recon_x, x.view(-1, 64**2))
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return BCE + KLD


def train(epoch):
    scaler = GradScaler()   # what is grad_scaler?

    model.train()
    train_loss = 0
    for batch_idx, (data, _) in enumerate(train_loader):
        optimizer.zero_grad()
        with autocast("cuda"):
            data = data.to(device)
            optimizer.zero_grad()
            recon_batch, mu, logvar = model(data)
            loss = loss_function(recon_batch, data, mu, logvar)
            scaler.scale(loss).backward()
            train_loss += loss.item()
            scaler.step(optimizer)
            scaler.update()
            if batch_idx % args.log_interval == 0:
                print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                    epoch, batch_idx * len(data), len(train_loader.dataset),
                    100. * batch_idx / len(train_loader),
                    loss.item() / len(data)))

    print('====> Epoch: {} Average loss: {:.4f}'.format(
          epoch, train_loss / len(train_loader.dataset)))


def test(epoch):
    model.eval()
    test_loss = 0
    with torch.no_grad():
        for i, (data, _) in enumerate(test_loader):
            data = data.to(device)
            recon_batch, mu, logvar = model(data)
            test_loss += loss_function(recon_batch, data, mu, logvar).item()
            if i == 0:
                n = min(data.size(0), 8)
                comparison = torch.cat([data[:n],
                                      recon_batch.view(args.batch_size, 1, 64, 64)[:n]])
                save_image(comparison.cpu(),
                         './VAE/results/ChestXRay/reconstruction_' + str(epoch) + '.png', nrow=n)

    test_loss /= len(test_loader.dataset)
    print('====> Test set loss: {:.4f}'.format(test_loss))


if __name__ == "__main__":
    for epoch in range(1, args.epochs + 1):
        train(epoch)
        test(epoch)
        with torch.no_grad():
            sample = torch.randn(64, 20).to(device)
            sample = model.decode(sample).cpu()
            save_image(sample.view(64, 1, 64, 64),
                       './VAE/results/ChestXRay/sample_' + str(epoch) + '.png')