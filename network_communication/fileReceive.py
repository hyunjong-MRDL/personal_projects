import socket

# 서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8080))   # Receiving인 경우 Server로 Listening함
server_socket.listen(1)
print("서버가 클라이언트의 연결 요청을 기다리고 있습니다.")

# 클라이언트의 연결 요청 수락
connection, address = server_socket.accept()
print(f"클라이언트 {address}가 연결되었습니다.")

# 파일 수신
with open('received_file.sh', 'wb') as f:
    print("파일 수신 중...")
    while True:
        data = connection.recv(1024)
        if not data:
            break
        f.write(data)

print("데이터 수신 완료")

# 소켓 종료
connection.close()
server_socket.close()