from antlr4 import *
from openunderstand.gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from openunderstand.gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
from openunderstand.gen.javaLabeled.JavaLexer import JavaLexer
import argparse
import os

class Interface:
    def __init__(self, name, numberOfLines, numberOfBlankLines, numberOfCommentLines, numberOfCodeLines, startLine, endLine):
        self.startLine = startLine
        self.endLine = endLine
        self.interfaceName = name
        self.numberOfLines = numberOfLines
        self.numbderOfBlankLines = numberOfBlankLines
        self.numberOfCommentLines = numberOfCommentLines
        self.numberOfCodeLines = numberOfCodeLines

class Class:
    def __init__(self, name, numberOfLines, numberOfBlankLines, numberOfCommentLines, numberOfCodeLines, startLine, endLine):
        self.startLine = startLine
        self.endLine = endLine
        self.className = name
        self.numberOfLines = numberOfLines
        self.numbderOfBlankLines = numberOfBlankLines
        self.numberOfCommentLines = numberOfCommentLines
        self.numberOfCodeLines = numberOfCodeLines


class Method:
    def __init__(self, name, numberOfLines, numberOfBlankLines, numberOfCommentLines, numberOfCodeLines, startLine, endLine):
        self.startLine = startLine
        self.endLine = endLine
        self.methodName = name
        self.numberOfLines = numberOfLines
        self.numbderOfBlankLines = numberOfBlankLines
        self.numberOfCommentLines = numberOfCommentLines
        self.numberOfCodeLines = numberOfCodeLines

class ClassLineListener(JavaParserLabeledListener):
    def __init__(self):
        self.classes = []
    def enterClassDeclaration(self, ctx:JavaParserLabeled.ClassDeclarationContext):
        [FirstLine, col] = str(ctx.start).split(",")[3].split(":")
        col = col[:-1]
        FirstLineNum = int(FirstLine)
        newClass = Class(ctx.IDENTIFIER().getText(),
                           FirstLineNum, 0, 0, 0, FirstLineNum, FirstLineNum)
        self.classes.append(newClass)

    def exitClassBody(self, ctx:JavaParserLabeled.ClassBodyContext):
        for m in self.classes:
            if m.className == ctx.parentCtx.IDENTIFIER().getText():
                [LastLine, col] = str(ctx.stop).split(",")[3].split(":")
                col = col[:-1]
                LastLineNum = int(LastLine)
                m.numberOfLines = LastLineNum - m.numberOfLines
                m.endLine = LastLineNum


class InterfaceListener(JavaParserLabeledListener):
    def __init__(self):
        self.interfaces = []
    def enterInterfaceDeclaration(self, ctx:JavaParserLabeled.InterfaceDeclarationContext):
        [FirstLine, col] = str(ctx.start).split(",")[3].split(":")
        col = col[:-1]
        FirstLineNum = int(FirstLine)
        newInterface = Interface(ctx.IDENTIFIER().getText(),
                           FirstLineNum, 0, 0, 0, FirstLineNum, FirstLineNum)
        self.interfaces.append(newInterface)

    def exitInterfaceBody(self, ctx:JavaParserLabeled.InterfaceBodyContext):
        for m in self.interfaces:
            if m.interfaceName == ctx.parentCtx.IDENTIFIER().getText():
                [LastLine, col] = str(ctx.stop).split(",")[3].split(":")
                col = col[:-1]
                LastLineNum = int(LastLine)
                m.numberOfLines = LastLineNum - m.numberOfLines
                m.endLine = LastLineNum

class FunctionsLineListener(JavaParserLabeledListener):
    def __init__(self):
        self.methods = []

    def enterMethodDeclaration(self, ctx: JavaParserLabeled.MethodDeclarationContext):
        [FirstLine, col] = str(ctx.start).split(",")[3].split(":")
        col = col[:-1]
        FirstLineNum = int(FirstLine)
        newMethod = Method(ctx.IDENTIFIER().getText(),
                           FirstLineNum, 0, 0, 0, FirstLineNum, FirstLineNum)
        self.methods.append(newMethod)

    def exitMethodBody(self, ctx: JavaParserLabeled.MethodBodyContext):
        for m in self.methods:
            if m.methodName == ctx.parentCtx.IDENTIFIER().getText():
                [LastLine, col] = str(ctx.stop).split(",")[3].split(":")
                col = col[:-1]
                LastLineNum = int(LastLine)
                m.numberOfLines = LastLineNum - m.numberOfLines
                m.endLine = LastLineNum


