class Logger:
    # [SC] static variables
    printConsole = True

    # [SC] types of messages
    ERROR_TYPE = "ERROR"
    WARNING_TYPE = "WARNING"
    INFO_TYPE = "INFO"

    # [SC] Custom static printing method.
    # @param    string  type    Message type (ERROR, WARNING, INFO, etc).
    # @param    string  method  Name of the method that call this method.
    # @param    string  msg     Message to be printed.
    # @return   void
    @staticmethod
    def cPrint(type, method, msg):
        if Logger.printConsole:
            print(f"\n{type}:: {method}:: {msg}")