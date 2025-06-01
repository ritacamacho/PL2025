import sys
import ply.yacc as yacc
from language.compiler_context import Context
from lexer import tokens
from language.ast_nodes import (
    Node,
    ProgramNode,
    ProgramHeadingNode,
    DeclarationsNode,
    BlockNode,
    StringNode,
    CompoundStatementNode,
    StatementsNode,
    CallStatementNode,
    ExpressionListNode,
    EmptyStatementNode,
    IdentifierNode,
    VariableDeclarationBlock,
    VariableDeclarationList,
    VariableDeclaration,
    IdentifierListNode,
    TypeIdentifierNode,
    VariableNode,
    IfStatementNode,
    ExpressionNode,
    AssigmentStatementNode,
    RelationalOperatorNode,
    ForStatementNode,
    TermNode,
    ConstantDefinitionBlock,
    ConstantDefinitionList,
    ConstantDefinition,
    ConstantNode,
    UnsignedIntegerNode,
    UnsignedRealNode,
    SignNode,
    ConstantChrNode,
    TypeDeclarationBlock,
    TypeDefinitionList,
    TypeDefinition,
    ScalarTypeNode,
    SubRangeTypeNode,
    StringTypeNode,
    ArrayTypeNode,
    TypeListNode,
    recordTypeNode,
    FieldListNode,
    FixedPartNode,
    RecordSectionList,
    RecordSectionNode,
    VariantPartNode,
    TagNode,
    VariantListNode,
    VariantNode,
    ConstListNode,
    SetTypeNode,
    ProcedureDeclarationNode,
    FormalParameterListNode,
    FormalParameterSectionListNode,
    FormalParameterSectionNode,
    ParameterGroupNode,
    FunctionDeclarationNode,
    IndexedVariableNode,
    SimpleExpressionNode,
    AdditionOperatorNode,
    MultiplicativeOperatorNode,
    WhileStatementNode,
    BooleanConstantNode,
    ParenthesizedExpressionNode,
    FormattedExpressionNode,
)

# Define precedence to resolve ambiguity in the grammar
precedence = (
    ("right", "ASSIGN"),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "NOT"),
    ("left", "EQUAL", "NOT_EQUAL", "LT", "LE", "GT", "GE", "IN"),
    ("left", "PLUS", "MINUS"),
    ("left", "STAR", "SLASH", "DIV", "MOD"),
)


# Grammar rules
def p_program(p):
    """program : programHeading block DOT"""
    program_node = ProgramNode(p[1], p[2])
    p[0] = program_node

    # Create context and print the AST
    context = Context()


def p_programHeading(p):
    """programHeading : PROGRAM identifier SEMI"""
    p[0] = ProgramHeadingNode(p[2])


def p_identifier(p):
    """identifier : IDENT"""
    p[0] = IdentifierNode(p[1])


def p_block(p):
    """block : declarations compoundStatement"""
    p[0] = BlockNode(p[1], p[2])


def p_declarations(p):
    """declarations : declaration declarations
    | empty"""
    if len(p) > 2:
        if isinstance(p[1], list):
            p[0] = DeclarationsNode(p[1] + p[2].children)
        else:
            p[0] = DeclarationsNode([p[1]] + p[2].children)
    else:
        p[0] = DeclarationsNode([])

def p_declaration(p):
    """declaration : constantDefinitionBlock
    | typeDeclarationBlock
    | variableDeclarationBlock
    | procedureAndFunctionDeclarationBlock"""
    p[0] = p[1]


def p_constantDefinitionBlock(p):
    """constantDefinitionBlock : CONST constantDefinitionList"""
    p[0] = ConstantDefinitionBlock(p[2])


def p_constantDefinitionList(p):
    """constantDefinitionList : constantDefinitionList constantDefinition SEMI
    | constantDefinition SEMI"""
    if len(p) > 3:
        p[1].children.append(p[2])
        p[0] = p[1]
    else:
        p[0] = ConstantDefinitionList([p[1]])


def p_constantDefinition(p):
    """constantDefinition : identifier EQUAL constant"""
    p[0] = ConstantDefinition(p[1], p[3])


