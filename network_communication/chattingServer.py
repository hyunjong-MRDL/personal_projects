import socket

""" Python 실행 프로그램(.exe) 만들기 """
# $ pip install pyinstaller
# $ pyinstaller --onefile chattingServer.py (실행 파일 만들기)
# $ chmod +x dist/chattingServer    (실행 권한 부여)
# $ ./dist/chattingServer

def server_program():
    host = "0.0.0.0"        #  서버 IP 주소 (localhost)
    port = 12345            #  서버 포트 번호

    # 서버 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))    # 서버 소켓 바인딩
    server_socket.listen(1)             # 연결 대기

    print(f"Server is listening on {host}:{port}...")
    conn, addr = server_socket.accept() # 클라이언트 연결 수락
    print(f"Connection from {addr} established!")

    # 채팅 시작
    while True:
        # 클라이언트 메시지 수신
        client_message = conn.recv(1024).decode()
        if client_message.lower() == "bye":
            print("Client disconnected.")
            break
        print(f"Client: {client_message}")

        # 서버 메시지 전송
        server_message = input("You: ")
        conn.send(server_message.encode())
        if server_message.lower() == "bye":
            print("Closing connection.")
            break

    conn.close()    # 연결 닫기
    server_socket.close()

if __name__ == "__main__":
    server_program()