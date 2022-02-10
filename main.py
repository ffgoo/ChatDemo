import socketserver
import threading


# 서버의 ip를 열음. ( 이 서버의 아이피로 클라이언트가 접속을 해야한다) 그전에 핑 확인 필요
HOST = '127.0.0.1'
#포트번호
PORT = 9009
# syncronized 동기화 진행하는 스레드 생성
lock = threading.Lock()


#사용자 관리 및 채팅 메세지 전송을 담당하는 클래스
#1. 채팅 서버로 입장한 사용자의 등록
#2. 채팅을 종료하는 사용자의 퇴장 관리
#3. 사용자가 입장하고 퇴장하는 관리
#4. 사용자가 입력한 메세지를 채팅 서버에 접속한 모두에게 전송
class UserManager :

    def __init__(self):
        # 사용자의 등록 정보를 담을 Dictionary { 사용자 이름 : (소켓, 주소 )... }
        self.users= {}


    # 사용자 ID 를 self.users 에 추가하는 함수
    def addUser(self,username, conn, addr):

        #이미 등록된 사용자일때
        if username in self.users:
            conn.send('이미 등록되어있습니다.')
            return None
        # 새로운 사용자 등록하기
        lock.acquire()
        self.users[username] = (conn,addr)
        #업데이트 후 락 해제
        lock.release()

        self.sendMessageToAll('[%s]님이 입장했습니다'%username)
        print('+++대화 참여자수 [%d]'%len(self.users))

        return username

    #사용자 제거
    def removeUser(self,username):
        if username not in self.users:
            return
        lock.acquire()
        del self.users[username]
        lock.release()

        self.sendMessageToAll('[%s]님이 퇴장했습니다.'%username)
        print('---대화 참여자 수 [%d]' %len(self.users))


    #전송한 msg를 처리하는 부분
    def messageHandler(self,username,msg):
        #보낸 메싲지의 첫문자가 / 가 아니면
        if msg[0] != '/':
            self.sendMessageToAll('[%s] %s'%(username, msg))
            return

        #보낸 메시지가 /quit 이면
        if msg.strip() == '/quit':
            self.removeUser(username)
            return -1

    def sendMessageToAll(self,msg):
        for conn, addr in self.users.values():
            conn.send(msg.encode())

class MyTcpHandler(socketserver.BaseRequestHandler):
    userman = UserManager()

    #클라이언트가 접속시 클라이언트 주소 출력
    def handle(self):
        print('[%s] 연결됨' % self.client_address[0])

        try:
            username = self.registerUsername()
            msg = self.request.recv(1024)
            while msg :
                print(msg.decode())
                if self.userman.messageHandler(username,msg.decode()) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)
        except Exception as e :
            print(e)

        print('[%s] 접속종료' %self.client_address[0])
        self.userman.removeUser(username)
    def registerUsername(self):
        while True:
            self.request.send('로그인 ID:'.encode())
            username = self.request.recv(1024)
            username = username.decode().strip()
            if self.userman.addUser(username,self.request,self.client_address):
                return username

class ChatingServer(socketserver.ThreadingMixIn,socketserver.TCPServer):
    pass

def runServer():
    print('+++채팅 서버를 시작합니다.')
    print('+++ㅊㅐ팅 서버를 끝내려면 컨트롤 씨')

    try:
        server = ChatingServer((HOST,PORT),MyTcpHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('---채팅서버를 종료합니다.')
        server.shutdown()
        server.server_close()

runServer()
