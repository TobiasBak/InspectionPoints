from RobotControl.RobotControl import send_command_interpreter_socket


def test():
    commands = [
        'sec secondaryProgram(): set_digital_out(1,True) end',
        'secp = run secondaryProgram()',
        'movej([0,0,0,0,0,0], a=0.1, v=0.1)'
    ]

    for command in commands:
        send_command_interpreter_socket(command)



if __name__ == '__main__':
    test()