def p_constant(p):
    """constant : unsignedNumber
    | sign unsignedNumber
    | identifier
    | sign identifier
    | string
    | constantChr"""

    if len(p) == 2:
        p[0] = ConstantNode(str(p[1].value))  # wrap in ConstantNode
    else:
        sign = p[1].value if hasattr(p[1], "value") else p[1]
        value = p[2].value if hasattr(p[2], "value") else p[2]
        p[0] = ConstantNode(sign + str(value))


def p_unsignedNumber(p):
    """unsignedNumber : unsignedInteger
    | unsignedReal"""
    p[0] = p[1]


def p_unsignedInteger(p):
    """unsignedInteger : NUM_INT"""
    p[0] = UnsignedIntegerNode(p[1])


def p_unsignedReal(p):
    """unsignedReal : NUM_REAL"""
    p[0] = UnsignedRealNode(p[1])


def p_sign(p):
    """sign : PLUS
    | MINUS"""
    p[0] = SignNode(p[1])


def p_string(p):
    """string : STRING_LITERAL"""
    p[0] = StringNode(p[1])


def p_constantChr(p):
    """constantChr : CHR LPAREN unsignedInteger RPAREN"""
    p[0] = ConstantChrNode(p[3])


def p_typeDeclarationBlock(p):
    """typeDeclarationBlock : TYPE typeDefinitionList"""
    p[0] = TypeDeclarationBlock(p[2])


def p_typeDefinitionList(p):
    """typeDefinitionList : typeDefinitionList typeDefinition SEMI
    | typeDefinition SEMI"""
    if len(p) > 3:
        p[1].children.append(p[2])
        p[0] = p[1]
    else:
        p[0] = TypeDefinitionList([p[1]])


def p_typeDefinition(p):
    """typeDefinition : identifier EQUAL type_"""
    p[0] = TypeDefinition(p[1], p[3])


def p_type_(p):
    """type_ : scalarType
    | subrangeType
    | typeIdentifier
    | stringType
    | arrayType"""
    p[0] = p[1]


def p_scalarType(p):
    """scalarType : LPAREN identifierList RPAREN"""
    p[0] = ScalarTypeNode(p[2])


def p_identifierList(p):
    """identifierList : identifierList COMMA identifier
    | identifier"""
    if len(p) > 2:
        p[1].children.append(p[3])
        p[0] = p[1]
    else:
        p[0] = IdentifierListNode([p[1]])


def p_subrangeType(p):
    """subrangeType : unsignedInteger DOTDOT unsignedInteger"""
    p[0] = SubRangeTypeNode(p[1], p[3])


def p_identifierType(p):
    """identifierType : IDENT"""
    p[0] = IdentifierNode(p[1])


def p_stringType(p):
    """stringType : STRING LBRACK unsignedInteger RBRACK"""
    p[0] = StringTypeNode(p[3])


def p_structuredType(p):
    """structuredType : arrayType
    | recordType
    | setType"""
    p[0] = p[1]


def p_arrayType(p):
    """arrayType : ARRAY LBRACK subrangeType RBRACK OF typeIdentifier"""
    p[0] = ArrayTypeNode(p[3], p[6])


def p_typeList(p):
    """typeList : typeList COMMA indexType
    | indexType"""
    if len(p) > 2:
        p[1].children.append(p[3])
        p[0] = p[1]
    else:
        p[0] = TypeListNode([p[1]])


def p_indexType(p):
    """indexType : simpleType"""
    p[0] = p[1]


def p_simpleType(p):
    """simpleType : identifierType"""
    p[0] = p[1]


def p_recordType(p):
    """recordType : RECORD fieldList END"""
    p[0] = recordTypeNode(p[2])


def p_fieldList(p):
    """fieldList : fixedPart
    | fixedPart SEMI variantPart
    | variantPart"""
    if len(p) > 2:
        p[0] = FieldListNode([p[1], p[3]])
    else:
        p[0] = FieldListNode([p[1]])