def avgMethodsLineNumbers(file_path):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)
    parseTree = parser.compilationUnit()

    listener = FunctionsLineListener()
    walker = ParseTreeWalker()
    walker.walk(listener, parseTree)

    methods = listener.methods

    SumOfMethodsLines = 0
    for method in methods:
        SumOfMethodsLines = SumOfMethodsLines + method.numberOfLines
    avgMethodsLines = SumOfMethodsLines / len(methods)
    print("avg number of lines of functions :" + str(avgMethodsLines))

    return methods


def avgMethodCommentLines(file_path, methods):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)

    for method in methods:
        token = lexer.nextToken()
        while token.line <= method.endLine:
            if token.line >= method.startLine and token.line <= method.endLine:
                if token.type == lexer.LINE_COMMENT:
                    method.numberOfCommentLines = method.numberOfCommentLines + 1
            token = lexer.nextToken()

    SumOfMethodsCommentLines = 0
    for method in methods:
        SumOfMethodsCommentLines = SumOfMethodsCommentLines + method.numberOfCommentLines
    avgMethodsCommentsLines = SumOfMethodsCommentLines / len(methods)

    print("avg number of line comments lines of functions :" +
          str(avgMethodsCommentsLines))


def avgMethodCommentBlockLines(file_path, methods):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)
    for method in methods:
        token = lexer.nextToken()
        while token.line <= method.endLine:
            if token.line >= method.startLine and token.line <= method.endLine:
                if token.type == lexer.COMMENT:
                    commentBlockStartLine = token.line
                    token = lexer.nextToken()
                    endLine = token.line
                    method.numberOfCommentLines = method.numberOfCommentLines + (endLine - commentBlockStartLine) + 1

            token = lexer.nextToken()

    SumOfMethodsCommentLines = 0
    for method in methods:
        SumOfMethodsCommentLines = SumOfMethodsCommentLines + method.numberOfCommentLines
    avgMethodsCommentsLines = SumOfMethodsCommentLines / len(methods)
    print("avg number of comments lines of functions (block and line) :" +
          str(avgMethodsCommentsLines))


def avgMethodBlankLines(file_path, methods):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)

    notBlankRaws = []
    for method in methods:
        token = lexer.nextToken()
        while token.line < method.startLine:
            token = lexer.nextToken()

        while token.line <= method.endLine:
            if token.type == lexer.COMMENT:
                startLine = token.line
                token = lexer.nextToken()
                endLine = token.line
                for i in range (startLine , endLine):
                    notBlankRaws.append(i)
                notBlankRaws.append(endLine)
            else:
                token = lexer.nextToken()
                notBlankRaws.append(token.line)

        BlankLines = []
        for line in range(method.startLine, method.endLine):
            if not (line in notBlankRaws):
                BlankLines.append(line)

        method.numbderOfBlankLines = len(BlankLines)

    SumOfBlankLines = 0
    for method in methods:
        SumOfBlankLines = SumOfBlankLines + method.numbderOfBlankLines

    avgMethodBlankLinesNumber = SumOfBlankLines/len(methods)

    print("avg number of blank lines of functions : " +
          str(avgMethodBlankLinesNumber))


def avgMethodCodeLines(file_path, methods):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)

    for method in methods:
        token = lexer.nextToken()
        last_line = token.line
        while token.line <= method.endLine:
            if token.line >= method.startLine and token.line <= method.endLine:
                while token.line == last_line:
                    token = lexer.nextToken()
                last_line = token.line

                if token.type == lexer.COMMENT:
                    token = lexer.nextToken()
                    if not token.type == 108:
                        method.numberOfCodeLines = method.numberOfCodeLines +1
                else:
                    if not token.type == lexer.LINE_COMMENT:
                        method.numberOfCodeLines = method.numberOfCodeLines + 1

            token = lexer.nextToken()
        method.numberOfCodeLines = method.numberOfCodeLines - 1

    SumOfMethodsCodeLines = 0
    for method in methods:
        SumOfMethodsCodeLines = SumOfMethodsCodeLines + method.numberOfCodeLines
    SumOfMethodsCodeLines = SumOfMethodsCodeLines - 1
    avgMethodsCodeLines = SumOfMethodsCodeLines / len(methods)

    print("avg number of code lines of functions :" + str(avgMethodsCodeLines))


def avgClassesLineNumbers(file_path):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)
    parseTree = parser.compilationUnit()

    listener = ClassLineListener()
    walker = ParseTreeWalker()
    walker.walk(listener, parseTree)

    classes = listener.classes

    SumOfLines = 0
    for c in classes:
        SumOfLines = SumOfLines + c.numberOfLines
    avgLines = SumOfLines / len(classes)
    print("avg number of lines of classes :" + str(avgLines))

    return classes


