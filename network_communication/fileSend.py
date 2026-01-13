import socket

# 클라이언트 소켓 설정
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8080))
print("서버에 연결되었습니다.")

# 파일 전송 /home/hyunjong/pythonwork
with open('/home/hyunjong/pythonwork/sendfile.txt', 'rb') as f:
    print("파일 전송 중...")
    while True:
        data = f.read(1024)
        if not data:
            break
        client_socket.sendall(data)

print("파일 전송 완료")

# 소켓 종료
client_socket.close()