def p_fixedPart(p):
    """fixedPart : recordSectionList"""
    p[0] = FixedPartNode(p[1])


def p_recordSectionList(p):
    """recordSectionList : recordSectionList SEMI recordSection
    | recordSection"""
    if len(p) > 2:
        p[1].children.append(p[3])
        p[0] = p[1]
    else:
        p[0] = RecordSectionList([p[1]])


def p_recordSection(p):
    """recordSection : identifierList COLON type_"""
    p[0] = RecordSectionNode(p[1], p[3])


def p_variantPart(p):
    """variantPart : CASE tag OF variantList"""
    p[0] = VariantPartNode(p[3], p[2])


def p_tag(p):
    """tag : identifier COLON typeIdentifier
    | typeIdentifier"""
    if len(p) > 2:
        p[0] = TagNode(p[1], p[3])
    else:
        p[0] = TagNode(p[1], None)


def p_typeIdentifier(p):
    """typeIdentifier : identifier
    | INTEGER
    | REAL
    | BOOLEAN
    | CHAR
    | STRING"""
    if isinstance(p[1], IdentifierNode):  # If it's an identifier node
        p[0] = TypeIdentifierNode(p[1].value)
    else:  # If it's a keyword like INTEGER, REAL, etc.
        p[0] = TypeIdentifierNode(p[1])


def p_variantList(p):
    """variantList : variantList SEMI variant
    | variant"""
    if len(p) > 2:
        p[1].children.append(p[3])
        p[0] = p[1]
    else:
        p[0] = VariantListNode([p[1]])


def p_variant(p):
    """variant : constList COLON LPAREN fieldList RPAREN"""
    p[0] = VariantNode(p[1], p[4])


def p_constList(p):
    """constList : constList COMMA constant
    | constant"""
    if len(p) > 2:
        p[1].children.append(p[3])
        p[0] = p[1]
    else:
        p[0] = ConstListNode([p[1]])


def p_setType(p):
    """setType : SET OF baseType"""
    p[0] = SetTypeNode(p[4])


def p_baseType(p):
    """baseType : simpleType"""
    p[0] = p[1]


def p_variableDeclarationBlock(p):
    """variableDeclarationBlock : VAR variableDeclarationList SEMI"""
    p[0] = VariableDeclarationBlock(p[2])


def p_variableDeclarationList(p):
    """variableDeclarationList : variableDeclarationList SEMI variableDeclaration
    | variableDeclaration"""
    if len(p) > 2:
        p[1].declarations.append(p[3])
        p[0] = p[1]
    else:
        p[0] = VariableDeclarationList([p[1]])


def p_variableDeclaration(p):
    """variableDeclaration : identifierList COLON type_"""
    p[0] = VariableDeclaration(p[1], p[3])


def p_procedureAndFunctionDeclarationBlock(p):
    """procedureAndFunctionDeclarationBlock : procedureDeclaration SEMI
                                            | functionDeclaration SEMI"""
    p[0] = p[1]


def p_procedureDeclaration(p):
    """procedureDeclaration : PROCEDURE identifier SEMI block
                            | PROCEDURE identifier formalParameterList_opt SEMI block"""
    # Store procedure in context with its block

    procedure_name = p[2].value
    procedure_block = p[4]
    context = Context()
    context.add_procedure(procedure_name, procedure_block)
    p[0] = ProcedureDeclarationNode(p[2], None, p[4])


def p_formalParameterList_opt(p):
    """formalParameterList_opt : formalParameterList
                               | empty"""
    p[0] = p[1]


def p_formalParameterList(p):
    """formalParameterList : LPAREN formalParameterSectionList RPAREN"""
    p[0] = FormalParameterListNode(p[2])


def p_formalParameterSectionList(p):
    """formalParameterSectionList : formalParameterSectionList SEMI formalParameterSection
                                  | formalParameterSection"""
    if len(p) > 2:
        p[1].children.append(p[3])
        p[0] = p[1]
    else:
        p[0] = FormalParameterSectionListNode([p[1]])


