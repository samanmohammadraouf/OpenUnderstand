from antlr4 import *
from openunderstand.gen.javaLabeled.JavaParserLabeled import JavaParserLabeled
from openunderstand.gen.javaLabeled.JavaParserLabeledListener import JavaParserLabeledListener
from openunderstand.gen.javaLabeled.JavaLexer import JavaLexer
import argparse
import os

class Method:
    def __init__(self,name,numberOfLines,numberOfBlankLines,numberOfCommentLines,numberOfCodeLines):
        self.methodName = name
        self.numberOfLines = numberOfLines
        self.numbderOfBlankLines = numberOfBlankLines
        self.numberOfCommentLines = numberOfCommentLines
        self.numberOfCodeLines = numberOfCodeLines

class FunctionsListener(JavaParserLabeledListener):
    def __init__(self):
        self.methods = []

    def enterMethodDeclaration(self, ctx:JavaParserLabeled.MethodDeclarationContext):
        [FirstLine, col] = str(ctx.start).split(",")[3].split(":")
        col = col[:-1]
        FirstLineNum = int(FirstLine)
        newMethod = Method(ctx.IDENTIFIER().getText(),FirstLineNum,0,0,0)
        self.methods.append(newMethod)

    def exitMethodBody(self, ctx:JavaParserLabeled.MethodBodyContext):
        for m in self.methods:
            if m.methodName == ctx.parentCtx.IDENTIFIER().getText():
                [LastLine, col] = str(ctx.stop).split(",")[3].split(":")
                col = col[:-1]
                LastLineNum = int(LastLine)
                m.numberOfLines = LastLineNum - m.numberOfLines

def avgMethodsLineNumbers(file_path):
    file_stream = FileStream(file_path)
    lexer = JavaLexer(file_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParserLabeled(token_stream)
    parseTree = parser.compilationUnit()

    listener = FunctionsListener()
    walker = ParseTreeWalker()
    walker.walk(listener,parseTree)

    methods = listener.methods

    SumOfMethodsLines = 0
    for method in methods:
        SumOfMethodsLines = SumOfMethodsLines + method.numberOfLines
    avgMethodsLines = SumOfMethodsLines / len(methods)

    print("avg number of lines of functions :" + str(avgMethodsLines))

if __name__ == '__main__':
   for dirpath, dirnames, filenames in os.walk("D:/university/Term6/Courses/Compiler/Project_phase_2/OpenUnderstand-master/benchmark/metricsTest"):
        for filename in [f for f in filenames if f.endswith(".java")]:
                print("for file :"+ filename)
                file_path = os.path.join(dirpath,filename)
                avgMethodsLineNumbers(file_path)
                #avgMethodsCommentLines(file_path)
                #avgMethodsBlankLines(file_path)
                #avgMethodsCodeLines(file_path)