def avgClassCommentLines(file_path, classes):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)

    for c in classes:
        token = lexer.nextToken()
        while token.line < c.endLine:
            if token.line >= c.startLine and token.line < c.endLine:
                if token.type == lexer.LINE_COMMENT:
                    c.numberOfCommentLines = c.numberOfCommentLines + 1
            token = lexer.nextToken()

    SumOfCommentLines = 0
    for c in classes:
        SumOfCommentLines = SumOfCommentLines + c.numberOfCommentLines
    avgCommentsLines = SumOfCommentLines / len(classes)

    print("avg number of line comments lines of classes :" +
          str(avgCommentsLines))


def avgClassCommentBlockLines(file_path, classes):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)
    for c in classes:
        token = lexer.nextToken()
        while token.line < c.endLine:
            if token.line >= c.startLine and token.line < c.endLine:
                if token.type == lexer.COMMENT:
                    commentBlockStartLine = token.line
                    token = lexer.nextToken()
                    endLine = token.line
                    c.numberOfCommentLines = c.numberOfCommentLines + (endLine - commentBlockStartLine) + 1

            token = lexer.nextToken()

    SumOfCommentLines = 0
    for c in classes:
        SumOfCommentLines = SumOfCommentLines + c.numberOfCommentLines
    avgCommentsLines = SumOfCommentLines / len(classes)
    print("avg number of comments lines of classes (block and line) :" +
          str(avgCommentsLines))


def avgClassBlankLines(file_path, classes):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)

    notBlankRaws = []
    for c in classes:
        token = lexer.nextToken()
        while token.line < c.startLine:
            token = lexer.nextToken()

        while token.line < c.endLine:
            if token.type == lexer.COMMENT:
                startLine = token.line
                token = lexer.nextToken()
                endLine = token.line
                for i in range (startLine , endLine):
                    notBlankRaws.append(i)
                notBlankRaws.append(endLine)
            else:
                token = lexer.nextToken()
                notBlankRaws.append(token.line)

        BlankLines = []
        for line in range(c.startLine, c.endLine):
            if not (line in notBlankRaws):
                BlankLines.append(line)

        c.numbderOfBlankLines = len(BlankLines)

    SumOfBlankLines = 0
    for c in classes:
        SumOfBlankLines = SumOfBlankLines + c.numbderOfBlankLines

    avgBlankLinesNumber = SumOfBlankLines/len(classes)

    print("avg number of blank lines of classes : " +
          str(avgBlankLinesNumber))


def avgClassCodeLines(file_path, classes):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)

    for c in classes:
        token = lexer.nextToken()
        last_line = token.line
        while token.line < c.endLine:
            if token.line >= c.startLine and token.line < c.endLine:
                while token.line == last_line:
                    token = lexer.nextToken()
                last_line = token.line

                if token.type == lexer.COMMENT:
                    token = lexer.nextToken()
                    if not token.type == 108:
                        c.numberOfCodeLines = c.numberOfCodeLines +1
                else:
                    if not token.type == lexer.LINE_COMMENT:
                        c.numberOfCodeLines = c.numberOfCodeLines + 1

            token = lexer.nextToken()
        c.numberOfCodeLines += 1

    SumOfCodeLines = 0
    for c in classes:
        SumOfCodeLines = SumOfCodeLines + c.numberOfCodeLines
    SumOfCodeLines = SumOfCodeLines - 1
    avgMethodsCodeLines = SumOfCodeLines / len(classes)

    print("avg number of code lines of classes :" + str(avgMethodsCodeLines))

def avgInterfacesLineNumbers(file_path):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)
    parseTree = parser.compilationUnit()

    listener = InterfaceListener()
    walker = ParseTreeWalker()
    walker.walk(listener, parseTree)

    interfaces = listener.interfaces

    SumOfLines = 0
    for i in interfaces:
        SumOfLines = SumOfLines + i.numberOfLines

    if(len(interfaces) != 0):
        avgLines = SumOfLines / len(interfaces)
        print("avg number of lines of interfaces :" + str(avgLines))
    else:
        "There is not any interface in this file"

    return interfaces


def avgInterfacesCommentLines(file_path, interfaces):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)

    for i in interfaces:
        token = lexer.nextToken()
        while token.line < i.endLine:
            if token.line >= i.startLine and token.line < i.endLine:
                if token.type == lexer.LINE_COMMENT:
                    i.numberOfCommentLines = i.numberOfCommentLines + 1
            token = lexer.nextToken()

    SumOfCommentLines = 0
    for i in interfaces:
        SumOfCommentLines = SumOfCommentLines + i.numberOfCommentLines
    avgCommentsLines = SumOfCommentLines / len(interfaces)

    print("avg number of line comments lines of interfaces :" +
          str(avgCommentsLines))


