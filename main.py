import chira

if __name__ == '__main__':
    interpreter = chira.Interpreter(print)
    print("Chira v0.0.1\n============\n")
    text = ""
    while text != "quit":
        text = str(input("> "))
        if len(text.split(" ")) >= 2 and text.split(" ")[0] == "load":
            interpreter.parse_file(chira.list_to_str(text.replace("\"", "").split(" ")[1:]))
        else:
            interpreter.parse(text)