def p_formalParameterSection(p):
    """formalParameterSection : parameterGroup
    | VAR parameterGroup
    | FUNCTION parameterGroup
    | PROCEDURE parameterGroup"""
    if len(p) > 2:
        p[0] = FormalParameterSectionNode(p[2], p[1])
    else:
        p[0] = FormalParameterSectionNode(p[1], None)


def p_parameterGroup(p):
    """parameterGroup : identifierList COLON typeIdentifier"""
    p[0] = ParameterGroupNode(p[1], p[3])


def p_functionDeclaration(p):
    """functionDeclaration : FUNCTION identifier formalParameterList_opt COLON resultType SEMI block
                           | FUNCTION identifier SEMI block"""
    p[0] = FunctionDeclarationNode(p[2], p[3], p[5], p[7])


def p_resultType(p):
    """resultType : typeIdentifier"""
    p[0] = p[1]


def p_compoundStatement(p):
    """compoundStatement : BEGIN statements END"""

    p[0] = CompoundStatementNode(p[2])



def p_statements(p):
    """statements : statementList"""
    p[0] = p[1]

def p_statementList(p):
    """statementList : statementList SEMI statement
                     | statement"""
    if len(p) == 4:
        if isinstance(p[1], StatementsNode):
            if p[3] is not None:
                p[1].statements.append(p[3])
            p[0] = p[1]
        else:
            p[0] = StatementsNode([p[1], p[3]])
    else:
        p[0] = StatementsNode([p[1]])

def p_statement(p):
    """statement : simpleStatement
                 | structuredStatement """

    p[0] = p[1]


def p_simpleStatement(p):
    """simpleStatement : callStatement 
                       | assignmentStatement
                       | emptyStatement_"""
    p[0] = p[1]


def p_assignmentStatement(p):
    """assignmentStatement : variable ASSIGN Init_Final"""
    p[0] = AssigmentStatementNode(p[1], p[3])


def p_variable(p):
    """variable : identifier
                | indexedVariable"""
    p[0] = VariableNode(p[1])


def p_indexedVariable(p):
    """indexedVariable : identifier LBRACK expression RBRACK"""
    p[0] = IndexedVariableNode(p[1], p[3])


def p_expression(p):
    """expression : simpleExpression
                  | simpleExpression relationalOperator simpleExpression
                 """
    if len(p) > 2:
        p[0] = ExpressionNode(p[1], p[3], p[2])
    else:
        p[0] = p[1]


def p_relationalOperator(p):
    """relationalOperator : EQUAL
    | NOT_EQUAL
    | LT
    | LE
    | GT
    | GE
    | IN"""
    p[0] = RelationalOperatorNode(p[1])


