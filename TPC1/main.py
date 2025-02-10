import sys

def on_off(file):

    flag = True
    sum = 0
    i = 0    
    
    input_file = open(file, "r")
    input = input_file.read().upper()

    while i < len(input):
        if input[i] == "O":
            if input[i + 1 : i + 3] == "FF":
                flag = False
                i += 2
            elif input[i + 1] == "N":
                flag = True
                i += 1
        elif input[i] == "=":
            print(sum)
        elif flag and input[i].isdigit():
            sum += int(input[i])
        i += 1

    print("Final Sum: ", sum)


if __name__ == "__main__":
    file = sys.argv[1]
    on_off(file)