import torch
import torch.nn as nn
from flask import Flask, request, jsonify
from PIL import Image
from torchvision import transforms
import io

from models.mlp import MLP

# Flask 앱 초기화
app = Flask(__name__)

device = torch.device("cpu") # Server 환경에 맞춰 CPU 사용

model = MLP(input_dim=784, hidden_dim=256, num_classes=10).to(device) 
model.load_state_dict(torch.load('./model_params/mlp_mnist.pth', map_location=device))
model.eval()

preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

# 예측 API 엔드포인트
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    try:
        image = Image.open(io.BytesIO(image_file.read()))
        image_tensor = preprocess(image).unsqueeze(0)

        with torch.no_grad():
            output = model(image_tensor)
            _, predicted = torch.max(output.data, 1)
            result = predicted.item()

        return jsonify({'prediction': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # debug=True는 개발용
    # 배포 시에는 False로 설정.
    app.run(debug=True, port=5000)