def p_simpleExpression(p):
    """simpleExpression : term
    | sign term
    | simpleExpression additiveOperator term"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = SimpleExpressionNode(p[1], p[2])
    else:
        p[0] = SimpleExpressionNode(p[1], p[2], p[3])


def p_additiveOperator(p):
    """additiveOperator : PLUS
    | MINUS
    | OR"""
    p[0] = AdditionOperatorNode(p[1])


def p_term(p):
    """term : factor
    | term multiplicativeOperator factor"""
    if len(p) > 2:
        p[0] = TermNode(p[1], p[3], p[2])
    else:
        p[0] = p[1]


def p_multiplicativeOperator(p):
    """multiplicativeOperator : STAR
    | SLASH
    | DIV
    | MOD
    | AND"""
    p[0] = MultiplicativeOperatorNode(p[1])


def p_factor(p):
    """factor : variable
        | unsignedConstant
        | LPAREN expression RPAREN"""
    if len(p) == 2:
        # Handle variable or unsigned constant
        p[0] = p[1]
    else:
        # Handle parenthesized expression
        p[0] = ParenthesizedExpressionNode(p[2])


def p_unsignedConstant(p):
    """unsignedConstant : unsignedNumber
    | string
    | NIL
    | TRUE
    | FALSE"""
    if p[1] == "true":
        p[0] = BooleanConstantNode(True)
    elif p[1] == "false":
        p[0] = BooleanConstantNode(False)
    else:
        p[0] = p[1]


def p_callStatement(p):
    """callStatement : identifier 
                     | identifier LPAREN expressionList RPAREN"""
    if len(p) == 2:
        # Simple procedure call without parameters
        p[0] = CallStatementNode(p[1], None)
    else:
        # Procedure call with parameters
        p[0] = CallStatementNode(p[1], p[3])


def p_expressionList(p):
    """expressionList : expressionList COMMA expression
    | expressionList COMMA formattedExpression
    | expression
    | formattedExpression"""
    if len(p) > 2:
        if isinstance(p[1], ExpressionListNode):
            p[1].expressions.append(p[3])
            p[0] = p[1]
        else:
            p[0] = ExpressionListNode([p[1], p[3]])
    else:
        p[0] = ExpressionListNode([p[1]])


def p_formattedExpression(p):
    """formattedExpression : variable COLON expression COLON expression
    | variable COLON expression"""

    if len(p) > 4:
        p[0] = FormattedExpressionNode(p[1], p[3], p[5])
    else:
        p[0] = FormattedExpressionNode(p[1], p[3], None)


def p_emptyStatement_(p):
    """emptyStatement_ :"""
    p[0] = EmptyStatementNode()


def p_structuredStatement(p):
    """structuredStatement : compoundStatement
    | conditionalStatement
    | loopStatement"""
    p[0] = p[1]


def p_loopStatement(p):
    """loopStatement : forStatement
    | whileStatement
    | repeatStatement"""
    p[0] = p[1]


def p_forStatement(p):
    """forStatement : FOR identifier ASSIGN Init_Final TO Init_Final DO statement
                    | FOR identifier ASSIGN Init_Final DOWNTO Init_Final DO statement"""
    direction = p[5].lower()
    p[0] = ForStatementNode(p[2], p[4], p[6], p[8], direction)


def p_Init_Final(p):
    """ Init_Final : callStatement
                   | expression """
                
    p[0] = p[1]


# Add while statement rule
def p_whileStatement(p):
    """whileStatement : WHILE expression DO statement"""
    p[0] = WhileStatementNode(p[2], p[4])


# Add repeat statement rule
def p_repeatStatement(p):
    """repeatStatement : REPEAT statements UNTIL expression"""
    p[0] = Node("repeatStatement", [p[2], p[4]])


def p_conditionalStatement(p):
    """conditionalStatement : ifStatement"""
    p[0] = p[1]


def p_ifStatement(p):
    """ifStatement : IF expression THEN statement
    | IF expression THEN statement ELSE statement"""
    if len(p) > 5:
        p[0] = IfStatementNode(p[2], p[4], p[6])
    else:
        p[0] = IfStatementNode(p[2], p[4], None)


def p_empty(p):
    """empty :"""
    p[0] = EmptyStatementNode()


def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}', line {p.lineno}")
    else:
        print("Syntax error at EOF")


# Build the parser
parser = yacc.yacc()


# Test function
def parse(data):
    result = parser.parse(data)

    return result


def visualize(filepath):
    try:
        with open(filepath, "r") as file:
            data = file.read()
            result = parse(data)
            print(result)
    except FileNotFoundError:
        print("File not found. Please provide a valid file path.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Parsing completed.")


def convert_to_machine_code(filepath):
    try:
        with open(filepath, "r") as file:
            data = file.read()
            result = parse(data)

            if result:
                # Generate machine code from the AST
                context = Context()
                machine_code = result.to_vm(context)

                print(machine_code)
            else:
                print("Parsing failed. No machine code generated.")
    except FileNotFoundError:
        print("File not found. Please provide a valid file path.")
    finally:
        print("Parsing completed.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py [flag] <file_path>")
        print("Flag: -v for visualization, -c for conversion to machine code")
    else:
        if sys.argv[1] == "-v":
            visualize(sys.argv[2])
        elif sys.argv[1] == "-c":
            convert_to_machine_code(sys.argv[2])
        else:
            print("Invalid flag. Use -v for visualization or -c for conversion.")
