import socket

# 서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('127.0.0.1', 8080))   => 1대 pc로 소켓 통신할 경우
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(1)
print("서버가 클라이언트의 연결 요청을 기다리고 있습니다.")

# 클라이언트의 연결 요청 수락
connection, address = server_socket.accept()
print(f"클라이언트 {address}가 연결되었습니다.")

# 데이터 수신 및 응답
data = connection.recv(1024)
print(f"클라이언트로부터 받은 데이터: {data.decode()}")
connection.sendall(b'Hello, Client!')

# 소켓 종료
connection.close()
server_socket.close()