def avgInterfacesCommentBlockLines(file_path, interfaces):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)
    for i in interfaces:
        token = lexer.nextToken()
        while token.line < i.endLine:
            if token.line >= i.startLine and token.line < i.endLine:
                if token.type == lexer.COMMENT:
                    commentBlockStartLine = token.line
                    token = lexer.nextToken()
                    endLine = token.line
                    i.numberOfCommentLines = i.numberOfCommentLines + (endLine - commentBlockStartLine) + 1

            token = lexer.nextToken()

    SumOfCommentLines = 0
    for i in interfaces:
        SumOfCommentLines = SumOfCommentLines + i.numberOfCommentLines
    avgCommentsLines = SumOfCommentLines / len(interfaces)
    print("avg number of comments lines of interfaces (block and line) :" +
          str(avgCommentsLines))


def avgInterfaceBlankLines(file_path, interfaces):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)

    notBlankRaws = []
    for i in interfaces:
        token = lexer.nextToken()
        while token.line < i.startLine:
            token = lexer.nextToken()

        while token.line <= i.endLine:
            if token.type == lexer.COMMENT:
                startLine = token.line
                token = lexer.nextToken()
                endLine = token.line
                for i in range (startLine , endLine):
                    notBlankRaws.append(i)
                notBlankRaws.append(endLine)
            else:
                token = lexer.nextToken()
                notBlankRaws.append(token.line)

        BlankLines = []
        for line in range(i.startLine, i.endLine):
            if not (line in notBlankRaws):
                BlankLines.append(line)

        i.numbderOfBlankLines = len(BlankLines)

    SumOfBlankLines = 0
    for i in interfaces:
        SumOfBlankLines = SumOfBlankLines + i.numbderOfBlankLines

    avgBlankLinesNumber = SumOfBlankLines/len(interfaces)

    print("avg number of blank lines of interfaces : " +
          str(avgBlankLinesNumber))


def avgInterfaceCodeLines(file_path, interfaces):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)

    for i in interfaces:
        token = lexer.nextToken()
        last_line = token.line
        while token.line < i.endLine:
            if token.line >= i.startLine and token.line < i.endLine:
                while token.line == last_line:
                    token = lexer.nextToken()
                last_line = token.line

                if token.type == lexer.COMMENT:
                    token = lexer.nextToken()
                    if not token.type == 108:
                        i.numberOfCodeLines = i.numberOfCodeLines +1
                else:
                    if not token.type == lexer.LINE_COMMENT:
                        i.numberOfCodeLines = i.numberOfCodeLines + 1

            token = lexer.nextToken()
        i.numberOfCodeLines = i.numberOfCodeLines - 1

    SumOfCodeLines = 0
    for method in interfaces:
        SumOfCodeLines = SumOfCodeLines + method.numberOfCodeLines
    SumOfCodeLines = SumOfCodeLines - 1
    avgMethodsCodeLines = SumOfCodeLines / len(interfaces)

    print("avg number of code lines of functions :" + str(avgMethodsCodeLines))


def line_avg_info_for_methods (path):
    for dirpath, dirnames, filenames in os.walk(
            path):
        for filename in [f for f in filenames if f.endswith(".java")]:
            print("for file :" + filename)
            file_path = os.path.join(dirpath, filename)
            print("\nfunctions information :")
            methods = avgMethodsLineNumbers(file_path)
            if(len(methods)!= 0):
                avgMethodCommentLines(file_path, methods)
                avgMethodCommentBlockLines(file_path, methods)
                avgMethodCodeLines(file_path, methods)
                avgMethodBlankLines(file_path, methods)

            print("\nclasses information :")
            classes = avgClassesLineNumbers(file_path)
            if (len(classes) != 0):
                avgClassCommentLines(file_path, classes)
                avgClassCommentBlockLines(file_path, classes)
                avgClassCodeLines(file_path, classes)
                avgClassBlankLines(file_path, classes)

            print("\ninterfaces information :")
            interfaces = avgInterfacesLineNumbers(file_path)
            if(len(interfaces) != 0):
                avgInterfacesCommentLines(file_path, interfaces)
                avgInterfacesCommentBlockLines(file_path, interfaces)
                avgInterfaceCodeLines(file_path, interfaces)
                avgInterfaceBlankLines (file_path, interfaces)

if __name__ == '__main__':
    line_avg_info_for_methods("D:/university/Term6/Courses/Compiler/last_from_git/OpenUnderstand-master/benchmark/metricsTest")


