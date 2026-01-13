import sys

def main():
    # sys.argv[0]는 script file의 이름이므로, 실제 인수는 sys.argv[1:]에 저장된다
    args = sys.argv[1:]
    
    sum_ = 0

    # 인수가 하나 이상일 경우 출력
    if len(args) >= 0:
        for arg in args:
            sum_ += int(arg)
            print(arg)
    else:
        print("No arguments were provided.")
    
    print(f"\nsum = {sum_}\n")

if __name__ == "__main__":
    main()